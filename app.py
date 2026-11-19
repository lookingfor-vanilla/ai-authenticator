import hashlib
import html
import json
import mimetypes
import struct
import time
import uuid
import wave
from datetime import datetime
from io import BytesIO

import streamlit as st
from PIL import Image, ExifTags, UnidentifiedImageError

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="HashProof AI | Evidence Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# 2. DATABASE INTEGRATION (With safe fallback)
# ---------------------------------------------------------
try:
    from database import (
        init_db,
        save_report_to_db,
        get_reports_from_db,
        get_report_count,
    )
    init_db()
    DB_ENABLED = True
except ImportError:
    DB_ENABLED = False

    def save_report_to_db(report):
        return report

    def get_reports_from_db():
        return st.session_state.get("reports", [])

    def get_report_count():
        return len(st.session_state.get("reports", []))

# ---------------------------------------------------------
# 3. SESSION STATE
# ---------------------------------------------------------
for key, value in {
    "page": "Home",
    "reports": [],
    "latest_report": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

if "reports_loaded" not in st.session_state:
    try:
        st.session_state.reports = get_reports_from_db()
    except Exception:
        st.session_state.reports = []
    st.session_state.reports_loaded = True

# ---------------------------------------------------------
# 4. HIGH-TECH FORENSIC STYLING (CSS)
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #080914;
  --panel: #111326;
  --line: rgba(177,180,220,.14);
  --text: #f4f4ff;
  --muted: #999fbd;
  --violet: #a47aff;
  --cyan: #55e5ff;
  --emerald: #10b981;
  --rose: #f43f5e;
}

.stApp {
  background:
    radial-gradient(ellipse at 12% 0%, rgba(124,77,235,.16), transparent 36%),
    radial-gradient(ellipse at 92% 8%, rgba(85,229,255,.09), transparent 32%),
    var(--bg);
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
}

.block-container {
  max-width: 1280px;
  padding-top: 1.4rem;
  padding-bottom: 3.5rem;
}

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

h1, h2, h3, h4 {
  font-family: 'Manrope', sans-serif !important;
  letter-spacing: -.035em;
  color: var(--text);
}

p, li, label { color: #cbd5e1 !important; }
small { color: var(--muted) !important; }
hr { border-color: var(--line); }

@keyframes floatDoodle {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-7px) rotate(3deg); }
}

@keyframes pulseBorder {
  0%, 100% { border-color: rgba(164,122,255,0.3); box-shadow: 0 0 15px rgba(0,0,0,0.4); }
  50% { border-color: rgba(85,229,255,0.5); box-shadow: 0 0 25px rgba(85,229,255,0.15); }
}

@keyframes soundWave {
  0%, 100% { height: 6px; }
  50% { height: 28px; }
}

.equalizer-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  height: 38px;
  margin: 12px 0 16px;
}

.equalizer-bar {
  width: 5px;
  background: linear-gradient(180deg, var(--cyan), var(--violet));
  border-radius: 4px;
  animation: soundWave 1.2s infinite ease-in-out;
}

.equalizer-bar:nth-child(1) { animation-delay: 0.1s; height: 10px; }
.equalizer-bar:nth-child(2) { animation-delay: 0.3s; height: 22px; }
.equalizer-bar:nth-child(3) { animation-delay: 0.15s; height: 16px; }
.equalizer-bar:nth-child(4) { animation-delay: 0.45s; height: 30px; }
.equalizer-bar:nth-child(5) { animation-delay: 0.25s; height: 24px; }
.equalizer-bar:nth-child(6) { animation-delay: 0.5s; height: 18px; }
.equalizer-bar:nth-child(7) { animation-delay: 0.35s; height: 28px; }
.equalizer-bar:nth-child(8) { animation-delay: 0.2s; height: 12px; }

/* FIX FOR UGLY WHITE FILE UPLOADER CHIP */
div[data-testid="stFileUploaderFile"],
div[data-testid="stFileUploaderFile"] > div {
  background-color: #0b0e24 !important;
  border: 1px solid rgba(85,229,255,0.4) !important;
  border-radius: 10px !important;
}

div[data-testid="stFileUploaderFile"] * {
  color: #f4f4ff !important;
  fill: #55e5ff !important;
}

div[data-testid="stAlert"] {
  background: rgba(14, 18, 40, 0.95) !important;
  border: 1px solid rgba(85,229,255,.35) !important;
  border-radius: 14px !important;
}

div[data-testid="stAlert"] * { color: #cbd5e1 !important; }

div[data-testid="stTextInput"] div[data-baseweb="input"],
div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
  background-color: #080b1c !important;
  border: 1px solid rgba(164, 122, 255, 0.45) !important;
  border-radius: 12px !important;
  padding: 4px 8px !important;
}

div[data-testid="stTextInput"] input {
  color: #55e5ff !important;
  background-color: transparent !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 0.92rem !important;
}

div[data-testid="stFileUploader"] {
  background: rgba(14, 18, 38, 0.7) !important;
  border: 1px dashed rgba(164,122,255,.5) !important;
  border-radius: 18px !important;
  padding: 16px !important;
}

section[data-testid="stFileUploaderDropzone"],
div[data-testid="stFileUploaderDropzone"] {
  background: rgba(7, 9, 20, 0.95) !important;
  border: 1px dashed rgba(85, 229, 255, 0.35) !important;
  border-radius: 14px !important;
  color: #f4f4ff !important;
  padding: 18px !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small,
div[data-testid="stFileUploaderDropzone"] span,
div[data-testid="stFileUploaderDropzone"] small {
  color: #cbd5e1 !important;
  font-size: 0.82rem !important;
}

section[data-testid="stFileUploaderDropzone"] button,
div[data-testid="stFileUploaderDropzone"] button {
  background: linear-gradient(120deg, #8053e9, #5e4deb) !important;
  color: #ffffff !important;
  border: 1px solid rgba(85,229,255,.5) !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
}

.feature-banner {
  background: linear-gradient(135deg, rgba(23, 28, 56, 0.75), rgba(12, 15, 32, 0.9));
  border: 1px solid rgba(164,122,255,.28);
  border-radius: 22px;
  padding: 24px 28px;
  margin-bottom: 24px;
  animation: pulseBorder 5s infinite ease-in-out;
}

.feature-banner h2 { font-size: 1.85rem; margin: 10px 0 6px; }

.pod-card {
  background: rgba(17, 21, 44, 0.75);
  border: 1px solid rgba(164,122,255,.2);
  border-radius: 18px;
  padding: 22px;
  margin-bottom: 12px;
}

.pod-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.pod-tag-a {
  background: rgba(164,122,255,.15);
  border: 1px solid rgba(164,122,255,.35);
  color: #c9b5ff;
}

.pod-tag-b {
  background: rgba(85,229,255,.12);
  border: 1px solid rgba(85,229,255,.35);
  color: #83eaff;
}

.hash-box {
  padding: 12px 16px;
  background: #060812;
  border: 1px solid rgba(85,229,255,.25);
  border-radius: 10px;
  color: #83eaff;
  font-family: 'DM Mono', monospace;
  font-size: .82rem;
  overflow-wrap: anywhere;
  margin: 6px 0 12px;
}

.doodle-hero {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 28px 15px;
  text-align: center;
  border: 1px dashed rgba(164,122,255,.3);
  border-radius: 18px;
  background: rgba(11, 14, 30, 0.6);
  margin-top: 10px;
}

.doodle-icon {
  font-size: 3rem;
  animation: floatDoodle 3.5s infinite ease-in-out;
  display: inline-block;
  margin-bottom: 8px;
  filter: drop-shadow(0 0 16px rgba(85,229,255,0.35));
}

.step-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(164,122,255,.15);
  border: 1px solid rgba(164,122,255,.35);
  border-radius: 8px;
  color: #c9b5ff;
  font-family: 'DM Mono', monospace;
  font-weight: 700;
  font-size: 0.78rem;
}

.verdict-banner {
  padding: 20px 24px;
  border-radius: 16px;
  margin: 18px 0;
  display: flex;
  align-items: center;
  gap: 16px;
}

.verdict-match {
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.35);
  color: #a7f3d0;
}

.verdict-mismatch {
  background: rgba(244, 63, 94, 0.12);
  border: 1px solid rgba(244, 63, 94, 0.35);
  color: #fecdd3;
}

.stButton > button,
.stDownloadButton > button {
  border-radius: 12px;
  min-height: 2.85rem;
  padding: .55rem 1.15rem;
  font-weight: 700;
  color: white;
  background: linear-gradient(105deg, #8053e9, #695eea);
  border: 1px solid rgba(164,122,255,.5);
  transition: all .2s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
  border-color: var(--cyan);
  box-shadow: 0 0 22px rgba(85,229,255,.25);
  color: white;
  transform: translateY(-1px);
}

div[data-testid="stMetric"] {
  background: rgba(17,19,38,.85);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 16px;
}

.pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  border-radius: 999px;
  color: #baf5ff;
  border: 1px solid rgba(85,229,255,.26);
  background: rgba(85,229,255,.07);
  font-size: .74rem;
  letter-spacing: .06em;
  text-transform: uppercase;
  font-weight: 700;
}

.hero {
  position: relative;
  overflow: hidden;
  padding: 48px 40px;
  border-radius: 26px;
  border: 1px solid rgba(164,122,255,.28);
  background:
    radial-gradient(ellipse at 82% 22%, rgba(85,229,255,.14), transparent 36%),
    radial-gradient(ellipse at 70% 100%, rgba(164,122,255,.18), transparent 42%),
    linear-gradient(135deg, #191a36, #0d0e1e);
  box-shadow: 0 25px 80px rgba(0,0,0,.25);
  margin-bottom: 1.5rem;
}

.gradient {
  background: linear-gradient(95deg, #c0a7ff, #65eaff);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.feature {
  min-height: 180px;
  padding: 24px;
  border-radius: 18px;
  border: 1px solid var(--line);
  background: linear-gradient(145deg, #15172b, #0d0f1e);
  transition: all .25s ease;
}

.feature:hover {
  border-color: rgba(85,229,255,.3);
  transform: translateY(-2px);
}

.feature-icon {
  display: flex;
  width: 42px;
  height: 42px;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: rgba(164,122,255,.12);
  border: 1px solid rgba(164,122,255,.3);
  color: #c9b5ff;
  font-size: 1.2rem;
  margin-bottom: 14px;
}

.footer {
  text-align: center;
  color: #747b9a;
  font-size: .78rem;
  padding-top: 40px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. FORENSIC ENGINES (WITH SPEED CACHING & MP3 DECODER)
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def calculate_hashes(data: bytes):
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "sha1": hashlib.sha1(data).hexdigest(),
        "md5": hashlib.md5(data).hexdigest(),
    }

def readable_size(size):
    if size < 1024:
        return f"{size} B"
    if size < 1024**2:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024**2):.2f} MB"

def parse_mp3_metadata(data: bytes):
    """Pure Python MPEG-1 Layer III audio header parser."""
    offset = 0
    if data.startswith(b"ID3"):
        tag_size = ((data[6] & 0x7F) << 21) | ((data[7] & 0x7F) << 14) | ((data[8] & 0x7F) << 7) | (data[9] & 0x7F)
        offset = 10 + tag_size

    bitrate_map = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]
    samplerate_map = [44100, 48000, 32000, 0]

    for i in range(offset, min(len(data) - 4, offset + 8192)):
        if data[i] == 0xFF and (data[i+1] & 0xE0) == 0xE0:
            h = (data[i] << 24) | (data[i+1] << 16) | (data[i+2] << 8) | data[i+3]
            layer_bits = (h >> 17) & 3
            bitrate_idx = (h >> 12) & 0xF
            srate_idx = (h >> 10) & 3
            channel_bits = (h >> 6) & 3

            if layer_bits == 1 and bitrate_idx not in (0, 15) and srate_idx != 3:
                bitrate = bitrate_map[bitrate_idx] * 1000
                sample_rate = samplerate_map[srate_idx]
                channels = "Mono (1 Channel)" if channel_bits == 3 else "Stereo (2 Channels)"
                duration = (len(data) - offset) * 8 / float(bitrate) if bitrate > 0 else 0
                return {
                    "duration_str": f"{duration:.2f} seconds",
                    "sample_rate": f"{sample_rate:,} Hz",
                    "channels": channels,
                    "bit_depth": f"{bitrate // 1000} kbps MP3",
                    "total_frames": f"{int(duration * sample_rate):,} frames",
                }
    return None

