import io
import base64
import numpy as np
import cv2
from PIL import Image


def analyze_noise(image_path):
    """
    Noise Analysis — detect inconsistent noise patterns across an image.

    Different sources or edited regions have different noise signatures.
    We extract the noise residual via a high-pass filter, then measure
    noise level in overlapping blocks to find inconsistencies.

    Returns:
        dict with keys:
            noise_map_base64  – base64-encoded JPEG heatmap of noise levels
            mean_noise        – average noise magnitude
            max_noise         – peak noise magnitude
            inconsistency_pct – % of blocks that deviate significantly from the mean
            analysis          – human-readable conclusion
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Gagal membaca gambar")

    img_f = img.astype(np.float64)

    # High-pass filter: subtract a blurred version from the original
    blurred = cv2.GaussianBlur(img_f, (21, 21), 0)
    residual = img_f - blurred

    # Noise magnitude per pixel (absolute)
    noise_mag = np.abs(residual)

    # --- Block-wise analysis ---
    h, w = noise_mag.shape
    block_size = 32
    blocks_y = h // block_size
    blocks_x = w // block_size
    block_means = []

    for by in range(blocks_y):
        for bx in range(blocks_x):
            patch = noise_mag[by * block_size:(by + 1) * block_size,
                              bx * block_size:(bx + 1) * block_size]
            block_means.append(float(np.mean(patch)))

    block_means = np.array(block_means)
    global_mean = float(np.mean(block_means))
    global_std = float(np.std(block_means))

    mean_noise = global_mean
    max_noise = float(np.max(noise_mag))

    # Inconsistency: blocks whose mean noise deviates > 2 std from global mean
    threshold = global_mean + 2 * global_std
    low_threshold = max(global_mean - 2 * global_std, 0)
    suspicious = np.sum((block_means > threshold) | (block_means < low_threshold))
    inconsistency_pct = float(suspicious / len(block_means) * 100) if len(block_means) > 0 else 0.0

    # --- Build noise map heatmap ---
    # Expand block means back to full image size
    noise_map = np.zeros((blocks_y, blocks_x), dtype=np.float64)
    for i, bm in enumerate(block_means):
        by = i // blocks_x
        bx = i % blocks_x
        noise_map[by, bx] = bm

    noise_map_resized = cv2.resize(noise_map, (w, h), interpolation=cv2.INTER_NEAREST)
    noise_map_norm = np.clip(noise_map_resized / max(global_mean * 2, 1) * 255, 0, 255).astype(np.uint8)

    # Apply colormap
    heatmap_color = cv2.applyColorMap(noise_map_norm, cv2.COLORMAP_VIRIDIS)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

    # Blend with original
    original = cv2.imread(image_path)
    original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
    blended = cv2.addWeighted(original_rgb, 0.4, heatmap_color, 0.6, 0)

    # Encode
    result_img = Image.fromarray(blended)
    buf = io.BytesIO()
    result_img.save(buf, 'JPEG', quality=90)
    buf.seek(0)
    noise_b64 = base64.b64encode(buf.read()).decode('utf-8')

    # Analysis text
    if inconsistency_pct < 2:
        conclusion = (
            "Pola noise **relatif seragam** di seluruh gambar. "
            "Tidak terdeteksi indikasi manipulasi berbasis noise."
        )
    elif inconsistency_pct < 8:
        conclusion = (
            "Terdapat **ketidakseragaman noise ringan** pada beberapa area. "
            "Perlu pemeriksaan lebih lanjut untuk memastikan apakah akibat edit atau kompresi."
        )
    elif inconsistency_pct < 20:
        conclusion = (
            "Terdapat **ketidakseragaman noise sedang** yang mengindikasikan "
            "kemungkinan gabungan dari sumber gambar berbeda atau editing parsial."
        )
    else:
        conclusion = (
            "Terdapat **ketidakseragaman noise tinggi**. "
            "Gambar kemungkinan besar merupakan hasil manipulasi/collage "
            "dengan sumber berbeda yang digabungkan."
        )

    return {
        'noise_map_base64': noise_b64,
        'mean_noise': round(mean_noise, 4),
        'max_noise': round(max_noise, 2),
        'inconsistency_pct': round(inconsistency_pct, 2),
        'analysis': conclusion,
    }