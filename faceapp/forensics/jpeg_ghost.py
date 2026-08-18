import io
import base64
import numpy as np
import cv2
from PIL import Image


def analyze_jpeg_ghost(image_path):
    """
    JPEG Ghost Detection — detect double JPEG compression artefacts.

    When a JPEG image is saved, edited, and re-saved, it acquires two
    different quantisation grids. By re-compressing the image at every
    possible JPEG quality level and measuring the error at each, we can
    detect the "ghost" quality — a secondary minimum in the error curve
    that indicates double compression.

    We sample multiple quality levels (1-99) and build a quality-error
    curve. A single compression produces one clear minimum; double
    compression produces two minima.

    Returns:
        dict with keys:
            ghost_image_base64  – base64-encoded JPEG showing quality map
            original_quality    – estimated original JPEG quality
            ghost_quality       – detected second compression quality (or None)
            quality_scores      – list of [quality, error] pairs for chart
            double_compress_pct – estimated % of double-compressed blocks
            analysis            – human-readable conclusion
    """
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Gagal membaca gambar")

    h, w = img.shape[:2]

    # Sample quality levels
    qualities = list(range(1, 100, 2))
    global_errors = []

    for q in qualities:
        # Encode to JPEG at quality q, decode back
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), q]
        _, buf = cv2.imencode('.jpg', img, encode_param)
        reencoded = cv2.imdecode(buf, cv2.IMREAD_COLOR)

        # Mean absolute error
        diff = np.abs(img.astype(np.float64) - reencoded.astype(np.float64))
        mae = float(np.mean(diff))
        global_errors.append(mae)

    global_errors = np.array(global_errors)

    # Find the minimum error quality (best match = original quality)
    min_idx = int(np.argmin(global_errors))
    original_quality = qualities[min_idx]

    # Ghost detection: look for a secondary local minimum
    ghost_quality = None
    ghost_image_b64 = None

    # Smooth the error curve to find local minima
    if len(global_errors) > 10:
        kernel = np.ones(5) / 5
        smoothed = np.convolve(global_errors, kernel, mode='same')

        # Find local minima (excluding the global minimum region)
        local_minima = []
        for i in range(2, len(smoothed) - 2):
            if smoothed[i] < smoothed[i-1] and smoothed[i] < smoothed[i+1]:
                if smoothed[i] < smoothed[i-2] and smoothed[i] < smoothed[i+2]:
                    local_minima.append((i, smoothed[i]))

        # Filter: ghost quality must be at least 10 away from original
        ghost_candidates = [
            (i, err) for i, err in local_minima
            if abs(qualities[i] - original_quality) >= 10
        ]

        if ghost_candidates:
            # Pick the one with the lowest error among candidates
            ghost_idx, ghost_err = min(ghost_candidates, key=lambda x: x[1])
            ghost_quality = qualities[ghost_idx]

    # Block-wise double compression analysis
    block_size = 64
    blocks_y = h // block_size
    blocks_x = w // block_size
    block_ghost_pct = []

    for by in range(blocks_y):
        for bx in range(blocks_x):
            patch = img[by * block_size:(by + 1) * block_size,
                       bx * block_size:(bx + 1) * block_size]

            # Re-compress at original quality
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), original_quality]
            _, buf = cv2.imencode('.jpg', patch, encode_param)
            reencoded = cv2.imdecode(buf, cv2.IMREAD_COLOR)

            diff = np.abs(patch.astype(np.float64) - reencoded.astype(np.float64))
            block_mae = float(np.mean(diff))

            # If ghost exists, check if this block's error at ghost quality is also low
            if ghost_quality is not None:
                encode_param2 = [int(cv2.IMWRITE_JPEG_QUALITY), ghost_quality]
                _, buf2 = cv2.imencode('.jpg', patch, encode_param2)
                reencoded2 = cv2.imdecode(buf2, cv2.IMREAD_COLOR)
                diff2 = np.abs(patch.astype(np.float64) + 0 - reencoded2.astype(np.float64))
                ghost_mae = float(np.mean(diff2))

                # Double compressed if both errors are relatively low
                threshold = 30.0
                is_double = block_mae < threshold and ghost_mae < threshold
                block_ghost_pct.append(1.0 if is_double else 0.0)
            else:
                block_ghost_pct.append(0.0)

    double_compress_pct = float(np.mean(block_ghost_pct) * 100) if block_ghost_pct else 0.0

    # Build ghost heatmap
    ghost_map = np.zeros((blocks_y, blocks_x), dtype=np.float64)
    for i, pct in enumerate(block_ghost_pct):
        by = i // blocks_x
        bx = i % blocks_x
        ghost_map[by, bx] = pct

    ghost_map_resized = cv2.resize(ghost_map, (w, h), interpolation=cv2.INTER_NEAREST)
    ghost_norm = (ghost_map_resized * 255).astype(np.uint8)

    heatmap_color = cv2.applyColorMap(ghost_norm, cv2.COLORMAP_COOL)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

    # Blend
    original_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    blended = cv2.addWeighted(original_rgb, 0.5, heatmap_color, 0.5, 0)

    result_img = Image.fromarray(blended)
    buf = io.BytesIO()
    result_img.save(buf, 'JPEG', quality=90)
    buf.seek(0)
    ghost_image_b64 = base64.b64encode(buf.read()).decode('utf-8')

    # Quality scores for potential chart display (subsample)
    quality_scores = [[int(qualities[i]), round(float(global_errors[i]), 2)]
                      for i in range(0, len(qualities), 2)]

    # Analysis text
    if ghost_quality is None:
        conclusion = (
            f"Tidak terdeteksi **double compression**. "
            f"Kualitas JPEG diperkirakan ~{original_quality}. "
            "Gambar kemungkinan hanya memiliki satu tingkat kompresi."
        )
    elif double_compress_pct < 5:
        conclusion = (
            f"Terdeteksi **indikasi ringan double compression** "
            f"(kualitas asli ~{original_quality}, kompresi ulang ~{ghost_quality}). "
            f"Hanya {double_compress_pct:.1f}% blok yang terpengaruh."
        )
    elif double_compress_pct < 20:
        conclusion = (
            f"Terdeteksi **double compression sedang** "
            f"(kualitas asli ~{original_quality}, kompresi ulang ~{ghost_quality}). "
            f"{double_compress_pct:.1f}% blok menunjukkan artefak ganda, "
            "mengindikasikan kemungkinan editing dan penyimpanan ulang."
        )
    else:
        conclusion = (
            f"Terdeteksi **double compression kuat** "
            f"(kualitas asli ~{original_quality}, kompresi ulang ~{ghost_quality}). "
            f"{double_compress_pct:.1f}% blok terpengaruh. "
            "Gambar telah mengalami kompresi berulang, "
            "kemungkinan besar merupakan hasil edit/manipulasi."
        )

    return {
        'ghost_image_base64': ghost_image_b64,
        'original_quality': original_quality,
        'ghost_quality': ghost_quality,
        'quality_scores': quality_scores,
        'double_compress_pct': round(double_compress_pct, 2),
        'analysis': conclusion,
    }