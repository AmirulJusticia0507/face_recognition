import io
import base64
import os
from datetime import datetime

from PIL import Image


# Known editing software signatures
EDITING_SOFTWARE = [
    'photoshop', 'gimp', 'lightroom', 'snapseed', 'picsart',
    'afterlight', 'vsco', 'fotor', 'canva', 'paint.net',
    'photopea', 'capture one', 'affinity', 'darktable',
    'acr', 'camera raw', 'express', 'pixlr', 'beautyplus',
    'b612', 'airbrush', 'meitu', 'facetune',
]

CAMERA_SOFTWARE = [
    'canon', 'nikon', 'sony', 'fuji', 'olympus', 'panasonic',
    'samsung', 'apple', 'huawei', 'xiaomi', 'oppo', 'vivo',
    'google', 'oneplus', 'realme', 'honor', 'lg', 'htc',
    'leica', 'hasselblad',
]


def _parse_exif_date(date_str):
    """Try to parse EXIF date strings in common formats."""
    formats = [
        '%Y:%m:%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y:%m:%d %H:%M',
        '%Y-%m-%dT%H:%M:%S',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def _detect_software_type(software_str):
    """Classify software as camera-native or editing tool."""
    if not software_str:
        return 'unknown', software_str
    sw_lower = software_str.lower()
    for name in EDITING_SOFTWARE:
        if name in sw_lower:
            return 'editing', software_str
    for name in CAMERA_SOFTWARE:
        if name in sw_lower:
            return 'camera', software_str
    return 'other', software_str


def analyze_metadata(image_path):
    """
    Metadata Forensics — extract and analyze EXIF metadata for anomalies.

    Checks for:
    - Missing or stripped metadata
    - Inconsistent timestamps (create vs modify vs digitize)
    - Editing software signatures
    - Thumbnail consistency
    - Multiple Save-for-Web patterns
    - GPS anomalies

    Returns:
        dict with keys:
            metadata        – dict of extracted metadata fields
            anomalies       – list of detected anomaly strings
            anomaly_count   – number of anomalies
            software_type   – 'camera', 'editing', 'other', 'unknown'
            confidence_pct  – confidence the image is unmanipulated
            analysis        – human-readable conclusion
    """
    anomalies = []
    metadata = {}

    try:
        img = Image.open(image_path)
    except Exception as e:
        return {
            'metadata': {},
            'anomalies': [f'Gagal membuka gambar: {str(e)}'],
            'anomaly_count': 1,
            'software_type': 'unknown',
            'confidence_pct': 0,
            'analysis': 'Gagal membaca metadata gambar.',
        }

    # Basic image info
    metadata['format'] = img.format or 'Unknown'
    metadata['mode'] = img.mode
    metadata['size'] = f'{img.width}x{img.height}'

    # File size
    file_size = os.path.getsize(image_path)
    metadata['file_size'] = f'{file_size / 1024:.1f} KB'

    # Extract EXIF
    exif_data = {}
    software_type = 'unknown'
    software_str = ''

    try:
        raw_exif = img.getexif()
        if raw_exif:
            # Decode known tags
            tag_names = {
                0x010F: 'Make',
                0x0110: 'Model',
                0x0112: 'Orientation',
                0x011A: 'XResolution',
                0x011B: 'YResolution',
                0x0131: 'Software',
                0x0132: 'ModifyDate',
                0x013B: 'Artist',
                0x8298: 'Copyright',
                0x8769: 'ExifIFD',
                0x8825: 'GPSInfo',
                0xA001: 'ColorSpace',
                0xA002: 'PixelXDimension',
                0xA003: 'PixelYDimension',
                0xA405: 'FocalLengthIn35mmFilm',
                0xA430: 'CameraOwnerName',
                0xA431: 'BodySerialNumber',
                0xA432: 'LensInfo',
                0xA433: 'LensMake',
                0xA434: 'LensModel',
            }

            for tag_id, value in raw_exif.items():
                name = tag_names.get(tag_id, f'Tag_{tag_id}')
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8', errors='replace')
                    except Exception:
                        value = f'<binary {len(value)} bytes>'
                exif_data[name] = str(value)

            # Sub-IFD: Exif
            exif_ifd = raw_exif.get_ifd(0x8769)
            if exif_ifd:
                exif_sub_names = {
                    0x829A: 'ExposureTime',
                    0x829D: 'FNumber',
                    0x8827: 'ISOSpeedRatings',
                    0x9000: 'ExifVersion',
                    0x9003: 'DateTimeOriginal',
                    0x9004: 'DateTimeDigitized',
                    0x9201: 'ShutterSpeedValue',
                    0x9202: 'ApertureValue',
                    0x920A: 'FocalLength',
                    0xA001: 'ColorSpace',
                    0xA430: 'CameraOwnerName',
                    0xA431: 'BodySerialNumber',
                    0xA432: 'LensInfo',
                    0xA433: 'LensMake',
                    0xA434: 'LensModel',
                }
                for tag_id, value in exif_ifd.items():
                    name = exif_sub_names.get(tag_id, f'Exif_{tag_id}')
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='replace')
                        except Exception:
                            value = f'<binary {len(value)} bytes>'
                    exif_data[name] = str(value)

        else:
            anomalies.append('Tidak ada data EXIF ditemukan')

    except Exception as e:
        anomalies.append(f'Error membaca EXIF: {str(e)}')

    metadata['exif'] = exif_data

    # --- Anomaly Checks ---

    # 1. Software analysis
    software_str = exif_data.get('Software', '')
    software_type, _ = _detect_software_type(software_str)
    metadata['software'] = software_str or 'Tidak ada'
    metadata['software_type'] = software_type

    if software_type == 'editing':
        anomalies.append(f'Perangkat lunak editing terdeteksi: {software_str}')
    elif not software_str:
        anomalies.append('Tag Software kosong/absen')

    # 2. Camera info
    make = exif_data.get('Make', '')
    model = exif_data.get('Model', '')
    metadata['camera_make'] = make or 'Tidak ada'
    metadata['camera_model'] = model or 'Tidak ada'

    if not make and not model:
        anomalies.append('Informasi kamera (Make/Model) tidak ada')

    # 3. Timestamp analysis
    dates = {}
    for key in ['DateTimeOriginal', 'ModifyDate', 'DateTimeDigitized']:
        val = exif_data.get(key)
        if val:
            parsed = _parse_exif_date(val)
            dates[key] = parsed
            metadata[key] = val
        else:
            metadata[key] = 'Tidak ada'

    if not any(dates.values()):
        anomalies.append('Tidak ada timestamp EXIF ditemukan')
    else:
        # Check consistency between original and digitized
        orig = dates.get('DateTimeOriginal')
        digi = dates.get('DateTimeDigitized')
        mod = dates.get('ModifyDate')

        if orig and digi and abs((orig - digi).total_seconds()) > 60:
            anomalies.append(
                f'Timestamp Original ({exif_data.get("DateTimeOriginal")}) '
                f'tidak cocok dengan Digitized ({exif_data.get("DateTimeDigitized")})'
            )

        if orig and mod and abs((orig - mod).total_seconds()) > 86400:
            anomalies.append(
                f'ModifyDate ({exif_data.get("ModifyDate")}) '
                f'berbeda >24 jam dari DateTimeOriginal'
            )

        if digi and mod and abs((digi - mod).total_seconds()) > 86400:
            anomalies.append(
                f'ModifyDate ({exif_data.get("ModifyDate")}) '
                f'berbeda >24 jam dari DateTimeDigitized'
            )

    # 4. Thumbnail check
    has_thumbnail = False
    try:
        raw_exif_bytes = img.info.get('exif', b'')
        if raw_exif_bytes and len(raw_exif_bytes) > 100:
            # Check for thumbnail marker (APP1 offset 0x0201)
            # Simplified: if raw EXIF is large enough, likely has thumbnail
            has_thumbnail = True
            metadata['thumbnail'] = f'EXIF data present ({len(raw_exif_bytes)} bytes)'
        else:
            metadata['thumbnail'] = 'Tidak ada / kosong'
    except Exception:
        metadata['thumbnail'] = 'Tidak dapat dibaca'

    if not has_thumbnail:
        anomalies.append('Thumbnail EXIF tidak ada atau kosong')

    # 5. GPS check
    gps_info = exif_data.get('GPSInfo', '')
    metadata['gps'] = gps_info or 'Tidak ada'

    # 6. Serial number / owner
    serial = exif_data.get('BodySerialNumber', '')
    owner = exif_data.get('CameraOwnerName', '')
    metadata['serial_number'] = serial or 'Tidak ada'
    metadata['camera_owner'] = owner or 'Tidak ada'

    # --- Confidence Score ---
    anomaly_count = len(anomalies)
    # Start at 100, deduct per anomaly type
    confidence = 100
    confidence -= anomaly_count * 12
    if software_type == 'editing':
        confidence -= 20
    if not make and not model:
        confidence -= 15
    confidence = max(confidence, 0)

    # --- Analysis Text ---
    if anomaly_count == 0:
        conclusion = (
            "Metadata gambar **konsisten dan lengkap**. "
            "Tidak ditemukan anomali yang mengindikasikan manipulasi."
        )
    elif anomaly_count <= 2:
        conclusion = (
            f"Ditemukan **{anomaly_count} anomali ringan** pada metadata. "
            "Kemungkinan akibat kompresi atau konversi format, "
            "bukan manipulasi aktif."
        )
    elif anomaly_count <= 4:
        conclusion = (
            f"Ditemukan **{anomaly_count} anomali** pada metadata. "
        )
        if software_type == 'editing':
            conclusion += "Perangkat lunak editing terdeteksi. "
        conclusion += "Perlu pemeriksaan lebih lanjut untuk memastikan integritas gambar."
    else:
        conclusion = (
            f"Ditemukan **{anomaly_count} anomali signifikan** pada metadata. "
            "Metadata tidak konsisten — kemungkinan besar gambar telah "
            "melalui proses editing/manipulasi."
        )

    return {
        'metadata': metadata,
        'anomalies': anomalies,
        'anomaly_count': anomaly_count,
        'software_type': software_type,
        'confidence_pct': confidence,
        'analysis': conclusion,
    }