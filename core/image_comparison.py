"""
HashProof AI — Image Comparison & Pixel Difference Engine.

Performs side-by-side technical property comparison, absolute pixel delta
calculations, difference maps, and opacity overlay blending.
"""

from io import BytesIO
from typing import Dict, Any, Tuple, Optional
import numpy as np
from PIL import Image, ImageChops

from .hashing import calculate_sha256, readable_size


def compare_images(
    bytes_a: bytes,
    bytes_b: bytes,
    name_a: str = "Image A",
    name_b: str = "Image B",
    amplification: int = 10,
) -> Dict[str, Any]:
    """
    Compare two images technically and visually.

    Returns structured comparison metrics, pixel difference statistics,
    and rendered difference map / blended overlay buffers.
    """
    hash_a = calculate_sha256(bytes_a)
    hash_b = calculate_sha256(bytes_b)
    hashes_match = hash_a == hash_b

    result = {
        "name_a": name_a,
        "name_b": name_b,
        "size_a": len(bytes_a),
        "size_b": len(bytes_b),
        "size_a_readable": readable_size(len(bytes_a)),
        "size_b_readable": readable_size(len(bytes_b)),
        "hash_a": hash_a,
        "hash_b": hash_b,
        "hashes_match": hashes_match,
        "dimensions_match": False,
        "dim_a": None,
        "dim_b": None,
        "format_a": None,
        "format_b": None,
        "modes_match": False,
        "mode_a": None,
        "mode_b": None,
        "differing_pixels_count": 0,
        "differing_pixels_percent": 0.0,
        "mean_absolute_error": 0.0,
        "diff_map_bytes": None,
        "comparison_method": "Exact RGB absolute difference with contrast amplification.",
        "summary": "",
        "limitations": [
            "Pixel difference maps illustrate numerical deltas; they do not determine intent or authenticity.",
            "Compression artifacts (e.g. JPEG) inherently introduce diffuse pixel differences across an entire image.",
            "Images with different dimensions or alignments require normalization before direct pixel comparison.",
        ],
    }

    try:
        with Image.open(BytesIO(bytes_a)) as img_a, Image.open(BytesIO(bytes_b)) as img_b:
            result["format_a"] = img_a.format or "Unknown"
            result["format_b"] = img_b.format or "Unknown"
            result["dim_a"] = (img_a.width, img_a.height)
            result["dim_b"] = (img_b.width, img_b.height)
            result["mode_a"] = img_a.mode
            result["mode_b"] = img_b.mode
            result["dimensions_match"] = result["dim_a"] == result["dim_b"]
            result["modes_match"] = result["mode_a"] == result["mode_b"]

            # Convert both to RGB for uniform pixel math
            rgb_a = img_a.convert("RGB")
            rgb_b = img_b.convert("RGB")

            # Handle dimension mismatch if needed
            was_resized = False
            if not result["dimensions_match"]:
                was_resized = True
                # Match B to A's dimensions for comparison
                rgb_b_comp = rgb_b.resize(rgb_a.size, Image.Resampling.LANCZOS)
            else:
                rgb_b_comp = rgb_b

            # Compute pixel arrays
            arr_a = np.array(rgb_a, dtype=np.int16)
            arr_b = np.array(rgb_b_comp, dtype=np.int16)

            # Absolute difference per channel
            abs_diff = np.abs(arr_a - arr_b)
            # Max difference across R, G, B
            diff_max = np.max(abs_diff, axis=2)

            # Differing pixels (threshold > 0)
            diff_mask = diff_max > 0
            diff_count = int(np.count_nonzero(diff_mask))
            total_pixels = rgb_a.width * rgb_a.height
            diff_percent = (diff_count / total_pixels) * 100.0 if total_pixels > 0 else 0.0
            mae = float(np.mean(abs_diff))

            result["differing_pixels_count"] = diff_count
            result["differing_pixels_percent"] = round(diff_percent, 3)
            result["mean_absolute_error"] = round(mae, 2)
            result["was_resized_for_comparison"] = was_resized

            # Generate amplified visual difference map
            # Scale differences so subtle variations are clearly visible
            amp_diff = np.clip(abs_diff * amplification, 0, 255).astype(np.uint8)
            diff_img = Image.fromarray(amp_diff, mode="RGB")

            diff_buf = BytesIO()
            diff_img.save(diff_buf, format="PNG")
            result["diff_map_bytes"] = diff_buf.getvalue()

            # Technical summary determination
            if hashes_match:
                result["summary"] = "BYTE-FOR-BYTE IDENTICAL: Files possess matching SHA-256 hashes and zero pixel variance."
            elif diff_count == 0 and was_resized:
                result["summary"] = "VISUALLY IDENTICAL AFTER RESCALING: Differing dimensions, but rescaled pixel values are identical."
            elif diff_count == 0 and not was_resized:
                result["summary"] = "IDENTICAL PIXELS, DIFFERENT BYTES: The decoded pixel matrices are identical, but file containers or metadata differ."
            elif diff_percent < 5.0 and mae < 5.0:
                result["summary"] = f"SUBTLE DEVIATIONS ({diff_percent:.2f}% differing pixels, MAE {mae:.1f}): Characteristic of recompression, minor color-space conversion, or slight filtering."
            else:
                result["summary"] = f"SIGNIFICANT VARIANCE ({diff_percent:.2f}% differing pixels, MAE {mae:.1f}): Localized or structural differences observed across compared regions."

    except Exception as e:
        result["summary"] = f"Error during visual comparison: {str(e)}"

    return result


def create_blended_overlay(
    bytes_a: bytes,
    bytes_b: bytes,
    alpha: float = 0.5,
) -> Optional[bytes]:
    """Create an alpha-blended overlay image between Image A and Image B."""
    try:
        with Image.open(BytesIO(bytes_a)) as img_a, Image.open(BytesIO(bytes_b)) as img_b:
            rgb_a = img_a.convert("RGB")
            rgb_b = img_b.convert("RGB")
            if rgb_a.size != rgb_b.size:
                rgb_b = rgb_b.resize(rgb_a.size, Image.Resampling.LANCZOS)

            blended = Image.blend(rgb_a, rgb_b, alpha=float(alpha))
            buf = BytesIO()
            blended.save(buf, format="PNG")
            return buf.getvalue()
    except Exception:
        return None
