import io
import base64
import numpy as np
import cv2
from PIL import Image


def _cluster_pairs(pairs, min_cluster_size=3):
    """
    Group keypoint index pairs into spatially coherent clusters using
    Union-Find, then filter small clusters.
    """
    parent = {}

    def find(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], parent[x])
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for a, b in pairs:
        union(a, b)

    groups = {}
    for a, b in pairs:
        root = find(a)
        groups.setdefault(root, set()).add(a)
        groups[root].add(b)

    return [g for g in groups.values() if len(g) >= min_cluster_size]


def analyze_copy_move(image_path):
    """
    Copy-Move Detection — detect regions copied from elsewhere in the image.

    Uses ORB feature extraction + brute-force matching to find keypoints
    that match each other across spatially distant regions. Clustered
    matching keypoints indicate copy-move forgery.

    Returns:
        dict with keys:
            copymove_image_base64 – base64-encoded JPEG with detected regions highlighted
            total_matches         – number of keypoint matches after filtering
            cluster_count         – number of detected forgery clusters
            cluster_sizes         – list of sizes per cluster
            forgery_pct           – estimated % of image covered by forged regions
            analysis              – human-readable conclusion
    """
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Gagal membaca gambar")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # ORB detector (free, no patent issues unlike SIFT)
    orb = cv2.ORB_create(nfeatures=5000, scaleFactor=1.2, nlevels=8)
    keypoints, descriptors = orb.detectAndCompute(gray, None)

    if descriptors is None or len(keypoints) < 10:
        return _empty_result(img, "Gambar terlalu sedikit fitur untuk dianalisis.")

    # BFMatcher with Hamming distance (appropriate for ORB binary descriptors)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

    # KNN match (k=2) for Lowe's ratio test
    matches = bf.knnMatch(descriptors, descriptors, k=2)

    # Lowe's ratio test + spatial distance filter
    good_matches = []
    min_spatial_dist = max(w, h) * 0.05  # at least 5% of image dimension apart

    for m_list in matches:
        if len(m_list) < 2:
            continue
        m, n = m_list
        # Ratio test
        if m.distance < 0.75 * n.distance:
            # Ensure the two keypoints are spatially distant
            kp_a = keypoints[m.queryIdx]
            kp_b = keypoints[m.trainIdx]
            dx = kp_a.pt[0] - kp_b.pt[0]
            dy = kp_a.pt[1] - kp_b.pt[1]
            dist = (dx * dx + dy * dy) ** 0.5
            if dist > min_spatial_dist:
                good_matches.append(m)

    if len(good_matches) < min_cluster_size_for_result(good_matches, 3):
        return _draw_result(img, [], [], h, w)

    # Build pairs of matching keypoint indices
    pairs = [(m.queryIdx, m.trainIdx) for m in good_matches]

    # Cluster
    clusters = _cluster_pairs(pairs, min_cluster_size=3)

    # Calculate forgery coverage
    forged_mask = np.zeros((h, w), dtype=np.uint8)
    for cluster in clusters:
        pts = []
        for idx in cluster:
            kp = keypoints[idx]
            pts.append([int(kp.pt[0]), int(kp.pt[1])])
        if len(pts) >= 3:
            pts = np.array(pts, dtype=np.int32)
            hull = cv2.convexHull(pts)
            cv2.fillConvexPoly(forged_mask, hull, 255)

    forgery_pct = float(np.mean(forged_mask > 0) * 100)

    # Draw result
    result_img = _draw_result(img, clusters, keypoints, h, w)

    # Encode
    result_pil = Image.fromarray(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
    buf = io.BytesIO()
    result_pil.save(buf, 'JPEG', quality=90)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')

    cluster_sizes = [len(c) for c in clusters]

    # Analysis
    if len(clusters) == 0:
        conclusion = (
            "Tidak terdeteksi **copy-move forgery**. "
            "Tidak ditemukan region yang dicopy dari bagian lain gambar."
        )
    elif forgery_pct < 2:
        conclusion = (
            f"Terdeteksi **{len(clusters)} cluster copy-move** dengan cakupan {forgery_pct:.1f}%. "
            "Indikasi manipulasi ringan pada area kecil."
        )
    elif forgery_pct < 10:
        conclusion = (
            f"Terdeteksi **{len(clusters)} cluster copy-move** dengan cakupan {forgery_pct:.1f}%. "
            "Beberapa region menunjukkan tanda salin-tempel dari bagian lain gambar."
        )
    else:
        conclusion = (
            f"Terdeteksi **{len(clusters)} cluster copy-move** dengan cakupan {forgery_pct:.1f}%. "
            "Manipulasi signifikan terdeteksi — banyak area merupakan hasil copy-paste."
        )

    return {
        'copymove_image_base64': b64,
        'total_matches': len(good_matches),
        'cluster_count': len(clusters),
        'cluster_sizes': cluster_sizes,
        'forgery_pct': round(forgery_pct, 2),
        'analysis': conclusion,
    }


def min_cluster_size_for_result(matches, default):
    return default


def _empty_result(img, message):
    result_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    buf = io.BytesIO()
    result_pil.save(buf, 'JPEG', quality=90)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    return {
        'copymove_image_base64': b64,
        'total_matches': 0,
        'cluster_count': 0,
        'cluster_sizes': [],
        'forgery_pct': 0.0,
        'analysis': message,
    }


def _draw_result(img, clusters, keypoints, h, w):
    """Draw detected regions on a copy of the image."""
    result = img.copy()
    colors = [
        (0, 0, 255),    # red
        (0, 165, 255),  # orange
        (0, 255, 255),  # yellow
        (0, 255, 0),    # green
        (255, 0, 0),    # blue
        (255, 0, 255),  # magenta
        (128, 0, 255),  # purple
    ]

    for ci, cluster in enumerate(clusters):
        color = colors[ci % len(colors)]
        pts = []
        for idx in cluster:
            kp = keypoints[idx]
            pts.append([int(kp.pt[0]), int(kp.pt[1])])

        if len(pts) >= 3:
            pts_arr = np.array(pts, dtype=np.int32)
            hull = cv2.convexHull(pts_arr)
            # Semi-transparent overlay
            overlay = result.copy()
            cv2.fillConvexPoly(overlay, hull, color)
            cv2.addWeighted(overlay, 0.3, result, 0.7, 0, result)
            # Border
            cv2.polylines(result, [hull], True, color, 2)

        # Draw keypoints
        for pt in pts:
            cv2.circle(result, pt, 4, color, -1)

    return result