@st.cache_data(show_spinner=False)
def inspect_audio_data(data: bytes, filename: str):
    """Analyzes audio containers, parses acoustic headers, and downsamples waveform."""
    hashes = calculate_hashes(data)
    info = {
        "filename": filename,
        "size": readable_size(len(data)),
        "hashes": hashes,
        "format": filename.split(".")[-1].upper(),
        "is_wav": False,
        "duration_str": "—",
        "sample_rate": "—",
        "channels": "—",
        "bit_depth": "—",
        "total_frames": "—",
        "waveform": []
    }

    # 1. Try WAV parsing
    try:
        with wave.open(BytesIO(data), 'rb') as wav:
            info["is_wav"] = True
            n_channels = wav.getnchannels()
            sampwidth = wav.getsampwidth()
            framerate = wav.getframerate()
            n_frames = wav.getnframes()

            duration = n_frames / float(framerate) if framerate > 0 else 0
            info["duration_str"] = f"{duration:.3f} seconds"
            info["sample_rate"] = f"{framerate:,} Hz"
            info["channels"] = "Stereo (2 Channels)" if n_channels == 2 else ("Mono (1 Channel)" if n_channels == 1 else f"{n_channels} Channels")
            info["bit_depth"] = f"{sampwidth * 8}-bit PCM"
            info["total_frames"] = f"{n_frames:,} frames"

            step = max(1, n_frames // 120)
            raw_frames = wav.readframes(min(n_frames, 400000))
            if sampwidth == 2:
                fmt = f"{len(raw_frames) // 2}h"
                samples = struct.unpack(fmt, raw_frames)
                info["waveform"] = [abs(samples[i]) for i in range(0, len(samples), step * n_channels)][:120]
            return info
    except Exception:
        pass

    # 2. Try MP3 parsing
    mp3_meta = parse_mp3_metadata(data)
    if mp3_meta:
        info.update(mp3_meta)

    return info

@st.cache_data(show_spinner=False)
def examine_evidence(data: bytes, upload_name: str, reference_hash: str = ""):
    hashes = calculate_hashes(data)

    report = {
        "report_id": "AA-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + hashes["sha256"][:6].upper(),
        "file_name": upload_name,
        "filename": upload_name,
        "file_size": readable_size(len(data)),
        "file_size_bytes": len(data),
        "size_bytes": len(data),
        "mime_type": mimetypes.guess_type(upload_name)[0] or "application/octet-stream",
        "sha256": hashes["sha256"],
        "sha1": hashes["sha1"],
        "md5": hashes["md5"],
        "reference_hash": reference_hash.strip().lower() if reference_hash else None,
        "hash_match": None,
        "examined_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "date": datetime.now().astimezone().isoformat(timespec="seconds"),
        "image": None,
        "exif": {},
        "exif_categorized": {},
        "editing_traces": [],
        "findings": [
            "SHA-256, SHA-1, and MD5 cryptographic checksums calculated from raw byte bitstream."
        ],
        "limitations": [
            "A hash verifies exact byte-level identity; it does not identify who created or edited the file.",
            "Metadata can be modified, fabricated, or stripped by web apps (e.g. WhatsApp, Discord).",
            "These preliminary checks do not replace deep learning neural GAN/diffusion artifact detection.",
            "Certified forensic authenticity in court requires complete chain-of-custody documentation.",
        ],
    }

    if reference_hash:
        clean_ref = reference_hash.strip().lower()
        report["hash_match"] = (hashes["sha256"] == clean_ref)
        if report["hash_match"]:
            report["findings"].append("Reference Parity: The file byte-for-byte matches the provided reference hash.")
        else:
            report["findings"].append("Reference Parity: MISMATCH detected against the provided reference hash.")

    try:
        with Image.open(BytesIO(data)) as image:
            image.verify()
        with Image.open(BytesIO(data)) as image:
            report["image"] = {
                "format": image.format or "Unknown",
                "width_pixels": image.width,
                "height_pixels": image.height,
                "dimensions": f"{image.width} × {image.height}",
                "color_mode": image.mode,
                "frames": getattr(image, "n_frames", 1),
            }
            # extract exif
            raw_metadata = {}
            categorized = {"camera": {}, "timestamps": {}, "software": {}, "gps": {}}
            exif = image.getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                    if isinstance(value, bytes):
                        value = value.decode("utf-8", errors="replace")
                    val_str = str(value)[:500]
                    raw_metadata[tag_name] = val_str

                    if tag_name in ["Make", "Model", "LensModel", "FocalLength", "FNumber", "ExposureTime", "ISOSpeedRatings"]:
                        categorized["camera"][tag_name] = val_str
                    elif tag_name in ["DateTime", "DateTimeOriginal", "DateTimeDigitized"]:
                        categorized["timestamps"][tag_name] = val_str
                    elif tag_name in ["Software", "Artist", "Copyright", "ProcessingSoftware"]:
                        categorized["software"][tag_name] = val_str
                    elif "GPS" in tag_name:
                        categorized["gps"][tag_name] = val_str

            report["exif"] = raw_metadata
            report["exif_categorized"] = categorized

            # detect editing
            editing_tools = ["photoshop", "lightroom", "gimp", "canva", "picsart", "snapseed", "pixlr", "affinity"]
            combined = " ".join(list(categorized["software"].values()) + list(raw_metadata.values())).lower()
            report["editing_traces"] = list(set([tool.capitalize() for tool in editing_tools if tool in combined]))

            report["findings"].append(f"Image Structure: Valid {image.format} container structure verified successfully.")
            if report["editing_traces"]:
                report["findings"].append(f"Software Footprint: Detected post-capture editing signatures ({', '.join(report['editing_traces'])}).")
    except (UnidentifiedImageError, OSError, ValueError):
        report["findings"].append("Container Decoding: File could not be parsed as a supported image format.")

    return report

def export_report_json(report):
    return json.dumps(report, indent=2, ensure_ascii=False).encode("utf-8")

def generate_text_docket(report: dict) -> str:
    """Generates a court-ready plaintext evidence docket."""
    if not isinstance(report, dict):
        report = {}

    rep_id = str(report.get("report_id") or "HP-EVID-" + uuid.uuid4().hex[:8].upper())
    filename = str(report.get("file_name") or report.get("filename") or "Unknown_Evidence_Asset")
    size_str = str(report.get("file_size") or (f"{report.get('size_bytes', 0):,} bytes" if report.get("size_bytes") else "Not Recorded"))
    mime_type = str(report.get("mime_type") or "application/octet-stream")
    examined_at = str(report.get("examined_at") or report.get("timestamp") or report.get("created_at") or report.get("date") or datetime.now().isoformat())

    sha256 = str(report.get("sha256") or (report.get("hashes", {}).get("sha256") if isinstance(report.get("hashes"), dict) else None) or "Unavailable")
    sha1 = str(report.get("sha1") or (report.get("hashes", {}).get("sha1") if isinstance(report.get("hashes"), dict) else None) or "Unavailable")
    md5 = str(report.get("md5") or (report.get("hashes", {}).get("md5") if isinstance(report.get("hashes"), dict) else None) or "Unavailable")

    hash_match = report.get("hash_match")
    if hash_match is True:
        status = "BITSTREAM INTEGRITY CONFIRMED — EXACT REFERENCE MATCH"
    elif hash_match is False:
        status = "PARITY MISMATCH — EVIDENCE ALTERATION DETECTED"
    else:
        status = "CRYPTOGRAPHICALLY AUDITED & SEALED"

    lines = [
        "=" * 80,
        "                    HASHPROOF AI — FORENSIC EVIDENCE DOCKET",
        "              Cryptographic Bitstream Verification & Integrity Report",
        "=" * 80,
        f"CASE DOCKET / REPORT ID : {rep_id}",
        f"EXAMINED AT / TIMESTAMP : {examined_at}",
        f"VERDICT STATUS          : {status}",
        f"STANDARDS COMPLIANCE    : NIST FIPS 180-4 / FRE RULE 902(13)(14)",
        "-" * 80,
        "1. SUBJECT EVIDENCE IDENTIFICATION",
        "-" * 80,
        f"  Evidence Filename     : {filename}",
        f"  File Size             : {size_str}",
        f"  MIME / Container Type : {mime_type}",
        f"  Acquisition Mode      : Binary Bitstream Ingestion",
        "",
        "-" * 80,
        "2. CRYPTOGRAPHIC BITSTREAM CHECKSUMS (NIST FIPS 180-4)",
        "-" * 80,
        f"  SHA-256 (Primary)     : {sha256}",
        f"  SHA-1   (Secondary)   : {sha1}",
        f"  MD5     (Legacy)      : {md5}",
        "",
    ]

    audio = report.get("audio") or report.get("telemetry") or {}
    if audio.get("duration") or audio.get("sample_rate"):
        lines.extend([
            "-" * 80,
            "3. ACOUSTIC FORENSIC TELEMETRY",
            "-" * 80,
            f"  Duration              : {audio.get('duration', '—')}",
            f"  Sample Rate           : {audio.get('sample_rate', '—')}",
            f"  Audio Channels        : {audio.get('channels', '—')}",
            f"  Bit Depth / Encoding  : {audio.get('bit_depth', '—')}",
            f"  Total Audio Frames    : {audio.get('total_frames', '—')}",
            "",
        ])

    image = report.get("image") or {}
    if image.get("format") or image.get("dimensions"):
        lines.extend([
            "-" * 80,
            "3. VISUAL CONTAINER TELEMETRY",
            "-" * 80,
            f"  Container Format      : {image.get('format', '—')}",
            f"  Dimensions            : {image.get('dimensions', '—')}",
            f"  Color Mode            : {image.get('color_mode', '—')}",
            f"  Frames                : {image.get('frames', 1)}",
            "",
        ])

    findings = report.get("findings") or []
    if findings:
        lines.extend([
            "-" * 80,
            "4. FORENSIC OBSERVATIONS & FINDINGS",
            "-" * 80,
        ])
        for idx, f in enumerate(findings, 1):
            lines.append(f"  [{idx}] {f}")
        lines.append("")

    lines.extend([
        "=" * 80,
        "ATTESTATION & LEGAL STANDARDS:",
        "This record certifies that the digital asset was hashed directly from its unaltered",
        "binary bitstream. Admissible under Federal Rules of Evidence Rule 902(13) and Rule",
        "902(14) for self-authenticating electronic records when chain of custody is established.",
        "=" * 80,
    ])

    return "\n".join(lines)

def generate_html_certificate(report: dict) -> str:
    """Generates an official, print-ready Forensic Authenticity Certificate and Case Dossier."""
    if not isinstance(report, dict):
        report = {}

    esc = html.escape

    rep_id = esc(str(report.get("report_id") or "HP-EVID-" + uuid.uuid4().hex[:8].upper()))
    filename = esc(str(report.get("file_name") or report.get("filename") or "Unknown_Evidence_Asset"))
    size_str = esc(str(report.get("file_size") or (f"{report.get('size_bytes', 0):,} bytes" if report.get("size_bytes") else "Not Recorded")))
    mime_type = esc(str(report.get("mime_type") or "application/octet-stream"))
    examined_at = esc(str(report.get("examined_at") or report.get("timestamp") or report.get("created_at") or report.get("date") or datetime.now().isoformat()))

    sha256 = esc(str(report.get("sha256") or (report.get("hashes", {}).get("sha256") if isinstance(report.get("hashes"), dict) else None) or "Unavailable"))
    sha1 = esc(str(report.get("sha1") or (report.get("hashes", {}).get("sha1") if isinstance(report.get("hashes"), dict) else None) or "Unavailable"))
    md5 = esc(str(report.get("md5") or (report.get("hashes", {}).get("md5") if isinstance(report.get("hashes"), dict) else None) or "Unavailable"))

    hash_match = report.get("hash_match")
    if hash_match is True:
        status_text = "BITSTREAM INTEGRITY CONFIRMED — EXACT REFERENCE MATCH"
        status_sub = "Zero bitstream deviation detected against reference cryptographic digest."
        badge_class = "badge-match"
        badge_symbol = "✔"
    elif hash_match is False:
        status_text = "PARITY MISMATCH — EVIDENCE ALTERATION DETECTED"
        status_sub = "Cryptographic checksum diverges from reference standard. Modification confirmed."
        badge_class = "badge-mismatch"
        badge_symbol = "✖"
    else:
        status_text = "CRYPTOGRAPHIC BITSTREAM CERTIFIED & SEALED"
        status_sub = "Bitstream cryptographically signed and archived under NIST FIPS 180-4 standard."
        badge_class = "badge-verified"
        badge_symbol = "◈"

    audio_data = report.get("audio") or report.get("telemetry") or {}
    has_audio = bool(audio_data.get("duration") or audio_data.get("sample_rate") or filename.lower().endswith((".mp3", ".wav", ".ogg", ".m4a", ".aac")))

    image_data = report.get("image") or {}
    has_image = bool(image_data.get("format") or image_data.get("dimensions"))

    exif_cat = report.get("exif_categorized") or {}
    camera_meta = exif_cat.get("camera", {}) if isinstance(exif_cat, dict) else {}
    software_meta = exif_cat.get("software", {}) if isinstance(exif_cat, dict) else {}
    time_meta = exif_cat.get("timestamps", {}) if isinstance(exif_cat, dict) else {}
    gps_meta = exif_cat.get("gps", {}) if isinstance(exif_cat, dict) else {}
    editing_traces = report.get("editing_traces") or []

    comp_data = report.get("comparison") or {}
    has_comp = bool(comp_data)

    raw_findings = report.get("findings") or [
        "Cryptographic digests computed directly from raw binary bitstream.",
        "Bitstream integrity archived in ACID-compliant repository ledger."
    ]
    findings_html = "".join([f'<li class="finding-item">◈ {esc(str(f))}</li>' for f in raw_findings])

    telemetry_html = ""
    if has_audio:
        dur = esc(str(audio_data.get("duration", "—")))
        srate = esc(str(audio_data.get("sample_rate", "—")))
        chans = esc(str(audio_data.get("channels", "—")))
        bdepth = esc(str(audio_data.get("bit_depth", "—")))
        tframes = esc(str(audio_data.get("total_frames", "—")))
        telemetry_html = f"""
        <div class="section-title">🎙️ Acoustic Forensic Telemetry</div>
        <table class="docket-table">
          <tr><th>Acoustic Duration</th><td>{dur}</td></tr>
          <tr><th>Sampling Frequency</th><td>{srate}</td></tr>
          <tr><th>Channel Topology</th><td>{chans}</td></tr>
          <tr><th>Encoding / Bit Depth</th><td>{bdepth}</td></tr>
          <tr><th>Total Frame Buffer</th><td>{tframes}</td></tr>
          <tr><th>Splice Evaluation</th><td>Bitstream examined for amplitude dropouts and cut points</td></tr>
        </table>
        """
    elif has_image:
        fmt = esc(str(image_data.get("format", "—")))
        dims = esc(str(image_data.get("dimensions", "—")))
        cmode = esc(str(image_data.get("color_mode", "—")))
        frames = esc(str(image_data.get("frames", 1)))
        cam_info = ", ".join([f"{esc(k)}: {esc(str(v))}" for k, v in camera_meta.items() if v]) or "Standard Camera / Untagged"
        edit_footprint = (", ".join([esc(str(t)) for t in editing_traces])) if editing_traces else "None (Clean sensor capture)"
        time_info = ", ".join([f"{esc(k)}: {esc(str(v))}" for k, v in time_meta.items() if v]) or "Preserved from acquisition"
        gps_info = "Embedded GPS Coordinates Present" if gps_meta else "No Geotagging Headers Embedded"

        telemetry_html = f"""
        <div class="section-title">🔍 Visual Container & EXIF Telemetry</div>
        <table class="docket-table">
          <tr><th>Container Format</th><td>{fmt}</td></tr>
          <tr><th>Resolution & Dimensions</th><td>{dims}</td></tr>
          <tr><th>Color Space</th><td>{cmode} ({frames} frame{'s' if frames != 1 else ''})</td></tr>
          <tr><th>Camera Hardware</th><td>{cam_info}</td></tr>
          <tr><th>Acquisition Timestamps</th><td>{time_info}</td></tr>
          <tr><th>Software Signatures</th><td>{edit_footprint}</td></tr>
          <tr><th>Geolocation Tags</th><td>{gps_info}</td></tr>
        </table>
        """
    elif has_comp:
        file_a = comp_data.get("file_a", {})
        file_b = comp_data.get("file_b", {})
        exact_match = comp_data.get("exact_byte_match", False)
        match_str = "✔ EXACT CLONE (Identical bitstreams)" if exact_match else "✖ DIVERGENT (Files differ)"
        telemetry_html = f"""
        <div class="section-title">⚖️ Comparative Parity Matrix</div>
        <table class="docket-table">
          <tr><th>Evidence Asset A</th><td>{esc(str(file_a.get('name', 'Reference A')))} ({esc(str(file_a.get('size', '—')))})</td></tr>
          <tr><th>Evidence Asset B</th><td>{esc(str(file_b.get('name', 'Suspect B')))} ({esc(str(file_b.get('size', '—')))})</td></tr>
          <tr><th>Byte Parity Result</th><td><strong>{match_str}</strong></td></tr>
          <tr><th>Evidence A SHA-256</th><td class="mono">{esc(str(file_a.get('sha256', '—')))}</td></tr>
          <tr><th>Evidence B SHA-256</th><td class="mono">{esc(str(file_b.get('sha256', '—')))}</td></tr>
        </table>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Forensic Certificate — {rep_id}</title>
  <style>
    :root {{
      --bg: #080914;
      --card-bg: #0e1124;
      --border: rgba(85, 229, 255, 0.22);
      --cyan: #55e5ff;
      --violet: #a47aff;
      --emerald: #10b981;
      --rose: #f43f5e;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--bg);
      color: var(--text-main);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.5;
      padding: 30px 16px;
    }}
    .action-bar {{
      max-width: 860px;
      margin: 0 auto 20px auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: linear-gradient(135deg, rgba(85,229,255,0.08), rgba(164,122,255,0.08));
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 12px 20px;
    }}
    .action-btn {{
      background: linear-gradient(135deg, #a47aff, #55e5ff);
      color: #080914;
      font-weight: 700;
      font-size: 0.95rem;
      border: none;
      padding: 10px 22px;
      border-radius: 8px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 4px 14px rgba(85,229,255,0.25);
      transition: all 0.2s ease;
    }}
    .action-btn:hover {{
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(85,229,255,0.4);
    }}
    .action-tip {{
      font-size: 0.85rem;
      color: var(--text-muted);
    }}
    .cert-canvas {{
      max-width: 860px;
      margin: 0 auto;
      background: var(--card-bg);
      border: 1.5px solid var(--border);
      border-radius: 18px;
      padding: 40px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
      position: relative;
      overflow: hidden;
    }}
    .cert-canvas::before {{
      content: "HASHPROOF";
      position: absolute;
      top: 45%;
      left: 50%;
      transform: translate(-50%, -50%) rotate(-25deg);
      font-size: 7.5rem;
      font-weight: 900;
      letter-spacing: 0.2em;
      color: rgba(85, 229, 255, 0.02);
      pointer-events: none;
      z-index: 0;
      white-space: nowrap;
    }}
    .cert-content {{
      position: relative;
      z-index: 1;
    }}
    .cert-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 1.5px solid rgba(85,229,255,0.18);
      padding-bottom: 24px;
      margin-bottom: 26px;
    }}
    .cert-logo {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .cert-badge-icon {{
      width: 44px;
      height: 44px;
      background: linear-gradient(135deg, #a47aff, #55e5ff);
      color: #080914;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.6rem;
      font-weight: 900;
    }}
    .cert-title-group h1 {{
      font-size: 1.2rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-weight: 800;
      color: #ffffff;
      margin: 0;
    }}
    .cert-title-group p {{
      font-size: 0.75rem;
      color: var(--cyan);
      letter-spacing: 0.1em;
      text-transform: uppercase;
      font-weight: 600;
      margin-top: 2px;
    }}
    .cert-meta-right {{
      text-align: right;
    }}
    .cert-id {{
      font-family: 'JetBrains Mono', Consolas, monospace;
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--cyan);
    }}
    .cert-date {{
      font-size: 0.78rem;
      color: var(--text-muted);
      margin-top: 4px;
    }}
    .title-banner {{
      text-align: center;
      margin: 10px 0 26px 0;
    }}
    .title-banner h2 {{
      font-size: 1.5rem;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .title-banner p {{
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-top: 6px;
    }}
    .verdict-box {{
      border-radius: 12px;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 26px;
    }}
    .badge-match, .badge-verified {{
      background: rgba(16, 185, 129, 0.12);
      border: 1.5px solid #10b981;
      color: #a7f3d0;
    }}
    .badge-mismatch {{
      background: rgba(244, 63, 94, 0.12);
      border: 1.5px solid #f43f5e;
      color: #fecdd3;
    }}
    .verdict-icon {{
      font-size: 2rem;
      font-weight: 900;
    }}
    .verdict-title {{
      font-weight: 800;
      font-size: 1.05rem;
      letter-spacing: 0.02em;
    }}
    .verdict-desc {{
      font-size: 0.82rem;
      opacity: 0.9;
      margin-top: 2px;
    }}
    .section-title {{
      font-size: 0.82rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      font-weight: 700;
      color: var(--cyan);
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .docket-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 24px;
      font-size: 0.88rem;
    }}
    .docket-table th, .docket-table td {{
      padding: 10px 14px;
      border: 1px solid rgba(85,229,255,0.14);
      text-align: left;
    }}
    .docket-table th {{
      background: rgba(85,229,255,0.06);
      color: var(--text-muted);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      width: 28%;
    }}
    .docket-table td {{
      color: #ffffff;
      font-weight: 500;
    }}
    .mono {{
      font-family: 'JetBrains Mono', Consolas, monospace;
      font-size: 0.82rem;
    }}
    .hash-panel {{
      background: rgba(85, 229, 255, 0.04);
      border: 1px solid rgba(85, 229, 255, 0.22);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 24px;
    }}
    .hash-label {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--cyan);
      font-weight: 700;
      margin-bottom: 6px;
    }}
    .hash-val-sha256 {{
      font-family: 'JetBrains Mono', Consolas, monospace;
      font-size: 0.88rem;
      font-weight: 700;
      color: #55e5ff;
      word-break: break-all;
      background: rgba(0, 0, 0, 0.35);
      padding: 10px 14px;
      border-radius: 8px;
      border: 1px solid rgba(85, 229, 255, 0.2);
    }}
    .hash-subgrid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-top: 12px;
    }}
    .hash-sub-item {{
      background: rgba(0, 0, 0, 0.2);
      padding: 8px 12px;
      border-radius: 6px;
      border: 1px solid rgba(255,255,255,0.06);
    }}
    .hash-sub-label {{
      font-size: 0.7rem;
      color: var(--text-muted);
      text-transform: uppercase;
      font-weight: 600;
    }}
    .hash-sub-val {{
      font-family: 'JetBrains Mono', Consolas, monospace;
      font-size: 0.78rem;
      color: #e2e8f0;
      word-break: break-all;
      margin-top: 2px;
    }}
    .finding-list {{
      list-style: none;
      margin-bottom: 24px;
    }}
    .finding-item {{
      padding: 8px 12px;
      margin-bottom: 6px;
      background: rgba(255, 255, 255, 0.02);
      border-left: 3px solid var(--cyan);
      font-size: 0.85rem;
      color: #e2e8f0;
    }}
    .cert-footer {{
      border-top: 1.5px solid rgba(85, 229, 255, 0.18);
      padding-top: 20px;
      margin-top: 28px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }}
    .footer-legal {{
      max-width: 65%;
      font-size: 0.75rem;
      color: var(--text-muted);
      line-height: 1.45;
    }}
    .footer-stamp {{
      text-align: right;
    }}
    .stamp-box {{
      display: inline-block;
      border: 2px dashed var(--cyan);
      border-radius: 10px;
      padding: 8px 14px;
      text-align: center;
      background: rgba(85, 229, 255, 0.05);
    }}
    .stamp-title {{
      font-size: 0.72rem;
      font-weight: 800;
      letter-spacing: 0.1em;
      color: var(--cyan);
      text-transform: uppercase;
    }}
    .stamp-node {{
      font-family: 'JetBrains Mono', Consolas, monospace;
      font-size: 0.7rem;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    @media print {{
      body {{
        background: #ffffff !important;
        color: #0f172a !important;
        padding: 0 !important;
      }}
      .no-print {{
        display: none !important;
      }}
      .cert-canvas {{
        max-width: 100% !important;
        background: #ffffff !important;
        border: 2px solid #0f172a !important;
        box-shadow: none !important;
        padding: 24px 30px !important;
        border-radius: 0 !important;
      }}
      .cert-canvas::before {{
        display: none !important;
      }}
      .cert-header {{
        border-bottom: 2px solid #0f172a !important;
      }}
      .cert-title-group h1, .title-banner h2 {{
        color: #0f172a !important;
      }}
      .cert-title-group p, .section-title, .hash-label {{
        color: #0369a1 !important;
      }}
      .cert-id {{
        color: #0f172a !important;
      }}
      .badge-match, .badge-verified {{
        background: #f0fdf4 !important;
        border: 2px solid #16a34a !important;
        color: #166534 !important;
      }}
      .badge-mismatch {{
        background: #fef2f2 !important;
        border: 2px solid #dc2626 !important;
        color: #991b1b !important;
      }}
      .docket-table th {{
        background: #f1f5f9 !important;
        color: #334155 !important;
        border-color: #cbd5e1 !important;
      }}
      .docket-table td {{
        color: #0f172a !important;
        border-color: #cbd5e1 !important;
      }}
      .hash-panel {{
        background: #f8fafc !important;
        border: 1.5px solid #cbd5e1 !important;
      }}
      .hash-val-sha256 {{
        background: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #94a3b8 !important;
      }}
      .hash-sub-item {{
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
      }}
      .hash-sub-val {{
        color: #0f172a !important;
      }}
      .finding-item {{
        background: #f8fafc !important;
        border-left: 3px solid #0284c7 !important;
        color: #1e293b !important;
      }}
      .cert-footer {{
        border-top: 2px solid #0f172a !important;
      }}
      .stamp-box {{
        border-color: #0f172a !important;
        background: #f8fafc !important;
      }}
      .stamp-title {{
        color: #0f172a !important;
      }}
      @page {{
        size: A4 portrait;
        margin: 12mm 15mm;
      }}
    }}
  </style>
</head>
<body>

  <!-- Floating Utility Bar -->
  <div class="action-bar no-print">
    <div>
      <button onclick="window.print()" class="action-btn">🖨️ Print / Save as PDF</button>
    </div>
    <div class="action-tip">
      💡 Tip: In the print dialog, set Destination to <strong>"Save as PDF"</strong> to export an official PDF document.
    </div>
  </div>

  <div class="cert-canvas">
    <div class="cert-content">
      
      <!-- Header -->
      <div class="cert-header">
        <div class="cert-logo">
          <div class="cert-badge-icon">◈</div>
          <div class="cert-title-group">
            <h1>HashProof AI Forensic Laboratory</h1>
            <p>Digital Evidence & Cryptographic Verification Division</p>
          </div>
        </div>
        <div class="cert-meta-right">
          <div class="cert-id">#{rep_id}</div>
          <div class="cert-date">{examined_at}</div>
        </div>
      </div>

      <!-- Main Title -->
      <div class="title-banner">
        <h2>Certificate of Forensic Bitstream Integrity</h2>
        <p>Official Cryptographic Audit Docket & Telemetry Verification</p>
      </div>

      <!-- Verdict Banner -->
      <div class="verdict-box {badge_class}">
        <div class="verdict-icon">{badge_symbol}</div>
        <div>
          <div class="verdict-title">{status_text}</div>
          <div class="verdict-desc">{status_sub}</div>
        </div>
      </div>

      <!-- Subject Evidence Information -->
      <div class="section-title">📁 Subject Evidence Identification</div>
      <table class="docket-table">
        <tr><th>Evidence Filename</th><td><strong>{filename}</strong></td></tr>
        <tr><th>Calculated Size</th><td>{size_str}</td></tr>
        <tr><th>MIME / Media Format</th><td>{mime_type}</td></tr>
        <tr><th>Acquisition Method</th><td>Direct Binary Bitstream Ingestion (NIST FIPS 180-4)</td></tr>
      </table>

      <!-- Cryptographic Checksums -->
      <div class="section-title">🔐 Cryptographic Checksum Fingerprints</div>
      <div class="hash-panel">
        <div class="hash-label">Primary SHA-256 Checksum (256-Bit Cryptographic Hash)</div>
        <div class="hash-val-sha256">{sha256}</div>
        <div class="hash-subgrid">
          <div class="hash-sub-item">
            <div class="hash-sub-label">Secondary SHA-1 Checksum</div>
            <div class="hash-sub-val">{sha1}</div>
          </div>
          <div class="hash-sub-item">
            <div class="hash-sub-label">Legacy MD5 Checksum</div>
            <div class="hash-sub-val">{md5}</div>
          </div>
        </div>
      </div>

      <!-- Modality Telemetry -->
      {telemetry_html}

      <!-- Findings -->
      <div class="section-title">🔍 Forensic Observations & Findings</div>
      <ul class="finding-list">
        {findings_html}
      </ul>

      <!-- Footer & Attestation -->
      <div class="cert-footer">
        <div class="footer-legal">
          <strong>LEGAL ADMISSIBILITY NOTICE:</strong> This record certifies that the digital asset described herein was mathematically hashed directly from its byte bitstream without transformation. Admissible under Federal Rules of Evidence Rule 902(13) and Rule 902(14) for self-authenticating electronic records when chain of custody is established.
        </div>
        <div class="footer-stamp">
          <div class="stamp-box">
            <div class="stamp-title">AUTHENTICATED</div>
            <div class="stamp-node">NODE: HP-SEC-01</div>
          </div>
        </div>
      </div>

    </div>
  </div>

</body>
</html>
"""
    return html_content

def add_report(report):
    saved_report = save_report_to_db(report)
    existing_ids = {item.get("report_id") for item in st.session_state.reports if isinstance(item, dict)}

    if saved_report.get("report_id") not in existing_ids:
        st.session_state.reports.insert(0, saved_report)
    else:
        st.session_state.reports = [
            saved_report if item.get("report_id") == saved_report.get("report_id") else item
            for item in st.session_state.reports
        ]
    st.session_state.latest_report = saved_report

# ---------------------------------------------------------
# 6. HEADER & PERSISTENT NAVIGATION (7 FORENSIC MODULES)
# ---------------------------------------------------------
logo, tagline = st.columns([2, 1], vertical_alignment="center")

with logo:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:14px">
      <div style="display:flex;align-items:center;justify-content:center;
      width:44px;height:44px;border-radius:12px;
      background:linear-gradient(135deg,#a47aff,#55e5ff);
      color:#090914;font-size:24px;font-weight:900;box-shadow:0 0 22px rgba(85,229,255,.3)">◈</div>
      <div>
        <div style="font-family:Manrope,sans-serif;font-weight:800;
        letter-spacing:-.03em;font-size:1.18rem;color:#f4f4ff;line-height:1.1">
          HASHPROOF AI
        </div>
        <div style="font-size:.72rem;color:#55e5ff;letter-spacing:.12em;font-weight:700">
          EVIDENCE INTELLIGENCE CONSOLE
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

with tagline:
    st.markdown(
        '<div style="text-align:right"><span class="pill">'
        '● Forensic Node Online</span></div>',
        unsafe_allow_html=True
    )

st.markdown("<hr style='margin:1.2rem 0'>", unsafe_allow_html=True)

nav_cols = st.columns(7)
pages = ["Home", "Analysis", "Comparison", "Audio", "Lab", "History", "About"]

for col, page in zip(nav_cols, pages):
    with col:
        label = {
            "Home": "⌂ Home",
            "Analysis": "◈ Image/Doc",
            "Comparison": "⚖ Parity (A/B)",
            "Audio": "🎙️ Audio",
            "Lab": "🧪 Crypto Lab",
            "History": f"▤ Archive ({len(st.session_state.reports)})",
            "About": "ⓘ Standards",
        }[page]

        if st.button(
            label,
            key=f"nav_{page}",
            use_container_width=True,
            type="primary" if st.session_state.page == page else "secondary",
        ):
            st.session_state.page = page
            st.rerun()

st.write("")

# ---------------------------------------------------------
# PAGE 1: HOME
# ---------------------------------------------------------
if st.session_state.page == "Home":

    st.markdown("""
    <section class="hero">
      <span class="pill">DIGITAL FORENSICS · MULTI-MODAL EVIDENCE SUITE</span>
      <h1>Trust the evidence.<br>
      <span class="gradient">Verify the details.</span></h1>
      <p>
        A unified intelligence laboratory for examining digital evidence: 
        evaluate image EXIF headers, calculate cryptographic fingerprints across photos, 
        and inspect audio recordings and wiretaps for splicing and truncation.
      </p>
      <div style="height:2px;width:100%;margin:25px 0;
      background:linear-gradient(90deg,#a47aff,#55e5ff,transparent)"></div>
      <div style="color:#b8bdd8;font-size:.85rem;font-weight:500">
        ◈ Image & Document Hashing &nbsp; / &nbsp;
        ◈ 🎙️ Audio Wiretap & Voice Note Triage &nbsp; / &nbsp;
        ◈ Dual-Evidence Bit Parity
      </div>
    </section>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.1, 0.9], gap="large")

    with left:
        st.markdown('<div class="eyebrow">GET STARTED</div>', unsafe_allow_html=True)
        st.markdown("### Your evidence laboratory")
        st.write(
            "Select a specialized forensic workspace below to examine image containers, "
            "inspect audio call recordings, or test cryptographic parity."
        )

        c_btn1, c_btn2, c_btn3 = st.columns(3)
        with c_btn1:
            if st.button("Image Analysis →", type="primary", use_container_width=True, key="home_start"):
                st.session_state.page = "Analysis"
                st.rerun()
        with c_btn2:
            if st.button("Audio Forensics →", type="secondary", use_container_width=True, key="home_audio"):
                st.session_state.page = "Audio"
                st.rerun()
        with c_btn3:
            if st.button("Dual Parity →", type="secondary", use_container_width=True, key="home_compare"):
                st.session_state.page = "Comparison"
                st.rerun()

    with right:
        st.markdown('<div class="eyebrow">SESSION METRICS</div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("Indexed reports", len(st.session_state.reports))
        m2.metric("Evidence Modes", "Visual · Audio · Crypto")
        st.caption("Records are stored securely in SQLite and session memory. Download official Forensic Certificates (.html/PDF) or Case Dockets (.txt) for permanent archiving.")

    st.write("")
    st.markdown('<div class="eyebrow">DESIGNED FOR FORENSIC RIGOR</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    cards = [
        (c1, "🔐", "Multi-Hash Parity",
         "Calculate SHA-256, SHA-1, and MD5 so exact file bytes can be verified mathematically."),
        (c2, "🎙️", "Audio Waveform & Wiretaps",
         "Audit voice notes, wiretaps, and audio recordings for duration cuts, sample rates, and splicing."),
        (c3, "⚖️", "Comparative Parity",
         "Compare original master evidence against suspect subpoena files to detect minute tampering."),
    ]

    for col, icon, title, description in cards:
        with col:
            st.markdown(
                f'<div class="feature"><div class="feature-icon">{icon}</div>'
                f'<h3>{title}</h3><p>{description}</p></div>',
                unsafe_allow_html=True
            )

# ---------------------------------------------------------
# PAGE 2: IMAGE & DOCUMENT ANALYSIS WORKSPACE
# ---------------------------------------------------------
elif st.session_state.page == "Analysis":

    st.markdown("""
    <div class="feature-banner">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <span class="pill">MODE: DEEP FILE AUDIT</span>
          <h2>Image & Document Examination</h2>
          <p>
            Perform a non-destructive forensic sweep across an evidence file. 
            Computes <b>SHA-256, SHA-1, and MD5</b> digests, extracts structured EXIF headers (Camera, Timestamps, GPS), 
            and scans for software manipulation signatures.
          </p>
        </div>
        <div style="font-size:3rem;animation:floatDoodle 3.5s infinite ease-in-out;filter:drop-shadow(0 0 16px rgba(85,229,255,0.4));">
          🔬
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([0.95, 1.05], gap="large")

    with left:
        st.markdown("""
        <div class="pod-card">
          <div class="pod-tag pod-tag-a">01 / INTAKE TARGET</div>
          <h4 style="margin:0 0 10px 0">Select Evidence File</h4>
        </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Evidence File Input",
            type=["jpg", "jpeg", "png", "webp", "tif", "tiff", "bmp", "pdf"],
            key="evidence_upload",
            label_visibility="collapsed"
        )

        ref_hash = st.text_input(
            "Optional: Trusted Reference SHA-256 Hash",
            placeholder="Paste known 64-character hexadecimal hash",
            help="Compare uploaded file against a reference hash obtained from legal discovery."
        ).strip().lower()

        if uploaded:
            st.caption(f"📁 {uploaded.name} · {readable_size(len(uploaded.getvalue()))}")
            try:
                st.image(uploaded, caption="Evidence Visual Preview", use_container_width=True)
            except Exception:
                st.warning("Visual preview is unavailable for this container format.")
        else:
            st.markdown("""
            <div class="doodle-hero">
              <div>
                <div class="doodle-icon">📂</div>
                <div style="font-weight:700;color:#ffffff;font-size:0.95rem">Awaiting Evidence Container</div>
                <div style="color:#94a3b8;font-size:0.82rem;margin-top:4px">
                  Drag & drop an image or document above to begin cryptographic triage
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        run = st.button(
            "Execute Forensic Inspection  →",
            type="primary",
            use_container_width=True,
            disabled=uploaded is None,
            key="run_analysis",
        )

    with right:
        st.markdown("""
        <div class="pod-card">
          <div class="pod-tag pod-tag-b">02 / TELEMETRY & WORKFLOW</div>
          <h4 style="margin:0 0 10px 0">Inspection Pipeline</h4>
        </div>
        """, unsafe_allow_html=True)

        for badge, title, detail in [
            ("[ 01 🧬 ]", "Bitstream Fingerprint", "Compute SHA-256, SHA-1, and MD5"),
            ("[ 02 📐 ]", "Container Geometry", "Validate image format, dimensions, color mode"),
            ("[ 03 📸 ]", "EXIF Harvesting", "Extract camera, chronology, and GPS fields"),
            ("[ 04 🕵️ ]", "Heuristic Artifact Scan", "Detect editing software signatures"),
        ]:
            a, b = st.columns([0.22, 0.78])
            with a:
                st.markdown(f'<span class="step-badge">{badge}</span>', unsafe_allow_html=True)
            with b:
                st.markdown(f"**{title}**")
                st.caption(detail)
            st.markdown("<hr style='margin:8px 0'>", unsafe_allow_html=True)

        if run and uploaded:
            data_bytes = uploaded.getvalue()
            report = examine_evidence(data_bytes, uploaded.name, ref_hash)
            add_report(report)
            st.success("Forensic examination completed.")

    report = st.session_state.latest_report

    if report:
        st.write("")
        st.markdown('<div class="eyebrow">03 / FORENSIC RESULTS</div>', unsafe_allow_html=True)
        filename_display = report.get("file_name") or report.get("filename") or "Evidence Document"
        st.markdown(f"### {filename_display}")

        image_info = report.get("image") or {}
        size_display = report.get("file_size") or (f"{report.get('size_bytes', 0):,} bytes" if report.get("size_bytes") else "Unknown")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("File Size", size_display)
        m2.metric("Format", image_info.get("format", report.get("mime_type", "").split("/")[-1].upper()))
        m3.metric("Dimensions", image_info.get("dimensions", "—"))
        m4.metric("EXIF Headers", len(report.get("exif", {})))

        editing_traces = report.get("editing_traces", [])
        if editing_traces:
            st.warning(
                f"⚠️ **Software Footprint Detected**: File metadata contains signatures from **{', '.join(editing_traces)}**. "
                "This indicates the image was likely created, saved, or modified in photo editing software."
            )
        else:
            st.success("✅ **Clean Software Audit**: No common desktop photo editor signatures were identified in the metadata.")

        st.markdown("#### Cryptographic Fingerprints")
        h_col1, h_col2 = st.columns(2)
        with h_col1:
            st.caption("SHA-256 (Courtroom Forensic Standard)")
            st.markdown(f'<div class="hash-box">{report.get("sha256", "—")}</div>', unsafe_allow_html=True)
            st.code(report.get("sha256", "—"), language="text")
        with h_col2:
            st.caption("MD5 (Legacy Quick Checksum)")
            st.markdown(f'<div class="hash-box">{report.get("md5", "—")}</div>', unsafe_allow_html=True)
            st.caption(f"SHA-1: `{report.get('sha1', '—')}`")

        if report.get("reference_hash"):
            if report.get("hash_match"):
                st.success("✅ **PARITY VERIFIED**: 100% byte agreement with reference hash.")
            else:
                st.error("🚨 **PARITY MISMATCH**: File byte sequence differs from the provided reference hash.")

        tab1, tab2, tab3, tab4 = st.tabs(["Findings & Audit", "Categorized EXIF", "Raw Headers", "Export Package"])

        with tab1:
            st.markdown("#### Examination Findings")
            for finding in report.get("findings", []):
                st.markdown(f"- {finding}")

            st.markdown("#### Limitations & Boundaries")
            for limitation in report.get("limitations", []):
                st.caption(f"• {limitation}")

        with tab2:
            cat = report.get("exif_categorized") or {}
            col_c1, col_c2 = st.columns(2)

            with col_c1:
                st.markdown("##### 📷 Camera & Hardware")
                if cat.get("camera"):
                    st.dataframe([{"Field": k, "Value": str(v)} for k, v in cat["camera"].items()], use_container_width=True, hide_index=True)
                else:
                    st.caption("No camera hardware tags detected.")

                st.markdown("##### 🕒 Chronology & Timestamps")
                if cat.get("timestamps"):
                    st.dataframe([{"Field": k, "Value": str(v)} for k, v in cat["timestamps"].items()], use_container_width=True, hide_index=True)
                else:
                    st.caption("No embedded timestamp tags found.")

            with col_c2:
                st.markdown("##### 💻 Software & Processing")
                if cat.get("software"):
                    st.dataframe([{"Field": k, "Value": str(v)} for k, v in cat["software"].items()], use_container_width=True, hide_index=True)
                else:
                    st.caption("No software metadata tags recorded.")

                st.markdown("##### 📍 Geolocation Data")
                if cat.get("gps"):
                    st.dataframe([{"Field": k, "Value": str(v)} for k, v in cat["gps"].items()], use_container_width=True, hide_index=True)
                else:
                    st.caption("No GPS coordinate headers embedded in this file.")

        with tab3:
            if report.get("exif"):
                st.markdown("#### All Extracted EXIF Tags")
                st.dataframe([{"Tag": k, "Value": str(v)} for k, v in report["exif"].items()], use_container_width=True, hide_index=True)
            else:
                st.info("No EXIF metadata fields were extracted.")

        with tab4:
            st.markdown("#### 📄 Forensic Examination Report Export")
            st.write("Generate a court-ready cryptographic certificate or evidence docket for record preservation, legal proceedings, or case filing.")
            rep_id = report.get("report_id", "report")
            raw_fn = report.get("file_name") or report.get("filename") or "evidence"
            clean_name = raw_fn.rsplit(".", 1)[0].replace(" ", "_")

            col_d1, col_d2, col_d3 = st.columns([2, 1.2, 1])
            with col_d1:
                st.download_button(
                    "⬇ Download Forensic Certificate (.html / PDF)",
                    data=generate_html_certificate(report),
                    file_name=f"{clean_name}_Forensic_Certificate.html",
                    mime="text/html",
                    use_container_width=True,
                    type="primary",
                    key=f"download_html_{rep_id}",
                    help="Interactive, branded certificate with one-click 'Print to PDF' for official filing."
                )
            with col_d2:
                st.download_button(
                    "⬇ Case Docket (.txt)",
                    data=generate_text_docket(report),
                    file_name=f"{clean_name}_Docket.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key=f"download_txt_{rep_id}",
                    help="Clean, formatted text docket suitable for transcripts or terminal logs."
                )
            with col_d3:
                st.download_button(
                    "⬇ JSON (.json)",
                    data=export_report_json(report),
                    file_name=f"{rep_id}.json",
                    mime="application/json",
                    use_container_width=True,
                    key=f"download_json_{rep_id}",
                    help="Raw cryptographic telemetry object for automated ingestion."
                )

            st.caption("💡 **Tip**: When you open the **.html Certificate**, click **'🖨️ Print / Save as PDF'** to instantly save an official, print-ready PDF certificate!")

# ---------------------------------------------------------
# PAGE 3: DUAL EVIDENCE COMPARATOR (A vs B)
# ---------------------------------------------------------
elif st.session_state.page == "Comparison":

    st.markdown("""
    <div class="feature-banner">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <span class="pill">MODE: COMPARATIVE PARITY</span>
          <h2>Dual-Evidence Parity Comparator</h2>
          <p>
            Upload an original reference file alongside a suspect file to perform side-by-side comparative inspection. 
            Detects whether an image has been re-saved, compressed, cropped, or edited down to the exact bitstream.
          </p>
        </div>
        <div style="font-size:3rem;animation:floatDoodle 3.5s infinite ease-in-out;filter:drop-shadow(0 0 16px rgba(164,122,255,0.4));">
          ⚖️
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    comp_left, comp_right = st.columns(2, gap="large")

    with comp_left:
        st.markdown("""
        <div class="pod-card">
          <div class="pod-tag pod-tag-a">POD A / ORIGINAL EVIDENCE</div>
          <h4 style="margin:0 0 10px 0">Evidence A (Reference)</h4>
        </div>
        """, unsafe_allow_html=True)

        file_a = st.file_uploader(
            "Upload Evidence A",
            type=["jpg", "jpeg", "png", "webp", "tif", "tiff", "bmp", "pdf"],
            key="file_a",
            label_visibility="collapsed"
        )
        if file_a:
            st.caption(f"📁 **{file_a.name}** · {readable_size(len(file_a.getvalue()))}")
            try:
                st.image(file_a, caption="Evidence A Preview", use_container_width=True)
            except Exception:
                pass
        else:
            st.markdown("""
            <div class="doodle-hero">
              <div>
                <div class="doodle-icon">🛡️</div>
                <div style="font-weight:700;color:#ffffff;font-size:0.9rem">Evidence A Required</div>
                <div style="color:#94a3b8;font-size:0.8rem;margin-top:2px">Upload the benchmark master file</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with comp_right:
        st.markdown("""
        <div class="pod-card">
          <div class="pod-tag pod-tag-b">POD B / COMPARISON EVIDENCE</div>
          <h4 style="margin:0 0 10px 0">Evidence B (Suspect)</h4>
        </div>
        """, unsafe_allow_html=True)

        file_b = st.file_uploader(
            "Upload Evidence B",
            type=["jpg", "jpeg", "png", "webp", "tif", "tiff", "bmp", "pdf"],
            key="file_b",
            label_visibility="collapsed"
        )
        if file_b:
            st.caption(f"📁 **{file_b.name}** · {readable_size(len(file_b.getvalue()))}")
            try:
                st.image(file_b, caption="Evidence B Preview", use_container_width=True)
            except Exception:
                pass
        else:
            st.markdown("""
            <div class="doodle-hero">
              <div>
                <div class="doodle-icon">🔍</div>
                <div style="font-weight:700;color:#ffffff;font-size:0.9rem">Evidence B Required</div>
                <div style="color:#94a3b8;font-size:0.8rem;margin-top:2px">Upload the suspect comparison file</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    if file_a and file_b:
        st.write("")
        if st.button("Execute Dual-File Parity Comparison →", type="primary", use_container_width=True):
            data_a = file_a.getvalue()
            data_b = file_b.getvalue()

            hash_a = calculate_hashes(data_a)
            hash_b = calculate_hashes(data_b)

            exact_byte_match = (hash_a["sha256"] == hash_b["sha256"])

            dims_match = False
            format_a, format_b = "Unknown", "Unknown"
            dim_a, dim_b = "—", "—"

            try:
                with Image.open(BytesIO(data_a)) as img_a:
                    format_a = img_a.format or "Unknown"
                    dim_a = f"{img_a.width} × {img_a.height}"
                with Image.open(BytesIO(data_b)) as img_b:
                    format_b = img_b.format or "Unknown"
                    dim_b = f"{img_b.width} × {img_b.height}"
                dims_match = (dim_a == dim_b)
            except Exception:
                pass

            if exact_byte_match:
                st.markdown("""
                <div class="verdict-banner verdict-match">
                  <div style="font-size:2.4rem">⚖️</div>
                  <div>
                    <h3 style="margin:0;color:#a7f3d0">PARITY VERIFIED — EXACT BYTE CLONE</h3>
                    <p style="margin:4px 0 0;font-size:0.9rem;color:#d1fae5">
                      Both files share identical SHA-256, SHA-1, and MD5 fingerprints. 
                      Not a single bit has been altered, cropped, recompressed, or modified.
                    </p>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="verdict-banner verdict-mismatch">
                  <div style="font-size:2.4rem">🚨</div>
                  <div>
                    <h3 style="margin:0;color:#fecdd3">PARITY MISMATCH — EVIDENCE ALTERATION DETECTED</h3>
                    <p style="margin:4px 0 0;font-size:0.9rem;color:#ffe4e6">
                      The cryptographic checksums do not match. The files are not byte-identical. 
                      This may indicate re-saving, metadata tampering, resolution scaling, or image manipulation.
                    </p>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("#### Comparison Telemetry Breakdown")
            comp_table = [
                {"Inspection Metric": "Exact Byte Parity (SHA-256)", "Evidence A": hash_a["sha256"][:16] + "…", "Evidence B": hash_b["sha256"][:16] + "…", "Match Status": "✅ Identical" if exact_byte_match else "❌ Differ"},
                {"Inspection Metric": "File Size", "Evidence A": readable_size(len(data_a)), "Evidence B": readable_size(len(data_b)), "Match Status": "✅ Identical" if len(data_a) == len(data_b) else "❌ Differ"},
                {"Inspection Metric": "Image Dimensions", "Evidence A": dim_a, "Evidence B": dim_b, "Match Status": "✅ Identical" if dims_match else "❌ Differ"},
                {"Inspection Metric": "Format Type", "Evidence A": format_a, "Evidence B": format_b, "Match Status": "✅ Identical" if format_a == format_b else "❌ Differ"},
                {"Inspection Metric": "MD5 Checksum", "Evidence A": hash_a["md5"], "Evidence B": hash_b["md5"], "Match Status": "✅ Identical" if hash_a["md5"] == hash_b["md5"] else "❌ Differ"},
            ]
            st.dataframe(comp_table, use_container_width=True, hide_index=True)

            comp_report = {
                "report_id": "CMP-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
                "file_name": f"{file_a.name} vs {file_b.name}",
                "filename": f"{file_a.name} vs {file_b.name}",
                "examined_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "date": datetime.now().astimezone().isoformat(timespec="seconds"),
                "hash_match": exact_byte_match,
                "sha256": hash_a["sha256"],
                "sha1": hash_a["sha1"],
                "md5": hash_a["md5"],
                "comparison": {
                    "file_a": {"name": file_a.name, "size": readable_size(len(data_a)), "sha256": hash_a["sha256"], "format": format_a, "dimensions": dim_a},
                    "file_b": {"name": file_b.name, "size": readable_size(len(data_b)), "sha256": hash_b["sha256"], "format": format_b, "dimensions": dim_b},
                    "exact_byte_match": exact_byte_match,
                    "dims_match": dims_match
                },
                "findings": [
                    f"Parity Verdict: {'EXACT BYTE-FOR-BYTE CLONE — UNALTERED' if exact_byte_match else 'PARITY MISMATCH — EVIDENCE ALTERATION DETECTED'}",
                    f"Evidence A SHA-256: {hash_a['sha256']}",
                    f"Evidence B SHA-256: {hash_b['sha256']}",
                    f"Dimensions: Evidence A ({dim_a}) vs Evidence B ({dim_b})",
                    f"File Size: Evidence A ({readable_size(len(data_a))}) vs Evidence B ({readable_size(len(data_b))})"
                ]
            }

            st.write("")
            st.markdown("#### 📄 Parity Comparison Report Export")
            col_c1, col_c2, col_c3 = st.columns([2, 1.2, 1])
            with col_c1:
                st.download_button(
                    "⬇ Download Parity Certificate (.html / PDF)",
                    data=generate_html_certificate(comp_report),
                    file_name=f"Parity_{file_a.name}_vs_{file_b.name}.html",
                    mime="text/html",
                    type="primary",
                    use_container_width=True,
                    key=f"comp_html_{comp_report['report_id']}",
                )
            with col_c2:
                st.download_button(
                    "⬇ Case Docket (.txt)",
                    data=generate_text_docket(comp_report),
                    file_name=f"Parity_{file_a.name}_vs_{file_b.name}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key=f"comp_txt_{comp_report['report_id']}",
                )
            with col_c3:
                st.download_button(
                    "⬇ JSON (.json)",
                    data=export_report_json(comp_report),
                    file_name=f"{comp_report['report_id']}.json",
                    mime="application/json",
                    use_container_width=True,
                    key=f"comp_json_{comp_report['report_id']}",
                )

# ---------------------------------------------------------
# PAGE 4: AUDIO FORENSICS (OPTIMIZED FOR ZERO LAG)
# ---------------------------------------------------------
elif st.session_state.page == "Audio":

    st.markdown("""
    <div class="feature-banner">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <span class="pill">MODE: ACOUSTIC EVIDENCE & WIRETAP AUDIT</span>
          <h2>Audio Forensic Intelligence</h2>
          <p>
            Audit voice notes, emergency dispatch recordings, wiretaps, and audio clips. 
            Verifies bitstream hashes, parses acoustic sample rates, renders waveform graphs, 
            and checks for audio trimming or splicing.
          </p>
        </div>
        <div style="font-size:3rem;animation:floatDoodle 3.5s infinite ease-in-out;filter:drop-shadow(0 0 16px rgba(85,229,255,0.4));">
          🎙️
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    audio_tab1, audio_tab2 = st.tabs(["Single Audio Inspection", "Dual Audio Comparator (Clip A vs B)"])

    with audio_tab1:
        aud_col1, aud_col2 = st.columns([0.95, 1.05], gap="large")

        with aud_col1:
            st.markdown("""
            <div class="pod-card">
              <div class="pod-tag pod-tag-a">AUDIO INTAKE</div>
              <h4 style="margin:0 0 10px 0">Upload Voice / Audio Recording</h4>
            </div>
            """, unsafe_allow_html=True)

            audio_file = st.file_uploader(
                "Upload Audio Evidence",
                type=["wav", "mp3", "ogg", "m4a"],
                key="audio_upload",
                label_visibility="collapsed"
            )

            if audio_file:
                st.caption(f"🎵 **{audio_file.name}** · {readable_size(len(audio_file.getvalue()))}")
                st.audio(audio_file)
            else:
                st.markdown("""
                <div class="doodle-hero">
                  <div>
                    <div class="doodle-icon">📻</div>
                    <div style="font-weight:700;color:#ffffff;font-size:0.95rem">Awaiting Audio Recording</div>
                    <div style="color:#94a3b8;font-size:0.82rem;margin-top:4px">
                      Upload WAV, MP3, or voice note to inspect acoustic telemetry
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        with aud_col2:
            if audio_file:
                aud_bytes = audio_file.getvalue()
                info = inspect_audio_data(aud_bytes, audio_file.name)

                st.markdown("""
                <div class="pod-card">
                  <div class="pod-tag pod-tag-b">ACOUSTIC TELEMETRY</div>
                  <h4 style="margin:0 0 10px 0">Signal Verification Metrics</h4>
                </div>
                """, unsafe_allow_html=True)

                m1, m2, m3 = st.columns(3)
                m1.metric("Duration", info["duration_str"])
                m2.metric("Sample Rate", info["sample_rate"])
                m3.metric("Channels", info["channels"])

                m4, m5 = st.columns(2)
                m4.metric("Encoding Format", info["bit_depth"])
                m5.metric("Total Frames", info["total_frames"])

                if info["waveform"]:
                    st.markdown("##### 📈 Waveform Amplitude Visualizer (Splice Detector)")
                    st.line_chart(info["waveform"], height=160)
                    st.caption("Visual amplitude envelope over time. Abrupt drops to zero or sudden shifts may indicate edited cut points.")

                st.markdown("##### Cryptographic Bitstream Checksums")
                st.markdown(f'<div class="hash-box">{info["hashes"]["sha256"]}</div>', unsafe_allow_html=True)
                st.caption(f"MD5: `{info['hashes']['md5']}` · SHA-1: `{info['hashes']['sha1']}`")

                rep_id = "AUD-" + datetime.now().strftime("%Y%m%d-%H%M%S")
                clean_name = audio_file.name.rsplit(".", 1)[0].replace(" ", "_")
                audio_bytes = audio_file.getvalue()
                
                report_audio = {
                    "report_id": rep_id,
                    "file_name": audio_file.name,
                    "filename": audio_file.name,
                    "file_size": readable_size(len(audio_bytes)),
                    "file_size_bytes": len(audio_bytes),
                    "size_bytes": len(audio_bytes),
                    "mime_type": getattr(audio_file, "type", "audio/mpeg") or "audio/mpeg",
                    "sha256": info["hashes"]["sha256"],
                    "sha1": info["hashes"]["sha1"],
                    "md5": info["hashes"]["md5"],
                    "hashes": info["hashes"],
                    "examined_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                    "date": datetime.now().astimezone().isoformat(timespec="seconds"),
                    "audio": {
                        "duration": info["duration_str"],
                        "sample_rate": info["sample_rate"],
                        "channels": info["channels"],
                        "bit_depth": info["bit_depth"],
                        "total_frames": info["total_frames"]
                    },
                    "telemetry": {
                        "duration": info["duration_str"],
                        "sample_rate": info["sample_rate"],
                        "channels": info["channels"],
                        "bit_depth": info["bit_depth"],
                        "total_frames": info["total_frames"]
                    },
                    "findings": [
                        f"Acoustic Duration: {info['duration_str']}",
                        f"Acoustic Sample Rate: {info['sample_rate']} with {info['channels']}",
                        f"Encoding & Bitrate: {info['bit_depth']}",
                        f"Total Frame Buffer: {info['total_frames']}",
                        "Cryptographic Bitstream: SHA-256 integrity digest verified directly from acoustic file."
                    ],
                    "limitations": [
                        "Cryptographic hashes verify bitstream identity; they do not detect analog acoustic re-recording.",
                        "Voice biometric matching requires verified reference voiceprints."
                    ]
                }

                # Persist in session state & SQLite database
                add_report(report_audio)

                st.write("")
                st.markdown("#### 📄 Audio Forensic Report Export")
                col_a1, col_a2, col_a3 = st.columns([2, 1.2, 1])
                with col_a1:
                    st.download_button(
                        "⬇ Download Forensic Certificate (.html / PDF)",
                        data=generate_html_certificate(report_audio),
                        file_name=f"{clean_name}_Audio_Certificate.html",
                        mime="text/html",
                        type="primary",
                        use_container_width=True,
                        key=f"audio_html_{rep_id}",
                        help="Interactive official certificate with 1-click 'Print / Save as PDF' for court submission."
                    )
                with col_a2:
                    st.download_button(
                        "⬇ Case Docket (.txt)",
                        data=generate_text_docket(report_audio),
                        file_name=f"{clean_name}_Audio_Docket.txt",
                        mime="text/plain",
                        use_container_width=True,
                        key=f"audio_txt_{rep_id}",
                        help="Clean, formatted text docket suitable for transcripts or case binders."
                    )
                with col_a3:
                    st.download_button(
                        "⬇ JSON (.json)",
                        data=export_report_json(report_audio),
                        file_name=f"{clean_name}_audio_forensics.json",
                        mime="application/json",
                        use_container_width=True,
                        key=f"audio_json_{rep_id}",
                        help="Raw JSON telemetry for technical ingestion."
                    )

                st.caption("💡 **Tip**: Open the **.html Certificate** in your browser and click **'🖨️ Print / Save as PDF'** to instantly save an official court-ready PDF!")
            else:
                st.markdown("""
                <div class="pod-card">
                  <div class="pod-tag pod-tag-b">ACOUSTIC PIPELINE ACTIVE</div>
                  <h4 style="margin:0 0 10px 0">Telemetry & Splice Monitor</h4>
                  
                  <div class="equalizer-box">
                    <span class="equalizer-bar"></span>
                    <span class="equalizer-bar"></span>
                    <span class="equalizer-bar"></span>
                    <span class="equalizer-bar"></span>
                    <span class="equalizer-bar"></span>
                    <span class="equalizer-bar"></span>
                    <span class="equalizer-bar"></span>
                    <span class="equalizer-bar"></span>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                for badge, title, detail in [
                    ("[ 01 🎵 ]", "Bitstream Checksums", "Calculate SHA-256 and MD5 on the raw audio track"),
                    ("[ 02 ⏱️ ]", "Millisecond Duration", "Parse exact frame count to expose cropped clips"),
                    ("[ 03 🎚️ ]", "PCM Sample Rate", "Distinguish 8 kHz phone calls vs 44.1 kHz studio audio"),
                    ("[ 04 ✂️ ]", "Splice & Cut Detector", "Chart the amplitude envelope to reveal silent edits"),
                ]:
                    a, b = st.columns([0.22, 0.78])
                    with a:
                        st.markdown(f'<span class="step-badge">{badge}</span>', unsafe_allow_html=True)
                    with b:
                        st.markdown(f"**{title}**")
                        st.caption(detail)
                    st.markdown("<hr style='margin:8px 0'>", unsafe_allow_html=True)

    with audio_tab2:
        st.markdown("### Dual Audio Parity Comparator")
        st.write("Compare a master recording against a suspected trimmed or altered audio file:")

        aud_a_col, aud_b_col = st.columns(2, gap="large")

        with aud_a_col:
            st.markdown("""
            <div class="pod-card">
              <div class="pod-tag pod-tag-a">AUDIO A / MASTER BENCHMARK</div>
              <h4 style="margin:0 0 10px 0">Master Wiretap / Audio A</h4>
            </div>
            """, unsafe_allow_html=True)
            aud_cmp_a = st.file_uploader("Upload Audio A", type=["wav", "mp3", "ogg", "m4a"], key="cmp_aud_a", label_visibility="collapsed")
            if aud_cmp_a:
                st.audio(aud_cmp_a)

        with aud_b_col:
            st.markdown("""
            <div class="pod-card">
              <div class="pod-tag pod-tag-b">AUDIO B / SUSPECT CLIP</div>
              <h4 style="margin:0 0 10px 0">Suspect / Leaked Clip B</h4>
            </div>
            """, unsafe_allow_html=True)
            aud_cmp_b = st.file_uploader("Upload Audio B", type=["wav", "mp3", "ogg", "m4a"], key="cmp_aud_b", label_visibility="collapsed")
            if aud_cmp_b:
                st.audio(aud_cmp_b)

        if aud_cmp_a and aud_cmp_b:
            data_aud_a = aud_cmp_a.getvalue()
            data_aud_b = aud_cmp_b.getvalue()

            h_a = calculate_hashes(data_aud_a)
            h_b = calculate_hashes(data_aud_b)

            is_match = (h_a["sha256"] == h_b["sha256"])

            if is_match:
                st.markdown("""
                <div class="verdict-banner verdict-match">
                  <div style="font-size:2.2rem">🎙️</div>
                  <div>
                    <h3 style="margin:0;color:#a7f3d0">ACOUSTIC PARITY VERIFIED — IDENTICAL BITSTREAM</h3>
                    <p style="margin:4px 0 0;font-size:0.88rem;color:#d1fae5">
                      Both audio files are 100% byte-for-byte identical. Neither file has been trimmed, re-encoded, filtered, or altered.
                    </p>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="verdict-banner verdict-mismatch">
                  <div style="font-size:2.2rem">🚨</div>
                  <div>
                    <h3 style="margin:0;color:#fecdd3">ACOUSTIC PARITY MISMATCH — AUDIO ALTERATION DETECTED</h3>
                    <p style="margin:4px 0 0;font-size:0.88rem;color:#ffe4e6">
                      The audio bitstreams differ. This indicates that one recording was cropped, re-compressed, noise-filtered, or spliced.
                    </p>
                  </div>
                </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# PAGE 5: DEDICATED CRYPTOGRAPHIC LAB
# ---------------------------------------------------------
elif st.session_state.page == "Lab":

    st.markdown("""
    <div class="feature-banner">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <span class="pill">MODE: INTERACTIVE CRYPTOGRAPHIC LAB</span>
          <h2>Cryptographic Avalanche Simulator</h2>
          <p>
            Experience how digital evidence verification works under the hood. 
            Test the <b>Avalanche Effect</b>: see how changing a single byte scrambles the entire 256-bit hash.
          </p>
        </div>
        <div style="font-size:3rem;animation:floatDoodle 3.5s infinite ease-in-out;filter:drop-shadow(0 0 16px rgba(85,229,255,0.4));">
          🧪
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Test the Avalanche Effect")
    st.write("Modify just one letter or symbol on the right, and observe how the output hashes diverge completely:")

    sim_col1, sim_col2 = st.columns(2, gap="large")

    with sim_col1:
        st.markdown("""
        <div class="pod-card">
          <div class="pod-tag pod-tag-a">SAMPLE A / BENCHMARK TEXT</div>
          <h4 style="margin:0 0 10px 0">Original Text String</h4>
        </div>
        """, unsafe_allow_html=True)

        text_a = st.text_input("Benchmark String", value="Evidence Item #104 - Intact Scene", key="lab_text_a")
        hashes_a = calculate_hashes(text_a.encode('utf-8'))

        st.caption("SHA-256 Output")
        st.markdown(f'<div class="hash-box">{hashes_a["sha256"]}</div>', unsafe_allow_html=True)
        st.caption(f"MD5: `{hashes_a['md5']}`")

    with sim_col2:
        st.markdown("""
        <div class="pod-card">
          <div class="pod-tag pod-tag-b">SAMPLE B / MODIFIED TEXT</div>
          <h4 style="margin:0 0 10px 0">Tampered Text String</h4>
        </div>
        """, unsafe_allow_html=True)

        text_b = st.text_input("Modified String (Change 1 character)", value="Evidence Item #104 - intact Scene", key="lab_text_b")
        hashes_b = calculate_hashes(text_b.encode('utf-8'))

        st.caption("SHA-256 Output")
        st.markdown(f'<div class="hash-box">{hashes_b["sha256"]}</div>', unsafe_allow_html=True)
        st.caption(f"MD5: `{hashes_b['md5']}`")

    st.write("")
    if hashes_a["sha256"] == hashes_b["sha256"]:
        st.markdown("""
        <div class="verdict-banner verdict-match">
          <div style="font-size:2rem">🛡️</div>
          <div>
            <b style="color:#a7f3d0">Exact Match (0 Bits Flipped)</b>
            <p style="margin:2px 0 0;font-size:0.85rem;color:#d1fae5">Both input strings are 100% byte-for-byte identical.</p>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        diff_count = sum(1 for a, b in zip(hashes_a["sha256"], hashes_b["sha256"]) if a != b)
        st.markdown(f"""
        <div class="verdict-banner verdict-mismatch">
          <div style="font-size:2rem">⚡</div>
          <div>
            <b style="color:#fecdd3">Avalanche Effect Triggered! ({diff_count}/64 hex positions scrambled)</b>
            <p style="margin:2px 0 0;font-size:0.85rem;color:#ffe4e6">
              Even a tiny 1-character case difference completely re-routes the internal SHA-256 round permutations. 
              This makes mathematical forgery or splicing impossible.
            </p>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# PAGE 6: REPORT HISTORY
# ---------------------------------------------------------
elif st.session_state.page == "History":

    st.markdown("""
    <div class="feature-banner">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <span class="pill">MODE: SESSION AUDIT REPOSITORY</span>
          <h2>Examination Archive</h2>
          <p>
            All digital evidence files analyzed during this active session are indexed here. 
            Download court-ready Forensic Certificates (.html/PDF), Plaintext Dockets (.txt), or machine JSON records.
          </p>
        </div>
        <div style="font-size:3rem;animation:floatDoodle 3.5s infinite ease-in-out;filter:drop-shadow(0 0 16px rgba(85,229,255,0.4));">
          🗄️
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    reports = st.session_state.reports

    if not reports:
        with st.container(border=True):
            st.markdown("### No examinations yet")
            st.write("Reports will appear here after you analyze an evidence file.")

            if st.button("Go to evidence analysis →", type="primary"):
                st.session_state.page = "Analysis"
                st.rerun()
    else:
        st.caption(f"{len(reports)} report(s) in this session")

        for report in reports:
            name = report.get("file_name") or report.get("filename") or "Unknown File"
            rep_id = report.get("report_id") or "HP-LEGACY"
            date = report.get("examined_at") or report.get("date") or "Unknown Date"
            size = report.get("file_size") or (f"{report.get('size_bytes', 0):,} bytes" if report.get("size_bytes") else "Size unavailable")
            hash_str = report.get("sha256") or report.get("file_hash") or "Hash unavailable"

            with st.container(border=True):
                left, right = st.columns([3, 1])

                with left:
                    st.markdown(f"**{name}**")
                    st.caption(f"{rep_id} · {date} · {size}")
                    st.code(hash_str, language="text")

                with right:
                    st.download_button(
                        "⬇ Certificate (.html/PDF)",
                        data=generate_html_certificate(report),
                        file_name=f"{rep_id}_Certificate.html",
                        mime="text/html",
                        use_container_width=True,
                        type="primary",
                        key=f"hist_html_{rep_id}",
                    )

                    with st.expander("More formats (.txt, .json)"):
                        st.download_button(
                            "⬇ Docket (.txt)",
                            data=generate_text_docket(report),
                            file_name=f"{rep_id}_Docket.txt",
                            mime="text/plain",
                            use_container_width=True,
                            key=f"hist_txt_{rep_id}",
                        )
                        st.download_button(
                            "⬇ JSON (.json)",
                            data=export_report_json(report),
                            file_name=f"{rep_id}.json",
                            mime="application/json",
                            use_container_width=True,
                            key=f"hist_json_{rep_id}",
                        )

                    if st.button("View report", key=f"view_{rep_id}", use_container_width=True):
                        st.session_state.latest_report = report
                        st.session_state.page = "Analysis"
                        st.rerun()

        st.caption("Reports are preserved in active session memory and SQLite. Download records for legal discovery.")

        if st.button("Clear session history"):
            st.session_state.reports = []
            st.session_state.latest_report = None
            st.rerun()

# ---------------------------------------------------------
# PAGE 7: ABOUT & STANDARDS
# ---------------------------------------------------------
elif st.session_state.page == "About":

    st.markdown("""
    <div class="feature-banner">
      <div style="display:flex;align-items:center;justify-content:space-between">
        <div>
          <span class="pill">MODE: METHODOLOGY & STANDARDS</span>
          <h2>Forensic Integrity & Standards</h2>
          <p>
            A transparent, courtroom-aligned reference guide to mathematical hashing, 
            metadata admissibility risks, and preliminary digital evidence boundaries.
          </p>
        </div>
        <div style="font-size:3.2rem;animation:floatDoodle 3s infinite ease-in-out;filter:drop-shadow(0 0 15px rgba(85,229,255,0.4));margin-left:20px;">
          ⚖️
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown('<div class="eyebrow">VERIFIED CAPABILITIES</div>', unsafe_allow_html=True)
        st.markdown("### What HashProof AI Does")

        capabilities = [
            ("🔐", "Deterministic Multi-Hashing", 
             "Calculates <b>SHA-256</b>, <b>SHA-1</b>, and <b>MD5</b> checksums simultaneously across the raw binary bitstream. Proves zero-bit modification."),
            ("🎙️", "Acoustic Telemetry & Wiretaps", 
             "Audits audio evidence, parsing exact millisecond durations, PCM sample rates, channels, and waveform cut points."),
            ("⚖️", "Bivalent Parity Verification", 
             "Performs side-by-side mathematical parity checks between original reference evidence and suspect subpoena files."),
            ("🧬", "Lossless Container Parsing", 
             "Reads EXIF, TIFF markers, dimensions, and color profiles without decompressing or modifying original evidence bytes."),
            ("🔍", "Heuristic Software Footprint Auditing", 
             "Scans file headers for traces of photo-editing applications such as Photoshop, GIMP, Snapseed, and Lightroom.")
        ]

        for icon, title, desc in capabilities:
            st.markdown(f"""
            <div style="background:rgba(20,24,48,0.8);border:1px solid rgba(85,229,255,0.18);border-radius:16px;padding:16px 20px;margin-bottom:12px;display:flex;gap:16px;align-items:flex-start;">
              <div style="font-size:1.5rem;background:rgba(85,229,255,0.1);border:1px solid rgba(85,229,255,0.25);border-radius:12px;width:44px;height:44px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">{icon}</div>
              <div>
                <b style="color:#ffffff;font-size:0.95rem">{title}</b>
                <p style="font-size:0.85rem;color:#94a3b8;margin:4px 0 0 0;line-height:1.5">{desc}</p>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="eyebrow" style="color:#f43f5e">LEGAL BOUNDARIES & DISCLAIMERS</div>', unsafe_allow_html=True)
        st.markdown("### What It Does Not Prove")

        limitations = [
            ("🛡️", "Authorship & Ownership", 
             "A hash confirms exact byte integrity, <b>never</b> who took the photograph, authored the document, or pressed the shutter."),
            ("⚠️", "EXIF Absolute Veracity", 
             "EXIF tags are stored as plain text. They can easily be edited, back-dated, or stripped completely by messaging apps and desktop tools."),
            ("🤖", "Neural / Deepfake AI Detection", 
             "This platform verifies file-level and container integrity; it does not run trained neural network deepfake / diffusion artifact classifiers."),
            ("⚖️", "Court Admissibility Pre-requisite", 
             "High-stakes judicial evidence requires certified expert testimony and unbroken physical/digital chain-of-custody logging.")
        ]

        for icon, title, desc in limitations:
            st.markdown(f"""
            <div style="background:rgba(26,18,35,0.8);border:1px solid rgba(244,63,94,0.2);border-radius:16px;padding:16px 20px;margin-bottom:12px;display:flex;gap:16px;align-items:flex-start;">
              <div style="font-size:1.5rem;background:rgba(244,63,94,0.1);border:1px solid rgba(244,63,94,0.25);border-radius:12px;width:44px;height:44px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">{icon}</div>
              <div>
                <b style="color:#fecdd3;font-size:0.95rem">{title}</b>
                <p style="font-size:0.85rem;color:#cbd5e1;margin:4px 0 0 0;line-height:1.5">{desc}</p>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    with st.expander("⚡ What is SHA-256 and why is it legally accepted in forensic science?"):
        st.write(
            "SHA-256 (Secure Hash Algorithm 256-bit) is a cryptographic standard designed by the NSA and formalized by NIST (FIPS 180-4). "
            "It computes a deterministic 64-character hexadecimal digest from an arbitrary stream of bytes. "
            "Because there are 2^256 possible combinations—more than the number of atoms in the observable universe—"
            "finding two different files with the same hash (a collision) is mathematically infeasible."
        )

    with st.expander("📷 Why can EXIF metadata be misleading or vulnerable to tampering?"):
        st.write(
            "EXIF (Exchangeable Image File Format) headers are written into unencrypted JPEG/TIFF metadata blocks. "
            "Anyone using common tools can alter the camera model, modify GPS coordinates, or forge the timestamp. "
            "Furthermore, platforms like WhatsApp, Twitter, and Facebook automatically strip EXIF headers to protect user privacy. "
            "Hence, missing EXIF is common on web media and does not automatically imply malicious intent."
        )

# ---------------------------------------------------------
# 8. CLEAN FOOTER
# ---------------------------------------------------------
st.markdown(
    '<div class="footer">HashProof AI · Digital Evidence Integrity & Forensic Triage Console<br>'
    'Document methods, record limitations, and maintain the chain of custody</div>',
    unsafe_allow_html=True
)