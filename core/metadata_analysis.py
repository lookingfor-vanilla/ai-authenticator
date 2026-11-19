"""
HashProof AI — Advanced Metadata & EXIF Analysis Engine.

Extracts deep image properties, EXIF tags, GPS coordinates, camera configurations,
and software signatures with forensic caveats and privacy protection.
"""

from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ExifTags, UnidentifiedImageError


def _convert_gps_coordinate(coord_tuple, ref: str) -> Optional[float]:
    """Convert EXIF GPS degree/minute/second rational tuple into decimal degrees."""
    try:
        if not coord_tuple or len(coord_tuple) < 3:
            return None

        # Handle tuple of values or IFDRational objects
        degrees = float(coord_tuple[0])
        minutes = float(coord_tuple[1])
        seconds = float(coord_tuple[2])

        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref.upper() in ["S", "W"]:
            decimal = -decimal
        return round(decimal, 6)
    except Exception:
        return None


def extract_metadata(file_bytes: bytes) -> Dict[str, Any]:
    """
    Extract comprehensive image metadata, categorized technical properties,
    EXIF records, GPS coordinates, and anomaly observations.
    """
    result = {
        "is_image": False,
        "format": "Unknown",
        "mime_type": "application/octet-stream",
        "dimensions": None,
        "width": 0,
        "height": 0,
        "color_mode": "Unknown",
        "aspect_ratio": "Unknown",
        "exif_present": False,
        "exif_count": 0,
        "categories": {
            "File Properties": {},
            "Camera & Hardware": {},
            "Exposure & Optics": {},
            "Software & History": {},
            "Geolocation": {},
            "Other EXIF Tags": {},
        },
        "gps": None,
        "observations": [],
        "limitations": [
            "Metadata can be modified, removed, or fabricated by standard editing tools.",
            "Missing EXIF data does not prove that an image was altered or AI-generated.",
            "Camera and software tags indicate claimed origins, not independently verified truths.",
            "GPS coordinates represent the recorded device location at capture, if available.",
        ],
    }

    try:
        with Image.open(BytesIO(file_bytes)) as img:
            result["is_image"] = True
            result["format"] = img.format or "Unknown"
            result["width"] = img.width
            result["height"] = img.height
            result["dimensions"] = f"{img.width} × {img.height} px"
            result["color_mode"] = img.mode

            # Aspect ratio calculation
            if img.width > 0 and img.height > 0:
                import math
                gcd = math.gcd(img.width, img.height)
                r_w = img.width // gcd
                r_h = img.height // gcd
                if r_w <= 16 and r_h <= 16:
                    result["aspect_ratio"] = f"{r_w}:{r_h}"
                else:
                    result["aspect_ratio"] = f"{img.width / img.height:.2f}:1"

            result["categories"]["File Properties"] = {
                "Detected Format": result["format"],
                "Dimensions": result["dimensions"],
                "Color Mode": result["color_mode"],
                "Aspect Ratio": result["aspect_ratio"],
                "Animated Frames": getattr(img, "n_frames", 1),
            }

            # ICC profile presence
            icc = img.info.get("icc_profile")
            if icc:
                result["categories"]["File Properties"]["Embedded ICC Profile"] = (
                    f"Present ({len(icc)} bytes)"
                )

            # Read EXIF
            raw_exif = {}
            try:
                exif_data = img.getexif()
                if exif_data:
                    for tag_id, val in exif_data.items():
                        tag_name = ExifTags.TAGS.get(tag_id, f"Tag_{tag_id}")
                        if isinstance(val, bytes):
                            val = val.decode("utf-8", errors="replace")
                        raw_exif[tag_name] = str(val)[:500]

                    # Read IFD sub-blocks (EXIF IFD, GPS IFD)
                    for ifd_id in (ExifTags.IFD.Exif, ExifTags.IFD.GPSInfo):
                        try:
                            ifd = exif_data.get_ifd(ifd_id)
                            for k, v in ifd.items():
                                if ifd_id == ExifTags.IFD.GPSInfo:
                                    tname = ExifTags.GPSTAGS.get(k, f"GPS_{k}")
                                else:
                                    tname = ExifTags.TAGS.get(k, f"Sub_{k}")
                                if isinstance(v, bytes):
                                    v = v.decode("utf-8", errors="replace")
                                raw_exif[tname] = v
                        except Exception:
                            pass
            except Exception:
                pass

            if raw_exif:
                result["exif_present"] = True
                result["exif_count"] = len(raw_exif)

                # Process specific categories
                # 1. Camera & Hardware
                camera_keys = ["Make", "Model", "LensMake", "LensModel", "SerialNumber", "BodySerialNumber"]
                for k in camera_keys:
                    if k in raw_exif:
                        result["categories"]["Camera & Hardware"][k] = str(raw_exif[k])

                # 2. Exposure & Optics
                exposure_keys = [
                    "ExposureTime", "FNumber", "ISOSpeedRatings", "FocalLength",
                    "FocalLengthIn35mmFilm", "Flash", "WhiteBalance", "ExposureProgram",
                    "MeteringMode", "DateTimeOriginal", "DateTimeDigitized"
                ]
                for k in exposure_keys:
                    if k in raw_exif:
                        result["categories"]["Exposure & Optics"][k] = str(raw_exif[k])

                # 3. Software & History
                software_keys = ["Software", "ProcessingSoftware", "Artist", "Copyright", "DateTime"]
                for k in software_keys:
                    if k in raw_exif:
                        result["categories"]["Software & History"][k] = str(raw_exif[k])

                # 4. Geolocation (GPS)
                gps_info = {}
                lat_val = raw_exif.get("GPSLatitude")
                lat_ref = raw_exif.get("GPSLatitudeRef", "N")
                lon_val = raw_exif.get("GPSLongitude")
                lon_ref = raw_exif.get("GPSLongitudeRef", "E")
                alt_val = raw_exif.get("GPSAltitude")

                if lat_val and lon_val:
                    lat_dec = _convert_gps_coordinate(lat_val, str(lat_ref))
                    lon_dec = _convert_gps_coordinate(lon_val, str(lon_ref))
                    if lat_dec is not None and lon_dec is not None:
                        gps_info["latitude"] = lat_dec
                        gps_info["longitude"] = lon_dec
                        gps_info["altitude"] = str(alt_val) if alt_val else "Unknown"
                        gps_info["maps_link"] = f"https://www.google.com/maps?q={lat_dec},{lon_dec}"
                        result["gps"] = gps_info
                        result["categories"]["Geolocation"] = {
                            "Latitude": f"{lat_dec}° ({lat_ref})",
                            "Longitude": f"{lon_dec}° ({lon_ref})",
                            "Altitude": str(alt_val) if alt_val else "Not recorded",
                            "Maps Reference": gps_info["maps_link"],
                        }

                # 5. Other EXIF
                handled = set(camera_keys + exposure_keys + software_keys + [
                    "GPSLatitude", "GPSLatitudeRef", "GPSLongitude", "GPSLongitudeRef", "GPSAltitude"
                ])
                for k, v in raw_exif.items():
                    if k not in handled and not k.startswith("GPS"):
                        result["categories"]["Other EXIF Tags"][k] = str(v)[:300]

                # Evaluate Observations
                software_tag = raw_exif.get("Software", "")
                if any(sw in software_tag.lower() for sw in ["photoshop", "gimp", "canva", "lightroom", "paint.net", "snapseed"]):
                    result["observations"].append({
                        "type": "SOFTWARE_SIGNATURE",
                        "severity": "REVIEW_RECOMMENDED",
                        "title": "Editing Application Recorded",
                        "detail": f"The metadata contains a Software tag identifying '{software_tag}'.",
                        "interpretation": "Indicates the file passed through post-processing or export software. Does not by itself establish malicious alteration.",
                    })

                # Check timestamp divergence
                dto = raw_exif.get("DateTimeOriginal")
                dt = raw_exif.get("DateTime")
                if dto and dt and dto != dt:
                    result["observations"].append({
                        "type": "TIMESTAMP_DIVERGENCE",
                        "severity": "OBSERVATION",
                        "title": "Capture vs Modification Timestamp Divergence",
                        "detail": f"Capture time recorded as '{dto}', but last modified time recorded as '{dt}'.",
                        "interpretation": "Commonly occurs when a file is edited or saved after initial capture.",
                    })
            else:
                result["observations"].append({
                    "type": "EXIF_ABSENT",
                    "severity": "NEUTRAL",
                    "title": "No Readable EXIF Metadata Found",
                    "detail": "The image file contains no embedded EXIF tags.",
                    "interpretation": "Typical of images shared via web platforms, messaging apps, screenshots, or stripped by privacy filters. Not proof of manipulation.",
                })

    except (UnidentifiedImageError, OSError, ValueError) as err:
        result["observations"].append({
            "type": "DECODE_ERROR",
            "severity": "WARNING",
            "title": "Image Decoding Failed",
            "detail": f"File could not be parsed as a standard image: {str(err)}",
            "interpretation": "The file may be corrupted, truncated, or formatted differently than its extension suggests.",
        })

    return result
