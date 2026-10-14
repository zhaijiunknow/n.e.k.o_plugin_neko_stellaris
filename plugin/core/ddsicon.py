# -*- coding: utf-8 -*-
# Copyright 2025-2026 Project N.E.K.O. Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""Write the advisor icon as an uncompressed BGRA DDS.

The game's advisor icons are *not* DXT-compressed: every file in
``gfx/interface/icons/advisor_vo`` is exactly 3492 bytes = 128-byte header +
29*29*4, with ``pfFlags = 0x41`` (ALPHAPIXELS|RGB), ``rgbBits = 32``, masks
``00FF0000/0000FF00/000000FF/FF000000`` and no mipmaps. Writing that same shape
by hand avoids a DDS encoder dependency and guarantees the game sees a format it
already ships.

The artwork is a small procedural "neko" mark: a rounded head, two ears, two
eyes and a highlight, drawn with 4x4 supersampling so the 29px edges are not
jagged. It is deliberately simple — the icon renders at ~29 device pixels in the
voice-selection list, where anything finer is invisible.
"""

from __future__ import annotations

import struct
from pathlib import Path

DEFAULT_SIZE = 29
_SUPERSAMPLE = 4

# N.E.K.O palette: a cool cyan-to-violet head with warm highlights.
_HEAD_TOP = (0.55, 0.86, 0.98)     # light cyan
_HEAD_BOTTOM = (0.42, 0.55, 0.92)  # soft violet-blue
_EAR_INNER = (0.98, 0.72, 0.82)    # pink
_EYE = (0.16, 0.19, 0.31)
_HIGHLIGHT = (1.0, 1.0, 1.0)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _inside_circle(x: float, y: float, cx: float, cy: float, r: float) -> bool:
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def _inside_triangle(px: float, py: float,
                     ax: float, ay: float, bx: float, by: float,
                     cx: float, cy: float) -> bool:
    def sign(x1, y1, x2, y2, x3, y3):
        return (x1 - x3) * (y2 - y3) - (x2 - x3) * (y1 - y3)

    d1 = sign(px, py, ax, ay, bx, by)
    d2 = sign(px, py, bx, by, cx, cy)
    d3 = sign(px, py, cx, cy, ax, ay)
    has_neg = d1 < 0 or d2 < 0 or d3 < 0
    has_pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (has_neg and has_pos)


def _sample(x: float, y: float, size: int) -> tuple[float, float, float, float]:
    """Return premultiplied-free (r, g, b, a) for one sample point, 0..1."""
    unit = size / 29.0
    cx = 14.5 * unit
    head_cy = 16.5 * unit
    head_r = 10.2 * unit

    # Ears first: they must be filled *before* the head so the head circle can
    # round off their bases. Painting the head first would erase the ear tips.
    ear_h = 7.6 * unit
    for side in (-1, 1):
        tipx = cx + side * 6.4 * unit
        tipy = 5.0 * unit
        base_y = 12.5 * unit
        base_in = cx + side * 1.9 * unit
        base_out = cx + side * 9.2 * unit
        if _inside_triangle(x, y, tipx, tipy, base_in, base_y, base_out, base_y):
            inner = _inside_triangle(
                x, y,
                tipx + side * -1.2 * unit, tipy + 2.6 * unit,
                base_in + side * 1.5 * unit, base_y - 1.2 * unit,
                base_out - side * 1.4 * unit, base_y - 1.2 * unit,
            )
            base = _EAR_INNER if inner else (
                _lerp(_HEAD_TOP[0], _HEAD_BOTTOM[0], 0.1),
                _lerp(_HEAD_TOP[1], _HEAD_BOTTOM[1], 0.1),
                _lerp(_HEAD_TOP[2], _HEAD_BOTTOM[2], 0.1),
            )
            return base[0], base[1], base[2], 1.0

    if _inside_circle(x, y, cx, head_cy, head_r):
        t = (y - (head_cy - head_r)) / (2 * head_r)
        t = min(1.0, max(0.0, t))
        col = (_lerp(_HEAD_TOP[0], _HEAD_BOTTOM[0], t),
               _lerp(_HEAD_TOP[1], _HEAD_BOTTOM[1], t),
               _lerp(_HEAD_TOP[2], _HEAD_BOTTOM[2], t))
        # Eyes sit below the vertical centre so the face reads as a face.
        for side in (-1, 1):
            if _inside_circle(x, y, cx + side * 3.5 * unit, head_cy + 0.4 * unit,
                              1.75 * unit):
                return _EYE[0], _EYE[1], _EYE[2], 1.0
            if _inside_circle(x, y, cx + side * 3.5 * unit - 0.5 * unit,
                              head_cy + 0.4 * unit, 0.55 * unit):
                return _HIGHLIGHT[0], _HIGHLIGHT[1], _HIGHLIGHT[2], 1.0
        # A small muzzle dot, offset low, keeps the silhouette from reading as a
        # plain smiley at 29px.
        if _inside_circle(x, y, cx, head_cy + 4.4 * unit, 0.9 * unit):
            return _EAR_INNER[0], _EAR_INNER[1], _EAR_INNER[2], 1.0
        return col[0], col[1], col[2], 1.0

    return 0.0, 0.0, 0.0, 0.0


def render_bgra(size: int = DEFAULT_SIZE) -> bytes:
    """Render the icon and return raw BGRA rows (top-down), 4 bytes per pixel."""
    step = 1.0 / _SUPERSAMPLE
    offset = step / 2.0
    out = bytearray(size * size * 4)
    for py in range(size):
        for px in range(size):
            r = g = b = a = 0.0
            for sy in range(_SUPERSAMPLE):
                for sx in range(_SUPERSAMPLE):
                    sr, sg, sb, sa = _sample(px + offset + sx * step,
                                             py + offset + sy * step, size)
                    r += sr * sa
                    g += sg * sa
                    b += sb * sa
                    a += sa
            n = _SUPERSAMPLE * _SUPERSAMPLE
            alpha = a / n
            if alpha > 0:
                # DDS expects straight (non-premultiplied) alpha.
                r, g, b = r / a, g / a, b / a
            idx = (py * size + px) * 4
            out[idx + 0] = int(min(255, max(0, round(b * 255))))
            out[idx + 1] = int(min(255, max(0, round(g * 255))))
            out[idx + 2] = int(min(255, max(0, round(r * 255))))
            out[idx + 3] = int(min(255, max(0, round(alpha * 255))))
    return bytes(out)


def build_dds(size: int = DEFAULT_SIZE) -> bytes:
    """Complete uncompressed BGRA DDS payload matching the vanilla advisor icons."""
    if size <= 0 or size > 512:
        raise ValueError(f"unsupported icon size {size}")
    pixels = render_bgra(size)
    header = bytearray(128)
    header[0:4] = b"DDS "
    struct.pack_into("<I", header, 4, 124)                 # dwSize
    struct.pack_into("<I", header, 8, 0x0000100F)          # CAPS|HEIGHT|WIDTH|PIXELFORMAT|PITCH
    struct.pack_into("<I", header, 12, size)               # dwHeight
    struct.pack_into("<I", header, 16, size)               # dwWidth
    struct.pack_into("<I", header, 20, size * 4)           # dwPitchOrLinearSize
    struct.pack_into("<I", header, 24, 0)                  # dwDepth
    struct.pack_into("<I", header, 28, 0)                  # dwMipMapCount
    struct.pack_into("<I", header, 76, 32)                 # ddspf.dwSize
    struct.pack_into("<I", header, 80, 0x41)               # ALPHAPIXELS | RGB
    struct.pack_into("<I", header, 84, 0)                  # no FourCC
    struct.pack_into("<I", header, 88, 32)                 # dwRGBBitCount
    struct.pack_into("<I", header, 92, 0x00FF0000)         # R
    struct.pack_into("<I", header, 96, 0x0000FF00)         # G
    struct.pack_into("<I", header, 100, 0x000000FF)        # B
    struct.pack_into("<I", header, 104, 0xFF000000)        # A
    struct.pack_into("<I", header, 108, 0x00001000)        # DDSCAPS_TEXTURE
    return bytes(header) + pixels


def write_dds(path: str | Path, size: int = DEFAULT_SIZE) -> int:
    """Write the icon and return its size in bytes."""
    payload = build_dds(size)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    return len(payload)
