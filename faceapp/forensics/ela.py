import io
import base64
import numpy as np
from PIL import Image


def analyze_ela(image_path, quality=95, scale=10):
    """
    Error Level Analysis (ELA).

    Re-saves the image at a fixed JPEG quality, then computes the
    per-pixel difference scaled for visual inspection.

    Returns:
        dict with keys:
            ela_image_base64  – base64-encoded JPEG of the ELA heatmap
            mean_error        – average absolute error
            max_error         – maximum absolute error
            suspicious_pct    – percentage of pixels above threshold
            analysis          – human-readable conclusion
    """
    original = Image.open(image_path).convert('RGB')

    # Re-save at fixed quality
    buffer = io.BytesIO()
    original.save(buffer, 'JPEG', quality=quality)
    buffer.seek(0)
    resaved = Image.open(buffer).convert('RGB')

    orig_arr = np.array(original, dtype=np.float64)
    resaved_arr = np.array(resaved, dtype=np.float64)

    # Per-pixel absolute difference
    diff = np.abs(orig_arr - resaved_arr)

    # Grayscale error magnitude per pixel
    error_mag = np.mean(diff, axis=2)

    # Statistics
    mean_error = float(np.mean(error_mag))
    max_error = float(np.max(error_mag))

    # Suspicious pixels: error > threshold (empirically ~25 works well)
    threshold = 25.0
    suspicious_mask = error_mag > threshold
    suspicious_pct = float(np.mean(suspicious_mask) * 100)

    # Build heatmap: scale differences and clip to 0-255
    heatmap_arr = np.clip(error_mag * scale, 0, 255).astype(np.uint8)

    # Apply colour map for better visualisation
    import cv2
    heatmap_color = cv2.applyColorMap(heatmap_arr, cv2.COLORMAP_JET)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

    # Blend with original for context (50/50)
    original_arr = orig_arr.astype(np.uint8)
    blended = cv2.addWeighted(original_arr, 0.5, heatmap_color, 0.5, 0)

    # Encode to base64 JPEG
    result_img = Image.fromarray(blended)
    out_buffer = io.BytesIO()
    result_img.save(out_buffer, 'JPEG', quality=90)
    out_buffer.seek(0)
    ela_b64 = base64.b64encode(out_buffer.read()).decode('utf-8')

    # Generate analysis text
    if suspicious_pct < 1:
        conclusion = (
            "Gambar kemungkinan **asli/tidak dimanipulasi**. "
            "Tingkat error seragam dan sangat rendah."
        )
    elif suspicious_pct < 5:
        conclusion = (
            "Gambar menunjukkan **indikasi manipulasi ringan**. "
            "Terdapat area dengan error level berbeda yang perlu diperiksa lebih lanjut."
        )
    elif suspicious_pct < 20:
        conclusion = (
            "Gambar menunjukkan **indikasi manipulasi sedang**. "
            "Beberapa area memiliki error level signifikan berbeda dari area lain."
        )
    else:
        conclusion = (
            "Gambar menunjukkan **indikasi manipulasi kuat**. "
            "Banyak area dengan error level sangat berbeda, "
            "kemungkinan besar merupakan hasil edit/collage."
        )

    return {
        'ela_image_base64': ela_b64,
        'mean_error': round(mean_error, 4),
        'max_error': round(max_error, 2),
        'suspicious_pct': round(suspicious_pct, 2),
        'analysis': conclusion,
    }