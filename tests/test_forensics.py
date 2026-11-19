"""
HashProof AI — Automated Verification Test Suite.

Tests cryptographic hashing, reference comparison, metadata parsing,
image comparison, Error Level Analysis (ELA), AI assessment,
provenance scanning, report serialization, and SQLite persistence.
"""

import sys
import unittest
from io import BytesIO
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image
from core.hashing import calculate_sha256, compare_hashes, create_educational_derivative
from core.metadata_analysis import extract_metadata
from core.image_comparison import compare_images, create_blended_overlay
from core.manipulation_analysis import perform_ela, check_container_consistency
from core.ai_detection import assess_synthetic_media
from core.provenance import inspect_provenance
from core.report_generator import build_examination_record, export_json, generate_printable_html_report
from core.forensic_assistant import ForensicAssistant
from database import init_db, save_report_to_db, get_report_by_id, get_report_count


class TestHashProofCore(unittest.TestCase):

    def setUp(self):
        # Create a synthetic 100x100 RGB image for testing
        img = Image.new("RGB", (100, 100), color=(45, 85, 125))
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=95)
        self.sample_jpeg = buf.getvalue()

        # Create a PNG version
        buf_png = BytesIO()
        img.save(buf_png, format="PNG")
        self.sample_png = buf_png.getvalue()

    def test_sha256_calculation(self):
        digest = calculate_sha256(self.sample_jpeg)
        self.assertIsInstance(digest, str)
        self.assertEqual(len(digest), 64)
        # Deterministic
        self.assertEqual(digest, calculate_sha256(self.sample_jpeg))

    def test_hash_comparison_match_and_mismatch(self):
        digest = calculate_sha256(self.sample_jpeg)
        res_match = compare_hashes(digest, digest)
        self.assertEqual(res_match["status"], "MATCH")
        self.assertTrue(res_match["is_match"])

        different_hash = "a" * 64
        res_mismatch = compare_hashes(digest, different_hash)
        self.assertEqual(res_mismatch["status"], "MISMATCH")
        self.assertFalse(res_mismatch["is_match"])

        res_none = compare_hashes(digest, None)
        self.assertEqual(res_none["status"], "REFERENCE NOT PROVIDED")

        res_invalid = compare_hashes(digest, "not-a-valid-hash")
        self.assertEqual(res_invalid["status"], "INVALID REFERENCE")

    def test_derivative_generation(self):
        deriv_bytes, fn, desc, stats = create_educational_derivative(
            self.sample_jpeg, transform_type="recompress_jpeg", quality=85
        )
        self.assertNotEqual(deriv_bytes, self.sample_jpeg)
        self.assertNotEqual(stats["original_hash"], stats["derivative_hash"])

    def test_metadata_extraction(self):
        meta = extract_metadata(self.sample_jpeg)
        self.assertTrue(meta["is_image"])
        self.assertEqual(meta["format"], "JPEG")
        self.assertEqual(meta["width"], 100)
        self.assertEqual(meta["height"], 100)
        self.assertIn("File Properties", meta["categories"])

    def test_corrupted_image_handling(self):
        corrupted = b"NOT_AN_IMAGE_DATA_12345"
        meta = extract_metadata(corrupted)
        self.assertFalse(meta["is_image"])
        self.assertTrue(any(obs["type"] == "DECODE_ERROR" for obs in meta["observations"]))

    def test_image_comparison(self):
        # Compare JPEG with PNG of same content
        comp = compare_images(self.sample_jpeg, self.sample_png, "Sample JPEG", "Sample PNG")
        self.assertFalse(comp["hashes_match"])
        self.assertEqual(comp["dim_a"], comp["dim_b"])
        self.assertIsNotNone(comp["diff_map_bytes"])

    def test_manipulation_ela(self):
        ela_res = perform_ela(self.sample_jpeg, quality=95)
        self.assertTrue(ela_res["success"])
        self.assertIsNotNone(ela_res["ela_image_bytes"])
        self.assertGreaterEqual(ela_res["mean_error"], 0.0)

    def test_container_consistency(self):
        res = check_container_consistency(self.sample_jpeg, "test.jpg")
        self.assertEqual(res["status"], "CONSISTENT")
        self.assertEqual(res["detected_format"], "JPEG")

        # Fake mismatch test: PNG bytes named as .jpg
        mismatch_res = check_container_consistency(self.sample_png, "fraudulent.jpg")
        self.assertEqual(mismatch_res["status"], "MISMATCH_DETECTED")

    def test_ai_detection_baseline(self):
        ai_res = assess_synthetic_media(self.sample_jpeg)
        self.assertIn(ai_res["assessment_label"], [
            "NO STRONG AI-GENERATION SIGNALS DETECTED",
            "AI-GENERATION SIGNALS DETECTED",
            "INCONCLUSIVE"
        ])
        self.assertIsNotNone(ai_res["raw_score"])

    def test_provenance_inspection(self):
        prov = inspect_provenance(self.sample_jpeg, "sample.jpg")
        self.assertIn("status", prov)
        self.assertFalse(prov["has_c2pa_manifest"])

    def test_report_building_and_export(self):
        meta = extract_metadata(self.sample_jpeg)
        record = build_examination_record(
            examination_id="HP-TEST-001",
            filename="sample.jpg",
            file_size_bytes=len(self.sample_jpeg),
            file_size_readable="10 KB",
            file_hash=calculate_sha256(self.sample_jpeg),
            detected_format="JPEG",
            metadata_results=meta,
        )
        self.assertEqual(record["report_id"], "HP-TEST-001")
        json_str = export_json(record)
        self.assertIn("HP-TEST-001", json_str)

        html_str = generate_printable_html_report(record)
        self.assertIn("HASHPROOF", html_str)
        self.assertIn("HP-TEST-001", html_str)

    def test_database_persistence(self):
        init_db()
        count_before = get_report_count()
        test_rep = {
            "report_id": "TEST-DB-001",
            "filename": "unit_test_img.jpg",
            "sha256": calculate_sha256(self.sample_jpeg),
            "custom_field": "forensic_data",
        }
        saved = save_report_to_db(test_rep)
        self.assertEqual(saved["report_id"], "TEST-DB-001")

        retrieved = get_report_by_id("TEST-DB-001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["filename"], "unit_test_img.jpg")
        self.assertGreaterEqual(get_report_count(), count_before)


if __name__ == "__main__":
    unittest.main()
