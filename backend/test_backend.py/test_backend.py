
from backend.analyzer import analyze_file

# A tiny test file with a valid PNG signature.
sample_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20

result = analyze_file(sample_bytes, "sample.png")

print("Detected format:", result["detected_format"])
print("SHA-256:", result["sha256"])
print("File size:", result["file_size_bytes"])
print("Consistency:", result["consistency_status"])
