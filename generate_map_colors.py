from pathlib import Path
import json
import png

IMG_PATH = Path("map.png")
OUT_PATH = Path("map_100x100_cells_colors.json")
COLS = 100
ROWS = 100
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def median(values):
    values.sort()
    return values[len(values) // 2]


reader = png.Reader(filename=str(IMG_PATH))
width, height, rows, info = reader.read()
planes = info["planes"]
has_alpha = info.get("alpha", False)
rows = list(rows)


def get_rgb(x, y):
    row = rows[y]
    base = x * planes
    r = row[base]
    g = row[base + 1]
    b = row[base + 2]
    if has_alpha and planes >= 4:
        a = row[base + 3]
        if a == 0:
            return 255, 255, 255
    return r, g, b

cell_w = width / COLS
cell_h = height / ROWS

grid_colors = []
for y in range(ROWS):
    row_colors = []
    y0 = int(round(y * cell_h))
    y1 = int(round((y + 1) * cell_h))
    if y1 <= y0:
        y1 = y0 + 1

    pad_y = max(1, int((y1 - y0) * 0.2))
    sy0 = y0 + pad_y
    sy1 = y1 - pad_y
    if sy1 <= sy0:
        sy0, sy1 = y0, y1

    for x in range(COLS):
        x0 = int(round(x * cell_w))
        x1 = int(round((x + 1) * cell_w))
        if x1 <= x0:
            x1 = x0 + 1

        pad_x = max(1, int((x1 - x0) * 0.2))
        sx0 = x0 + pad_x
        sx1 = x1 - pad_x
        if sx1 <= sx0:
            sx0, sx1 = x0, x1

        rs, gs, bs = [], [], []
        for yy in range(sy0, min(sy1, height)):
            for xx in range(sx0, min(sx1, width)):
                r, g, b = get_rgb(xx, yy)
                rs.append(r)
                gs.append(g)
                bs.append(b)

        if rs:
            r = median(rs)
            g = median(gs)
            b = median(bs)
        else:
            cx = min(max(int((x + 0.5) * cell_w), 0), width - 1)
            cy = min(max(int((y + 0.5) * cell_h), 0), height - 1)
            r, g, b = get_rgb(cx, cy)

        row_colors.append(f"#{r:02X}{g:02X}{b:02X}")

    grid_colors.append(row_colors)

palette = []
palette_index = {}
for row_colors in grid_colors:
    for color in row_colors:
        if color not in palette_index:
            palette_index[color] = len(palette)
            palette.append(color)

if len(palette) > len(ALPHABET):
    raise RuntimeError(f"Palette too large for symbol bitmap encoding: {len(palette)} colors")

bitmap = []
for row_colors in grid_colors:
    bitmap.append("".join(ALPHABET[palette_index[color]] for color in row_colors))

payload = {
    "sourceImage": str(IMG_PATH),
    "imageSize": {"width": width, "height": height},
    "grid": {"cols": COLS, "rows": ROWS},
    "encoding": {
        "type": "palette-symbol-bitmap",
        "symbolMeaning": "bitmap[y][x] -> palette[symbolMap[symbol]]",
        "palette": palette,
        "symbolMap": {ALPHABET[index]: color for index, color in enumerate(palette)},
    },
    "bitmap": bitmap,
}

OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"written {OUT_PATH}")
print(f"rows {len(bitmap)}")
print(f"cols {len(bitmap[0]) if bitmap else 0}")
print(f"palette {len(palette)}")
