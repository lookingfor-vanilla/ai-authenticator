"""
HashProof AI — Legacy Backend Compatibility Adapter.

Maintains backward compatibility with earlier project backend experiments.
Delegates to core forensic modules.
"""

from typing import Dict, Any
from core.hashing import calculate_sha256
from core.metadata_analysis import extract_metadata
from core.manipulation_analysis import check_container_consistency


def analyze_file(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Compatibility wrapper providing core analysis fields."""
    sha = calculate_sha256(file_bytes)
    consistency = check_container_consistency(file_bytes, filename)
    meta = extract_metadata(file_bytes)

    return {
        "filename": filename,
        "file_size_bytes": len(file_bytes),
        "sha256": sha,
        "detected_format": consistency["detected_format"],
        "consistency_status": consistency["status"],
        "is_image": meta["is_image"],
        "metadata": meta,
    }
