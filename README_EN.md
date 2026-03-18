# Dream Town Layout Design Tool

中文版本: [README.md](README.md)

A layout planning tool for the mobile game Dream Town. It supports building placement by drag-and-drop, buff calculation, road painting, layout import/export, and more. The app is fully frontend-based with no backend required, but it must be served over local HTTP (otherwise the browser will block JSON metadata loading).

> Statement: 100% of this project's code and documentation were developed by AI.
>
> Built with GitHub Copilot assistance.


## Quick Start

Start a local HTTP server in the project root:

```bash
python3 -m http.server 8000
```

Then open in your browser: `http://localhost:8000/`

---

## Feature Set

### Building Editing
- Drag buildings from the left panel to place them on the map; on mobile, tap a building first, then tap the map to place.
- Right-click a building to rotate on desktop; mobile uses the bottom action bar.
- Drag with left mouse button to move buildings; drag into the left toolbar area to delete.
- With a building selected: `Ctrl/Cmd + C` to copy, `Ctrl/Cmd + V` to paste nearby when space is available.
- `Ctrl/Cmd + A` selects all buildings on the map.
- `Backspace / Delete` removes selected buildings.
- Undo/redo supported: `Ctrl/Cmd + Z` / `Ctrl/Cmd + Y` (macOS also supports `Cmd + Shift + Z`).

### Box Selection and Batch Operations
- Drag on empty map area to box-select multiple buildings.
- Hold `Ctrl/Cmd` while clicking or box-selecting to add to current selection; click a selected building again to deselect it.
- Drag any selected building to move the whole selected group.
- Batch delete, rotate group by 90 degrees around selection center (auto-cancel on overlap/out-of-bounds), and mirror group.

### Buff and Land Value Calculation
- Click a building to view live buff details in the right panel (specialty street, statue, trophy, landscape, etc.).
- In buff source list, click an item to highlight its source building on the map.
- Land-value-source list shows nearby buildings that provide area land-value additive bonus; clicking one locates and highlights it with temporary scope effect.
- Building details include base land value, buff count, total land bonus (%), total commodity bonus (%), and area land additive bonus; buildings with `scope` show `Range: X cells, +Y`.
- Land value formula: `base_land * total_land_bonus_percent / 100 + area_land_additive_bonus`.

### Scope Visualization
- When a selected building has `scope`, its influence area is rendered as blue pulsing cells (diamond range).
- Clicking a building in the land-value-source list also triggers a temporary scope visualization (about 2 seconds).

### Road System
- Road paint mode lets you draw road cells directly on the map.
- Road validation detects whether buildings are road-connected and shows warning badges for disconnected buildings.
- Path cells can be converted into roads in one click.

### Map View Controls
- Map color toggle displays the 100x100 game map region; when enabled, placement is constrained to white cells within the 100x100 area.
- Grid line toggle (black/white), section line toggle.
- Highlight same-type buildings based on current selection.
- Filter starred/non-starred buildings in the left panel.
- Previous/next sibling controls for quick same-type selection switching.

### Map Navigation
- Zoom by mouse wheel / trackpad pinch (Windows: `Ctrl + wheel`; macOS: pinch or `Ctrl/Meta + wheel`).
- Move viewport with `W / A / S / D`; use `Shift + WASD` for faster movement.
- Real-time coordinate HUD.

### Import / Export
- Export layout as JSON, including building positions, road data, and map toggle state.
- Import layout to restore buildings, roads, and map toggle state; built-in presets are supported.
- Export image: when map color is on, export the 100x100 area; when off, export the full map, with watermark/stat info in top margin.

### Data Panels
- Building data quick lookup.
- Specialty street buff table.
- Occupation medal data.
- Store data.
- Transport/pet data.
- Rank reward references.
- Building statistics for current map.

### Other
- Automatically caches layout, zoom scale, and scroll position (local storage).
- Mobile-friendly UI with top bar, collapsible side panels, and bottom action controls.

---

## Known Limitations

- Statue/trophy/landscape bonuses are supported, but only part of the metadata is currently maintained; some buildings may have missing or incomplete calculation data.
- Dragging a building onto another existing building may overwrite original building data; avoid overlap drag operations.

---

## File Overview

| File | Description |
|------|-------------|
| `index.html` | Main app (single-file frontend) |
| `metadata/build.json` | Building metadata (name, size, land value, buffs, etc.) |
| `metadata/occupation.json` | Occupation medal data |
| `metadata/store.json` | Store data |
| `buff.json` | Specialty street buff config |
| `layouts.json` | Built-in layout list |
| `map_100x100_cells_colors.json` | Map cell color data |
| `内置布局/` | Built-in layout JSON directory |
