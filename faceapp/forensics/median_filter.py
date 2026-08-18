import io
import base64
import numpy as np
import cv2
from PIL import Image


def analyze_median_filter(image_path):
    """
    Median Filter Detection — detect traces of median filtering.

    Median filters replace each pixel with the median of its neighbours,
    which smooths noise but also creates characteristic "staircase" artefacts
    in gradient maps. Comparing the ratio of mean to standard deviation of
    gradients in small blocks reveals inconsistent median-filter application.

    We apply a median filter to the image, then compute the per-pixel
    difference (original vs median-filtered). Regions that were already
    median-filtered show significantly less change than untouched regions.

    Returns:
        dict with keys:
            median_map_base64  – heatmap of median filter residue
            mean_residue       – average residue magnitude
            max_residue        – peak residue
            inconsistency_pct  – % of blocks with inconsistent filtering
            analysis           – human-readable conclusion
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Gagal membaca gambar")

    img_f = img.astype(np.float64)

    # Apply a 3x3 median filter
    median_filtered = cv2.medianBlur(img, 3).astype(np.float64)

    # Residue: how much each pixel changed
    residue = np.abs(img_f - median_filtered)

    mean_residue = float(np.mean(residue))
    max_residue = float(np.max(residue))

    # Block-wise analysis
    h, w = residue.shape
    block_size = 32
    blocks_y = h // block_size
    blocks_x = w // block_size
    block_means = []

    for by in range(blocks_y):
        for bx in range(blocks_x):
            patch = residue[by * block_size:(by + 1) * block_size,
                            bx * block_size:(bx + 1) * block_size]
            block_means.append(float(np.mean(patch)))

    block_means = np.array(block_means)
    global_mean = float(np.mean(block_means))
    global_std = float(np.std(block_means))

    # Inconsistency: blocks with very low residue (already filtered)
    # or very high residue (never filtered / different source)
    low_thresh = max(global_mean - 2 * global_std, 0)
    high_thresh = global_mean + 2 * global_std
    inconsistent = np.sum((block_means < low_thresh) | (block_means > high_thresh))
    inconsistency_pct = float(inconsistent / len(block_means) * 100) if len(block_means) > 0 else 0.0

    # Build map
    fmap = np.zeros((blocks_y, blocks_x), dtype=np.float64)
    for i, bm in enumerate(block_means):
        by = i // blocks_x
        bx = i % blocks_x
        fmap[by, bx] = bm

    fmap_resized = cv2.resize(fmap, (w, h), interpolation=cv2.INTER_NEAREST)
    fmap_norm = np.clip(fmap_resized / max(global_mean * 3, 1) * 255, 0, 255).astype(np.uint8)

    # Colormap
    heatmap_color = cv2.applyColorMap(fmap_norm, cv2.COLORMAP_MAGMA)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

    # Blend
    original = cv2.imread(image_path)
    original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
    blended = cv2.addWeighted(original_rgb, 0.4, heatmap_color, 0.6, 0)

    result_img = Image.fromarray(blended)
    buf = io.BytesIO()
    result_img.save(buf, 'JPEG', quality=90)
    buf.seek(0)
    median_b64 = base64.b64encode(buf.read()).decode('utf-8')

    # Analysis text
    if inconsistency_pct < 3:
        conclusion = (
            "Pola median filter **seragam** di seluruh gambar. "
            "Tidak terdeteksi manipulasi berbasis median filter."
        )
    elif inconsistency_pct < 10:
        conclusion = (
            "Terdeteksi **ketidakseragaman median filter ringan**. "
            "Beberapa area mungkin telah melalui proses filter yang berbeda."
        )
    elif inconsistency_pct < 25:
        conclusion = (
            "Terdeteksi **median filter tidak merata** yang signifikan. "
            "Beberapa bagian gambar telah di-smooth/denoise lebih agresif, "
            "mengindikasikan kemungkinan editing parsial."
        )
    else:
        conclusion = (
            "Gambar menunjukkan **perbedaan median filter sangat tinggi**. "
            "Kemungkinan merupakan gabungan dari sumber berbeda, "
            "di mana setiap sumber memiliki tingkat denoise berbeda."
        )

    return {
        'median_map_base64': median_b64,
        'mean_residue': round(mean_residue, 4),
        'max_residue': round(max_residue, 2),
        'inconsistency_pct': round(inconsistency_pct, 2),
        'analysis': conclusion,
    }