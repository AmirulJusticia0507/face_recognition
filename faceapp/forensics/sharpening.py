import io
import base64
import numpy as np
import cv2
from PIL import Image


def analyze_sharpening(image_path):
    """
    Sharpening Detection — detect localised sharpening or unsharp masking.

    When an image region is sharpened, the gradient magnitudes in that area
    become anomalously high compared to the rest. We compute the Laplacian
    gradient, partition into blocks, and flag outliers.

    Returns:
        dict with keys:
            sharpening_map_base64 – base64-encoded JPEG heatmap
            mean_sharpness        – average gradient magnitude
            max_sharpness         – peak gradient magnitude
            suspicious_pct        – % of blocks with abnormally high sharpness
            analysis              – human-readable conclusion
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Gagal membaca gambar")

    # Laplacian for edge / gradient magnitude
    laplacian = cv2.Laplacian(img, cv2.CV_64F)
    sharpness = np.abs(laplacian)

    mean_sharpness = float(np.mean(sharpness))
    max_sharpness = float(np.max(sharpness))

    # Block-wise analysis
    h, w = sharpness.shape
    block_size = 32
    blocks_y = h // block_size
    blocks_x = w // block_size
    block_means = []

    for by in range(blocks_y):
        for bx in range(blocks_x):
            patch = sharpness[by * block_size:(by + 1) * block_size,
                             bx * block_size:(bx + 1) * block_size]
            block_means.append(float(np.mean(patch)))

    block_means = np.array(block_means)
    global_mean = float(np.mean(block_means))
    global_std = float(np.std(block_means))

    # Suspicious: blocks with sharpness >> mean (likely sharpened)
    threshold = global_mean + 2.5 * global_std
    suspicious = np.sum(block_means > threshold)
    suspicious_pct = float(suspicious / len(block_means) * 100) if len(block_means) > 0 else 0.0

    # Build sharpening map
    smap = np.zeros((blocks_y, blocks_x), dtype=np.float64)
    for i, bm in enumerate(block_means):
        by = i // blocks_x
        bx = i % blocks_x
        smap[by, bx] = bm

    smap_resized = cv2.resize(smap, (w, h), interpolation=cv2.INTER_NEAREST)
    smap_norm = np.clip(smap_resized / max(global_mean * 3, 1) * 255, 0, 255).astype(np.uint8)

    # Colormap
    heatmap_color = cv2.applyColorMap(smap_norm, cv2.COLORMAP_INFERNO)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

    # Blend
    original = cv2.imread(image_path)
    original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
    blended = cv2.addWeighted(original_rgb, 0.4, heatmap_color, 0.6, 0)

    result_img = Image.fromarray(blended)
    buf = io.BytesIO()
    result_img.save(buf, 'JPEG', quality=90)
    buf.seek(0)
    sharpen_b64 = base64.b64encode(buf.read()).decode('utf-8')

    # Analysis text
    if suspicious_pct < 2:
        conclusion = (
            "Tingkat ketajaman **seragam** di seluruh gambar. "
            "Tidak terdeteksi tanda sharpening atau unsharp masking."
        )
    elif suspicious_pct < 8:
        conclusion = (
            "Beberapa area menunjukkan **ketajaman lebih tinggi** dari sekitarnya. "
            "Kemungkinan telah dilakukan sharpening parsial pada area tertentu."
        )
    elif suspicious_pct < 20:
        conclusion = (
            "Terdeteksi **sharpening signifikan** pada beberapa area. "
            "Ini mengindikasikan editing lokal atau post-processing yang tidak merata."
        )
    else:
        conclusion = (
            "Gambar menunjukkan **sharpening merata/kuat** di banyak area. "
            "Kemungkinan besar gambar telah melalui post-processing intensif "
            "atau merupakan komposisi dari beberapa sumber berbeda."
        )

    return {
        'sharpening_map_base64': sharpen_b64,
        'mean_sharpness': round(mean_sharpness, 4),
        'max_sharpness': round(max_sharpness, 2),
        'suspicious_pct': round(suspicious_pct, 2),
        'analysis': conclusion,
    }