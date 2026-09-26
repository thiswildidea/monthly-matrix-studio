# -*- coding: utf-8 -*-
"""生成 monthly-matrix-studio 专属图标 app.ico（纯标准库，不依赖 Pillow）。

本文件是「月度矩阵工作室」专用，与同仓库其他工作室的 gen_icon.py 不是同一份。
图案是应用的核心可视化——月度涨跌矩阵（月 × 标的的方格热力图），
配色取自应用 CSS：--bg:#070b16 / --panel:#0e1526，涨 #ef4444 / 跌 #22c55e /
高位 #0ea5e9、高亮 #fbbf24，未填格用 --line 灰。

给别的应用做图标时请改动 MATRIX / PALETTE，别直接复制本文件。
"""

import struct
import sys
import zlib
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SIZE = 256
OUT = Path(__file__).parent / "app.ico"
APP_TAG = "月度矩阵工作室"

BG = (7, 11, 22)        # --bg #070b16
FRAME = (48, 63, 90)    # --line 实色近似
PANEL_BG = (15, 23, 42)  # --panel

# 格子色档：0=浅涨 1=涨 2=强涨 3=浅跌 4=跌(绿) 5=强跌(绿) 6=高位(蓝) 7=高亮(琥珀)
PALETTE = {
    0: (252, 165, 165),   # #fca5a5 浅涨
    1: (239, 68, 68),     # #ef4444 涨
    2: (185, 28, 28),     # 强涨
    3: (187, 247, 208),   # #bbf7d0 浅跌
    4: (34, 197, 94),     # #22c55e 跌
    5: (21, 128, 61),     # 强跌
    6: (14, 165, 233),    # #0ea5e9 高位
    7: (251, 191, 36),    # #fbbf24 高亮
}
MATRIX = [
    [3, 0, 4, 6, 1, 3, 5, 6, 0, 3],
    [1, 6, 1, 0, 4, 6, 1, 3, 4, 6],
    [4, 1, 6, 1, 0, 5, 6, 0, 1, 1],
    [0, 3, 1, 6, 3, 1, 0, 4, 6, 0],
    [6, 4, 0, 1, 6, 0, 3, 1, 3, 4],
    [1, 0, 3, 4, 1, 6, 1, 6, 0, 1],
    [3, 6, 1, 0, 6, 1, 4, 0, 6, 7],
    [0, 1, 4, 3, 0, 4, 6, 1, 1, 6],
]


def rounded_alpha(x, y, size, radius):
    cx = min(max(x, radius), size - radius)
    cy = min(max(y, radius), size - radius)
    dx, dy = x - cx, y - cy
    d = (dx * dx + dy * dy) ** 0.5
    return max(0.0, min(1.0, radius - d + 0.5))


def build_pixels():
    # 外框（模拟面板）
    fl, fr = 30, 226
    ft, fb = 40, 216
    border = 2.0

    # 矩阵格子区域
    gl, gr = 46, 210
    gt, gb = 70, 186
    rows_n, cols_n = len(MATRIX), len(MATRIX[0])
    gap = 4.0
    cw = ((gr - gl) - gap * (cols_n - 1)) / cols_n
    ch = ((gb - gt) - gap * (rows_n - 1)) / rows_n

    rows = []
    for y in range(SIZE):
        row = bytearray()
        for x in range(SIZE):
            px, py = x + 0.5, y + 0.5
            r, g, b = BG

            if fl <= px <= fr and ft <= py <= fb:
                near = min(px - fl, fr - px, py - ft, fb - py) < border
                r, g, b = FRAME if near else PANEL_BG

            ci = int((px - gl) // (cw + gap))
            ri = int((py - gt) // (ch + gap))
            if 0 <= ri < rows_n and 0 <= ci < cols_n:
                x0 = gl + ci * (cw + gap)
                y0 = gt + ri * (ch + gap)
                if x0 <= px <= x0 + cw and y0 <= py <= y0 + ch:
                    r, g, b = PALETTE[MATRIX[ri][ci]]

            a = int(255 * rounded_alpha(px, py, SIZE, 52))
            row += bytes((r, g, b, a))
        rows.append(bytes(row))
    return rows


def png_bytes(rows):
    raw = b"".join(b"\x00" + r for r in rows)

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def main():
    png = png_bytes(build_pixels())
    header = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack("<BBBBHHII", 0, 0, 0, 0, 1, 32, len(png), 22)
    OUT.write_bytes(header + entry + png)
    print(f"{APP_TAG}: 已生成 {OUT.name}  ({OUT.stat().st_size:,} 字节, 内嵌 PNG {len(png):,} 字节)")


if __name__ == "__main__":
    main()
