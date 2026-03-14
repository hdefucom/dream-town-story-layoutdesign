from __future__ import annotations

import argparse
import json
from pathlib import Path

import png

IMG_PATH = Path("map.png")
OUT_PATH = Path("map_100x100_cells_colors.json")
COLS = 100
ROWS = 100
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.strip().lstrip("#")
    if len(color) != 6:
        raise ValueError(f"invalid color: {color}")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"#{r:02X}{g:02X}{b:02X}"


def dist2(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def nearest_palette_index(rgb: tuple[int, int, int], palette_rgb: list[tuple[int, int, int]]) -> int:
    best_idx = 0
    best_d2 = dist2(rgb, palette_rgb[0])
    for i in range(1, len(palette_rgb)):
        d2 = dist2(rgb, palette_rgb[i])
        if d2 < best_d2:
            best_d2 = d2
            best_idx = i
    return best_idx


def load_image(path: Path):
    reader = png.Reader(filename=str(path))
    width, height, png_rows, info = reader.read()
    planes = info["planes"]
    has_alpha = info.get("alpha", False)
    return width, height, list(png_rows), planes, has_alpha


def get_rgb(rows_data, planes: int, has_alpha: bool, x: int, y: int) -> tuple[int, int, int]:
    row = rows_data[y]
    base = x * planes
    r = row[base]
    g = row[base + 1]
    b = row[base + 2]
    if has_alpha and planes >= 4:
        a = row[base + 3]
        if a == 0:
            return 255, 255, 255
    return r, g, b


def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(v, hi))


def build_bitmap(
    width: int,
    height: int,
    rows_data,
    planes: int,
    has_alpha: bool,
    cols: int,
    rows: int,
    palette_rgb: list[tuple[int, int, int]],
    sample_pad_ratio: float,
) -> list[str]:
    cell_w = width / cols
    cell_h = height / rows
    bitmap: list[str] = []

    for gy in range(rows):
        y0 = int(round(gy * cell_h))
        y1 = int(round((gy + 1) * cell_h))
        if y1 <= y0:
            y1 = y0 + 1

        pad_y = max(0, int((y1 - y0) * sample_pad_ratio))
        sy0 = clamp(y0 + pad_y, 0, height - 1)
        sy1 = clamp(y1 - pad_y, sy0 + 1, height)

        row_symbols = []
        for gx in range(cols):
            x0 = int(round(gx * cell_w))
            x1 = int(round((gx + 1) * cell_w))
            if x1 <= x0:
                x1 = x0 + 1

            pad_x = max(0, int((x1 - x0) * sample_pad_ratio))
            sx0 = clamp(x0 + pad_x, 0, width - 1)
            sx1 = clamp(x1 - pad_x, sx0 + 1, width)

            # 对每个格子做“近色分类 + 多数投票”，可抗文字与锯齿噪声
            counts = [0] * len(palette_rgb)
            for py in range(sy0, sy1):
                for px in range(sx0, sx1):
                    rgb = get_rgb(rows_data, planes, has_alpha, px, py)
                    idx = nearest_palette_index(rgb, palette_rgb)
                    counts[idx] += 1

            if sum(counts) == 0:
                cx = clamp(int((gx + 0.5) * cell_w), 0, width - 1)
                cy = clamp(int((gy + 0.5) * cell_h), 0, height - 1)
                idx = nearest_palette_index(get_rgb(rows_data, planes, has_alpha, cx, cy), palette_rgb)
            else:
                idx = max(range(len(counts)), key=lambda i: counts[i])

            row_symbols.append(ALPHABET[idx])

        bitmap.append("".join(row_symbols))

    return bitmap


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate 100x100 map color bitmap from map.png")
    parser.add_argument("--input", type=Path, default=IMG_PATH, help="input image path")
    parser.add_argument("--output", type=Path, default=OUT_PATH, help="output json path")
    parser.add_argument("--cols", type=int, default=COLS, help="grid columns")
    parser.add_argument("--rows", type=int, default=ROWS, help="grid rows")
    parser.add_argument(
        "--palette",
        nargs="+",
        default=["#7030A0", "#9BC2E6", "#FFFFFF"],
        help="target palette, e.g. --palette #7030A0 #9BC2E6 #FFFFFF",
    )
    parser.add_argument(
        "--sample-pad-ratio",
        type=float,
        default=0.15,
        help="inner sampling padding ratio of each cell (0~0.45)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sample_pad_ratio = float(args.sample_pad_ratio)
    if not (0 <= sample_pad_ratio < 0.45):
        raise ValueError("sample-pad-ratio must be in [0, 0.45)")

    width, height, rows_data, planes, has_alpha = load_image(args.input)
    palette_rgb = [hex_to_rgb(c) for c in args.palette]
    if len(palette_rgb) > len(ALPHABET):
        raise RuntimeError(f"palette too large for symbol encoding: {len(palette_rgb)}")

    bitmap = build_bitmap(
        width=width,
        height=height,
        rows_data=rows_data,
        planes=planes,
        has_alpha=has_alpha,
        cols=args.cols,
        rows=args.rows,
        palette_rgb=palette_rgb,
        sample_pad_ratio=sample_pad_ratio,
    )

    palette = [rgb_to_hex(c) for c in palette_rgb]
    symbol_map = {ALPHABET[i]: palette[i] for i in range(len(palette))}

    payload = {
        "sourceImage": str(args.input),
        "imageSize": {"width": width, "height": height},
        "grid": {"cols": args.cols, "rows": args.rows},
        "encoding": {
            "type": "palette-symbol-bitmap",
            "symbolMeaning": "bitmap[y][x] -> palette[symbolMap[symbol]]",
            "palette": palette,
            "symbolMap": symbol_map,
        },
        "bitmap": bitmap,
    }

    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"written {args.output}")
    print(f"source {args.input} ({width}x{height})")
    print(f"grid {args.cols}x{args.rows}")
    print(f"palette {len(palette)}: {palette}")
    print(f"bitmap rows {len(bitmap)} cols {len(bitmap[0]) if bitmap else 0}")


if __name__ == "__main__":
    main()
