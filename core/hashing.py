"""
HashProof AI — Cryptographic Hashing and Integrity Engine.

Provides exact byte-level SHA-256 calculation, strict reference comparison,
and educational derivative generation demonstrating the avalanche effect.
"""

import hashlib
from io import BytesIO
from typing import Dict, Any, Optional, Tuple
from PIL import Image


def calculate_sha256(data: bytes) -> str:
    """Calculate the cryptographic SHA-256 digest directly from raw file bytes."""
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("Input data must be bytes or bytearray.")
    return hashlib.sha256(data).hexdigest()


def readable_size(size_bytes: int) -> str:
    """Format bytes into readable binary units (B, KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def compare_hashes(current_hash: str, reference_hash: Optional[str]) -> Dict[str, Any]:
    """
    Compare a calculated file hash against an optional reference hash.

    Strict forensic outcomes:
    - MATCH: Byte-for-byte exact equality between verified hashes.
    - MISMATCH: Hashes differ; content or representation has changed.
    - REFERENCE NOT PROVIDED: Hash recorded without comparison baseline.
    - INVALID REFERENCE: Provided string is not a valid 64-hex SHA-256 digest.
    """
    if not current_hash:
        return {
            "status": "ERROR",
            "message": "Current hash is empty.",
            "is_match": False,
        }

    current = current_hash.strip().lower()

    if not reference_hash or not reference_hash.strip():
        return {
            "status": "REFERENCE NOT PROVIDED",
            "current_hash": current,
            "reference_hash": None,
            "is_match": None,
            "message": "The file hash was calculated, but no reference copy or digest was supplied for comparison.",
            "conclusion": "Hash recorded for future baseline integrity tracking.",
        }

    ref = reference_hash.strip().lower()

    # Validate 64-character hexadecimal format
    if len(ref) != 64 or any(c not in "0123456789abcdef" for c in ref):
        return {
            "status": "INVALID REFERENCE",
            "current_hash": current,
            "reference_hash": ref,
            "is_match": False,
            "message": "The supplied reference string is not a valid 64-character hexadecimal SHA-256 digest.",
            "conclusion": "Comparison cannot be performed against a malformed digest.",
        }

    is_match = current == ref

    if is_match:
        return {
            "status": "MATCH",
            "current_hash": current,
            "reference_hash": ref,
            "is_match": True,
            "message": "The calculated hash matches the reference hash identically.",
            "conclusion": "Supports the conclusion that the compared byte sequences are identical.",
            "caveat": "A matching hash proves byte-for-byte agreement with the reference; it does not prove authorship or that the depicted content is genuine.",
        }
    else:
        # Count leading matching characters for technical transparency only
        matching_chars = 0
        for c1, c2 in zip(current, ref):
            if c1 == c2:
                matching_chars += 1
            else:
                break

        return {
            "status": "MISMATCH",
            "current_hash": current,
            "reference_hash": ref,
            "is_match": False,
            "matching_leading_chars": matching_chars,
            "message": "The calculated hash differs from the reference hash.",
            "conclusion": "The files are not byte-for-byte identical. A change in content, metadata, or encoding representation has occurred.",
            "caveat": "Due to the cryptographic avalanche effect, even a single modified pixel or metadata byte changes the digest completely.",
        }


def create_educational_derivative(
    original_bytes: bytes,
    transform_type: str = "recompress_jpeg",
    quality: int = 92,
) -> Tuple[bytes, str, str, Dict[str, Any]]:
    """
    Generate an explicit derivative of an image to demonstrate the avalanche effect.

    Transform types:
    - 'recompress_jpeg': Recompresses image at a specific JPEG quality.
    - 'resize_1px': Expands or shrinks image dimension by 1 pixel.
    - 'strip_metadata': Saves image without any EXIF/ICC metadata.
    """
    orig_hash = calculate_sha256(original_bytes)

    with Image.open(BytesIO(original_bytes)) as img:
        # Convert RGBA/P to RGB for JPEG compatibility if needed
        format_out = img.format or "JPEG"
        if format_out.upper() not in ["JPEG", "JPG", "PNG", "WEBP"]:
            format_out = "PNG"

        buf = BytesIO()

        if transform_type == "recompress_jpeg":
            rgb_img = img.convert("RGB") if img.mode != "RGB" else img
            rgb_img.save(buf, format="JPEG", quality=quality)
            desc = f"JPEG recompression at {quality}% quality."
            ext = "jpg"

        elif transform_type == "resize_1px":
            new_size = (max(1, img.width + 1), max(1, img.height + 1))
            resized = img.resize(new_size, Image.Resampling.LANCZOS)
            resized.save(buf, format=format_out)
            desc = f"Dimension modified by +1 pixel ({img.width}×{img.height} → {new_size[0]}×{new_size[1]})."
            ext = format_out.lower()

        elif transform_type == "strip_metadata":
            # Save raw pixel data without metadata dictionary
            clean_img = Image.new(img.mode, img.size)
            clean_img.putdata(list(img.getdata()))
            clean_img.save(buf, format=format_out)
            desc = "All EXIF and ancillary metadata stripped; pixel data preserved."
            ext = format_out.lower()

        else:
            raise ValueError(f"Unknown transform type: {transform_type}")

    derivative_bytes = buf.getvalue()
    derivative_hash = calculate_sha256(derivative_bytes)

    comparison = compare_hashes(derivative_hash, orig_hash)

    stats = {
        "original_size": len(original_bytes),
        "derivative_size": len(derivative_bytes),
        "size_delta_bytes": len(derivative_bytes) - len(original_bytes),
        "original_hash": orig_hash,
        "derivative_hash": derivative_hash,
        "comparison": comparison,
        "explanation": (
            "Because cryptographic hash functions like SHA-256 exhibit the avalanche effect, "
            "any minor change in encoding, metadata, or pixel values results in an entirely "
            "unrelated hash digest, even if the image appears visually indistinguishable."
        ),
    }

    filename = f"derivative_{transform_type}.{ext}"
    return derivative_bytes, filename, desc, stats
