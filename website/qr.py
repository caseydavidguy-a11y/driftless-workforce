#!/usr/bin/env python3
"""Print-ready QR codes for Driftless business cards and job flyers.

  python3 qr.py https://example.com/            -> qr/site.svg, qr/site.png (1200 px), checked by scanning it back
  python3 qr.py https://example.com/jobs/cnc.html cnc-machinist

Uses error correction level M and a 4-module quiet zone, which is what printers expect.
At 0.75 in (19 mm) or larger on a business card it scans from a phone at arm's length.
"""
import os, sys
import cv2
from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel

INK = '#241c13'


def matrix(url):
    q = QRCode(None, QRErrorCorrectLevel.M)
    q.addData(url)
    q.make()
    n = q.getModuleCount()
    return [[bool(q.isDark(r, c)) for c in range(n)] for r in range(n)]


def to_svg(m, quiet=4):
    n = len(m) + quiet * 2
    path = []
    for r, row in enumerate(m):
        c = 0
        while c < len(row):
            if row[c]:
                start = c
                while c < len(row) and row[c]:
                    c += 1
                path.append(f'M{start + quiet} {r + quiet}h{c - start}v1h{start - c}z')
            else:
                c += 1
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" shape-rendering="crispEdges">'
            f'<rect width="{n}" height="{n}" fill="#ffffff"/><path fill="{INK}" d="{"".join(path)}"/></svg>')


def to_png(m, path, size=1200, quiet=4):
    import numpy as np
    n = len(m) + quiet * 2
    scale = max(1, size // n)
    img = np.full((n * scale, n * scale), 255, dtype=np.uint8)
    for r, row in enumerate(m):
        for c, on in enumerate(row):
            if on:
                img[(r + quiet) * scale:(r + quiet + 1) * scale, (c + quiet) * scale:(c + quiet + 1) * scale] = 0x24
    cv2.imwrite(path, img)
    return img


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    url = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else 'site'
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qr')
    os.makedirs(out, exist_ok=True)
    m = matrix(url)
    with open(os.path.join(out, name + '.svg'), 'w') as fh:
        fh.write(to_svg(m))
    png = os.path.join(out, name + '.png')
    img = to_png(m, png)
    got, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    if got != url:
        sys.exit(f'Scan check FAILED: decoded {got!r}')
    print(f'{name}: {len(m)}x{len(m)} modules, scan check OK -> {png}')


if __name__ == '__main__':
    main()
