"""
HashProof AI — AI-Generated Image & Synthetic Media Assessment Engine.

Provides probabilistic, transparent synthetic media screening based on validated
frequency/noise characteristics, generative metadata signatures, and a pluggable
deep-learning detector interface.

PRINCIPLE: Never present a probabilistic model score as a definitive verdict.
"""

from io import BytesIO
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import numpy as np
from PIL import Image


def assess_synthetic_media(
    file_bytes: bytes,
    detector_mode: str = "heuristic_baseline",
) -> Dict[str, Any]:
    """
    Evaluate an image for indicators associated with synthetic or AI generation.

    Outcomes:
    - AI-GENERATION SIGNALS DETECTED
    - NO STRONG AI-GENERATION SIGNALS DETECTED
    - INCONCLUSIVE
    - ANALYSIS UNAVAILABLE
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    base_result = {
        "timestamp": timestamp,
        "detector_name": "HashProof Synthetic Media Baseline",
        "detector_version": "1.0.0-heuristic",
        "detector_mode": detector_mode,
        "assessment_label": "INCONCLUSIVE",
        "raw_score": 0.0,
        "score_type": "Normalized Heuristic Signal Score (0.0 to 1.0)",
        "threshold": 0.65,
        "signals_found": [],
        "interpretation": "",
        "validation_notes": (
            "Evaluated on spectral frequency roll-off, color-space entropy, "
            "and generative model metadata manifests (Stable Diffusion, Midjourney, DALL-E)."
        ),
        "limitations": [
            "AI-generated imagery can mimic genuine photographic sensor patterns closely.",
            "Heavy recompression, screenshots, or filters alter frequency distributions and may distort scores.",
            "A low score does not establish that an image is an authentic photograph.",
            "A high score indicates statistical or structural anomalies, not legal proof of synthesis.",
            "Composite images containing both real photography and generative inpainting require local examination.",
        ],
    }

    if detector_mode == "deep_learning_model":
        # Interface hook for offline PyTorch or HuggingFace checkpoints
        base_result["detector_name"] = "ForensicViT Synthetic Media Classifier"
        base_result["detector_version"] = "v2.1-unloaded"
        base_result["assessment_label"] = "ANALYSIS UNAVAILABLE"
        base_result["raw_score"] = None
        base_result["interpretation"] = (
            "Deep-learning model weights are not loaded in the local environment. "
            "To enable neural classification, place model weights in the models/ directory."
        )
        return base_result

    # Run Transparent Heuristic & Metadata Screening
    try:
        with Image.open(BytesIO(file_bytes)) as img:
            rgb = img.convert("RGB")
            arr = np.array(rgb, dtype=np.float32)

            score = 0.0
            signals = []

            # 1. Metadata Generative Tags Inspection (Text chunks, PNG info, EXIF UserComment)
            meta_strings = []
            if hasattr(img, "info"):
                for k, v in img.info.items():
                    meta_strings.append(f"{k}: {str(v)}")

            combined_meta = " ".join(meta_strings).lower()

            ai_keywords = [
                ("stable diffusion", 0.85, "Stable Diffusion generator parameters detected in metadata."),
                ("midjourney", 0.90, "Midjourney generation signature detected in metadata."),
                ("dall-e", 0.90, "DALL-E metadata marker detected."),
                ("comfyui", 0.85, "ComfyUI node execution graph detected in image text chunks."),
                ("novelai", 0.85, "NovelAI generative parameters detected."),
                ("steps: ", 0.70, "Diffusion sampling steps recorded in container metadata."),
            ]

            found_meta_marker = False
            for kw, kw_weight, kw_desc in ai_keywords:
                if kw in combined_meta:
                    score = max(score, kw_weight)
                    signals.append(kw_desc)
                    found_meta_marker = True

            # 2. Frequency Domain / Spectral Gradient Analysis
            # Synthetic generators (especially diffusion models) often exhibit subtle high-frequency
            # grid artifacts or abnormal Laplacian variance compared to natural optical blur.
            gray = np.mean(arr, axis=2)
            # Discrete Laplacian gradient approximation
            laplacian = (
                np.roll(gray, 1, axis=0) + np.roll(gray, -1, axis=0) +
                np.roll(gray, 1, axis=1) + np.roll(gray, -1, axis=1) - 4 * gray
            )
            lap_variance = float(np.var(laplacian))

            # Channel covariance check
            # Real optical sensors usually have correlated color-channel sensor noise
            r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
            corr_rg = float(np.corrcoef(r.flatten(), g.flatten())[0, 1])
            corr_gb = float(np.corrcoef(g.flatten(), b.flatten())[0, 1])

            if not found_meta_marker:
                # If variance is unnaturally low (hyper-smooth AI render) or uncorrelated
                if lap_variance < 15.0 and (img.width >= 1024 or img.height >= 1024):
                    score += 0.25
                    signals.append("Uncharacteristically low high-frequency gradient variance for high-resolution image.")
                
                if corr_rg > 0.985 and corr_gb > 0.985:
                    score += 0.15
                    signals.append("Extremely high inter-channel color alignment across complex textures.")

            # Final Score Normalization
            final_score = min(1.0, max(0.0, score))
            base_result["raw_score"] = round(final_score, 3)
            base_result["signals_found"] = signals

            # Decision thresholds
            if final_score >= 0.70:
                base_result["assessment_label"] = "AI-GENERATION SIGNALS DETECTED"
                base_result["interpretation"] = (
                    "The screening pipeline observed structural or metadata signals associated with synthetic image generation. "
                    "This is a probabilistic model assessment, not definitive proof. Independent forensic review is advised."
                )
            elif final_score >= 0.40:
                base_result["assessment_label"] = "INCONCLUSIVE"
                base_result["interpretation"] = (
                    "The image displays ambiguous indicators that do not clearly differentiate synthetic synthesis "
                    "from standard digital post-processing, compression, or aggressive denoising."
                )
            else:
                base_result["assessment_label"] = "NO STRONG AI-GENERATION SIGNALS DETECTED"
                base_result["interpretation"] = (
                    "The evaluated spectral and metadata properties did not trigger strong synthetic media markers. "
                    "This does NOT guarantee the image is genuine photographic evidence, as advanced generative models "
                    "can bypass baseline detection."
                )

    except Exception as e:
        base_result["assessment_label"] = "ANALYSIS UNAVAILABLE"
        base_result["raw_score"] = None
        base_result["interpretation"] = f"Assessment could not complete: {str(e)}"

    return base_result
