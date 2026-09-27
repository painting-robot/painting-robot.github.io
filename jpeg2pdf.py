#!/usr/bin/env python3
"""Wrap one JPEG in a single-page PDF without re-encoding it.

Usage: jpeg2pdf.py IN.jpg OUT.pdf PAGE_WIDTH_PT [PAGE_HEIGHT_PT]

The JPEG bytes are embedded as-is (DCTDecode), so quality and size are exactly
those of the input file. If the height is omitted it follows the image ratio.
Standard library only.
"""
import struct
import sys


def jpeg_size(data):
    """Return (width, height, components) from the JPEG's SOF marker."""
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            raise ValueError("not a JPEG")
        marker = data[i + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        length = struct.unpack(">H", data[i + 2:i + 4])[0]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            h, w, comps = struct.unpack(">HHB", data[i + 5:i + 10])
            return w, h, comps
        i += 2 + length
    raise ValueError("no SOF marker")


def main():
    src, dst, page_w = sys.argv[1], sys.argv[2], float(sys.argv[3])
    data = open(src, "rb").read()
    w, h, comps = jpeg_size(data)
    page_h = float(sys.argv[4]) if len(sys.argv) > 4 else page_w * h / w
    cs = {1: "/DeviceGray", 3: "/DeviceRGB", 4: "/DeviceCMYK"}[comps]
    content = f"q {page_w:.2f} 0 0 {page_h:.2f} 0 0 cm /Im0 Do Q".encode()

    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_w:.2f} {page_h:.2f}] "
        f"/Resources << /XObject << /Im0 4 0 R >> >> /Contents 5 0 R >>".encode(),
        (f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} /ColorSpace {cs} "
         f"/BitsPerComponent 8 /Filter /DCTDecode /Length {len(data)} >>\nstream\n").encode()
        + data + b"\nendstream",
        f"<< /Length {len(content)} >>\nstream\n".encode() + content + b"\nendstream",
    ]

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for n, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += f"{n} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n").encode()
    open(dst, "wb").write(out)
    print(f"{dst}: {w}x{h} px on a {page_w / 72:.1f} x {page_h / 72:.1f} in page, {len(out) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
