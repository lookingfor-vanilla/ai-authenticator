"""
HashProof AI — Grounded Forensic AI Assistant Engine.

Provides deterministic, fact-grounded explanations of examination data,
answers forensic questions, and ensures clear distinction between measured facts,
probabilistic model scores, and investigative unknowns.
"""

from typing import Dict, Any, List, Optional


class ForensicAssistant:
    """
    Forensic AI reasoning engine grounded strictly in current examination facts.
    """

    def __init__(self, record: Optional[Dict[str, Any]] = None):
        self.record = record or {}

    def set_record(self, record: Dict[str, Any]):
        self.record = record

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Produce a grounded answer to an examiner's question based on the active record.
        """
        q = question.lower().strip()
        rec = self.record
        ev = rec.get("evidence", {})
        integ = rec.get("integrity_analysis", {})
        meta = rec.get("metadata_analysis", {})
        ai = rec.get("synthetic_media_assessment", {})
        manip = rec.get("manipulation_analysis", {})
        prov = rec.get("provenance_analysis", {})
        findings = rec.get("findings", [])

        # Default structure
        response = {
            "question": question,
            "measured_facts": [],
            "interpretations": [],
            "investigative_unknowns": [],
            "recommended_next_steps": [],
            "direct_answer": "",
        }

        # 1. SHA-256 Hash query
        if "hash" in q or "sha" in q or "sha-256" in q or "fingerprint" in q:
            sha = ev.get("sha256", "Not yet calculated")
            status = integ.get("status", "NO_COMPARISON")
            response["measured_facts"].append(f"Calculated SHA-256 digest: {sha}")
            response["measured_facts"].append(f"Comparison status: {status}")

            if status == "MATCH":
                response["direct_answer"] = (
                    "The uploaded file matches the reference digest bit-for-bit. "
                    "This demonstrates mathematical identity between the compared byte sequences."
                )
                response["interpretations"].append("The file contents have not changed relative to the reference copy.")
                response["investigative_unknowns"].append("A matching hash does not prove who authored the file or that the content represents real events.")
            elif status == "MISMATCH":
                response["direct_answer"] = (
                    "The calculated hash differs from the reference digest. Under SHA-256, even a single altered bit "
                    "in the header, metadata, or pixel values produces a completely different hash digest."
                )
                response["interpretations"].append("The files are not byte-for-byte identical.")
                response["investigative_unknowns"].append("Hash comparison alone cannot identify which specific pixels or metadata fields were altered.")
                response["recommended_next_steps"].append("Run the Side-by-Side Image Comparison Lab to inspect visual differences.")
            else:
                response["direct_answer"] = (
                    f"The file has a unique SHA-256 digest ({sha[:12]}...). "
                    "Because no reference hash was provided, this value serves as an initial custody baseline."
                )

        # 2. Metadata / EXIF query
        elif "exif" in q or "metadata" in q or "camera" in q or "gps" in q:
            exif_count = meta.get("exif_count", 0)
            exif_present = meta.get("exif_present", False)
            response["measured_facts"].append(f"EXIF tags detected: {exif_count}")
            response["measured_facts"].append(f"Image container format: {meta.get('format', 'Unknown')}")

            if not exif_present:
                response["direct_answer"] = (
                    "No EXIF metadata was found in this file. In forensic investigations, missing EXIF is extremely common "
                    "and occurs automatically when images are uploaded to social media platforms, sent via messaging apps, "
                    "or captured as screenshots. It does NOT prove the image was tampered with or AI-generated."
                )
                response["interpretations"].append("The file has likely been stripped of metadata during transit or export.")
                response["investigative_unknowns"].append("Original camera hardware, capture timestamp, and geolocation cannot be verified from container headers.")
                response["recommended_next_steps"].append("Request original camera memory card / uncompressed source file from evidence custodian.")
            else:
                cats = meta.get("categories", {})
                cam = cats.get("Camera & Hardware", {})
                response["direct_answer"] = (
                    f"The image contains {exif_count} EXIF tags, including hardware descriptors ({cam.get('Make', '')} {cam.get('Model', '')}). "
                    "Remember that EXIF fields can be edited or spoofed using standard metadata utilities."
                )
                response["interpretations"].append("Metadata reflects claimed capture settings.")
                response["investigative_unknowns"].append("Authenticity of metadata timestamps requires cross-referencing with external evidence.")

        # 3. AI / Synthetic Media query
        elif "ai" in q or "synthetic" in q or "generator" in q or "deepfake" in q:
            label = ai.get("assessment_label", "UNAVAILABLE")
            score = ai.get("raw_score", "None")
            signals = ai.get("signals_found", [])

            response["measured_facts"].append(f"Detector: {ai.get('detector_name', 'Baseline')}")
            response["measured_facts"].append(f"Assessment label: {label} (Score: {score})")
            for s in signals:
                response["measured_facts"].append(f"Observed signal: {s}")

            response["direct_answer"] = (
                f"The AI-generation assessment returned: '{label}'. "
                "This is a probabilistic model score based on frequency gradients and metadata signatures. "
                "It is NOT a definitive verdict and must not be used as the sole basis for evidentiary conclusions."
            )
            response["interpretations"].append(ai.get("interpretation", ""))
            response["investigative_unknowns"].append("Modern diffusion and GAN models can produce images without detectable metadata markers.")
            response["recommended_next_steps"].append("Examine Error Level Analysis (ELA) and cross-reference with physical provenance.")

        # 4. Image Difference query
        elif "difference" in q or "compare" in q or "changed" in q or "derivative" in q:
            response["direct_answer"] = (
                "When comparing two images, HashProof AI computes both cryptographic hash equality and "
                "pixel-by-pixel mathematical delta. If images look identical to the human eye but have different hashes, "
                "they differ in byte encoding (e.g. recompression quality, container metadata, or color profile)."
            )
            response["interpretations"].append("Visual similarity does not equal digital byte identity.")
            response["recommended_next_steps"].append("Use the Image Comparison Lab with difference map amplification.")

        # 5. General Summary query
        else:
            fn = ev.get("filename", "Evidence file")
            response["direct_answer"] = (
                f"Forensic Summary for '{fn}':\n"
                f"• SHA-256: {ev.get('sha256', 'N/A')}\n"
                f"• Format: {meta.get('format', 'N/A')} ({meta.get('dimensions', 'N/A')})\n"
                f"• EXIF Tags: {meta.get('exif_count', 0)}\n"
                f"• Integrity Status: {integ.get('status', 'NOT TESTED')}\n"
                f"• AI Assessment: {ai.get('assessment_label', 'NOT TESTED')}\n"
                f"• Provenance: {prov.get('status', 'NOT TESTED')}"
            )
            response["interpretations"].append("Observations represent preliminary screening.")
            response["recommended_next_steps"].append("Export the formal JSON or printable examination report.")

        return response
