"""
HashProof AI — Image Manipulation & Forensic Artifact Analysis Engine.

Performs Error Level Analysis (ELA), format container consistency verification,
and structural compression artifact evaluation.
"""

from io import BytesIO
from typing import Dict, Any, Tuple, Optional
import numpy as np
from PIL import Image, ImageEnhance, UnidentifiedImageError


def check_container_consistency(file_bytes: bytes, filename: str, declared_mime: Optional[str] = None) -> Dict[str, Any]:
    """
    Examine magic numbers (file headers) against file extension and MIME type
    to detect container mismatches.
    """
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    header = file_bytes[:16]

    detected_format = "Unknown"
    detected_mime = "application/octet-stream"

    if header.startswith(b"\xff\xd8\xff"):
        detected_format = "JPEG"
        detected_mime = "image/jpeg"
    elif header.startswith(b"\x89PNG\r\n\x1a\n"):
        detected_format = "PNG"
        detected_mime = "image/png"
    elif header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        detected_format = "WEBP"
        detected_mime = "image/webp"
    elif header.startswith(b"II*\x00") or header.startswith(b"MM\x00*"):
        detected_format = "TIFF"
        detected_mime = "image/tiff"
    elif header.startswith(b"BM"):
        detected_format = "BMP"
        detected_mime = "image/bmp"
    elif header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
        detected_format = "GIF"
        detected_mime = "image/gif"

    # Consistency assessment
    is_extension_consistent = True
    if detected_format == "JPEG" and ext not in ["jpg", "jpeg", "jpe", "jfif"]:
        is_extension_consistent = False
    elif detected_format == "PNG" and ext != "png":
        is_extension_consistent = False
    elif detected_format == "WEBP" and ext != "webp":
        is_extension_consistent = False
    elif detected_format == "TIFF" and ext not in ["tif", "tiff"]:
        is_extension_consistent = False
    elif detected_format == "BMP" and ext != "bmp":
        is_extension_consistent = False

    status = "CONSISTENT" if is_extension_consistent else "MISMATCH_DETECTED"

    observations = []
    if not is_extension_consistent and detected_format != "Unknown":
        observations.append({
            "type": "CONTAINER_EXTENSION_MISMATCH",
            "severity": "REVIEW_RECOMMENDED",
            "title": "File Extension Does Not Match Internal Format",
            "detail": f"File is named with extension '.{ext}', but internal file headers identify it as '{detected_format}'.",
            "interpretation": "May occur through manual renaming, format conversion tools, or deliberate obfuscation.",
        })
    else:
        observations.append({
            "type": "CONTAINER_VERIFIED",
            "severity": "NORMAL",
            "title": "Container Header Consistent",
            "detail": f"Magic bytes match declared format '{detected_format}'.",
            "interpretation": "File container format matches standard specifications.",
        })

    return {
        "status": status,
        "detected_format": detected_format,
        "detected_mime": detected_mime,
        "file_extension": ext,
        "declared_mime": declared_mime or "Not supplied",
        "is_consistent": is_extension_consistent,
        "observations": observations,
    }


def perform_ela(
    file_bytes: bytes,
    quality: int = 95,
    scale: int = 15,
) -> Dict[str, Any]:
    """
    Perform Error Level Analysis (ELA).

    Recompresses the image at a known JPEG quality, computes the difference
    matrix between original and recompressed image, and scales the difference.
    """
    result = {
        "success": False,
        "ela_image_bytes": None,
        "quality_used": quality,
        "scale_factor": scale,
        "mean_error": 0.0,
        "max_error": 0.0,
        "interpretation": "",
        "observations": [],
        "limitations": [
            "ELA highlights compression variance, which naturally occurs near high-contrast edges and complex textures.",
            "A bright region in an ELA map is NOT definitive proof of splicing or manipulation.",
            "ELA is primarily calibrated for lossy formats (JPEG); uncompressed PNGs will show high uniform recompression error.",
        ],
    }

    try:
        with Image.open(BytesIO(file_bytes)) as original:
            rgb_orig = original.convert("RGB")

            # Resave at specified quality
            temp_buf = BytesIO()
            rgb_orig.save(temp_buf, format="JPEG", quality=quality)
            temp_buf.seek(0)

            with Image.open(temp_buf) as recompressed:
                rgb_decomp = recompressed.convert("RGB")

                # Compute difference array
                arr_orig = np.array(rgb_orig, dtype=np.float32)
                arr_decomp = np.array(rgb_decomp, dtype=np.float32)

                diff = np.abs(arr_orig - arr_decomp)
                mean_err = float(np.mean(diff))
                max_err = float(np.max(diff))

                # Scale error for visualization
                scaled_diff = np.clip(diff * scale, 0, 255).astype(np.uint8)
                ela_img = Image.fromarray(scaled_diff, mode="RGB")

                out_buf = BytesIO()
                ela_img.save(out_buf, format="PNG")

                result["success"] = True
                result["ela_image_bytes"] = out_buf.getvalue()
                result["mean_error"] = round(mean_err, 2)
                result["max_error"] = round(max_err, 2)

                if mean_err < 1.0:
                    result["interpretation"] = (
                        "Very low overall error level. Consistent with an image saved recently "
                        f"at approximately {quality}% JPEG quality or higher."
                    )
                elif mean_err > 8.0:
                    result["interpretation"] = (
                        "High overall error level across the image. Suggests the source image had a "
                        "substantially different compression profile than the 95% recompression baseline."
                    )
                else:
                    result["interpretation"] = (
                        "Moderate error levels distributed across textures. Examiner should inspect whether "
                        "isolated objects show conspicuously brighter or darker error levels than surrounding regions of similar texture."
                    )

                result["observations"].append({
                    "type": "ELA_ANALYSIS_COMPLETED",
                    "severity": "NORMAL",
                    "title": "ELA Recompression Assessment",
                    "detail": f"Mean error: {mean_err:.2f}, Max error: {max_err:.2f} (scale {scale}×, quality {quality}%).",
                    "interpretation": result["interpretation"],
                })

    except Exception as e:
        result["interpretation"] = f"ELA could not be executed: {str(e)}"
        result["observations"].append({
            "type": "ELA_FAILED",
            "severity": "WARNING",
            "title": "ELA Execution Halted",
            "detail": str(e),
            "interpretation": "Image could not be converted or recompressed as JPEG.",
        })

    return result
