# AI Handover & Architecture Document
**Project:** AI-Plesh Blueprint Parser  
**Status:** Symbol detection accuracy improvement — IN PROGRESS  
**Last Updated:** 2026-03-31

---

## 🏗️ 1. Overall Architecture
The project extracts electrical symbols from architectural blueprints (PDFs) and counts their occurrences on floor plans. It uses **OpenCV**, **PyMuPDF**, **Tesseract OCR**, and **Pandas**.

### The Two-Phase Workflow

1. **Phase 1: `build_library.py` (Pre-Run)**
   - Scans `inputs/` for files starting with `"legend"` (e.g. `legend.pdf`)
   - Extracts symbol template chips → `symbol_template_images/parts_images/`
   - Extracts OCR description images → `symbol_template_images/description_images/`
   - Uses pixel-hash deduplication (`save_if_new` in `image_utils.py`)

2. **Phase 2: `analyze_floorplan.py` (Execution)**
   - Scans `inputs/` for files starting with `"floor_plan"` (e.g. `floor_plan.pdf`)
   - Uses PyMuPDF vector text analysis to auto-detect the correct page (drawing `E1-1`)
   - Renders the page at high DPI → `pages_images/image_4.png`
   - Runs `symbol_matcher.extract_symbols_and_match()` against the full floor plan
   - Outputs: `csv_files/extracted_details.csv` + `csv_files/visual_takeoff_report.png`

---

## 🧩 2. Core Modules

| Module | Purpose |
|--------|---------|
| `config.py` | Centralized paths, coordinate arrays (`LSIZE`, `USIZE`, etc.), weight mapping (`IDX`/`VAL`), Tesseract path |
| `pdf_processor.py` | PyMuPDF rendering, auto-detection of floor plan page via vector text scanning for drawing number |
| `image_utils.py` | CV2 image manipulation wrappers — whitespace splitting, filtering, `crop_building_quadrants` (currently unused) |
| `ocr_extractor.py` | Tesseract OCR wrapper, keyword location, tabular text extraction |
| `symbol_matcher.py` | **The core matching engine** — template matching, NMS, bounding box visualization, CSV export |
| `analyze_floorplan.py` | Orchestrator script — calls pdf_processor then symbol_matcher |
| `build_library.py` | Legend extraction orchestrator — builds the template library |

---

## 🔍 3. Current State of `symbol_matcher.py`

### How It Works Now
```
Floor Plan Image → Gray → Binary Threshold (>200 = white) → "floor_plan_clean"
Template Image   → Gray → Auto-Crop Padding → Binary Threshold → "template_clean"
                        → Rotate 0°, 90°, 180°, 270°
                        → cv2.matchTemplate(TM_CCOEFF_NORMED) at threshold 0.65
                        → Non-Maximum Suppression (overlap > 0.3)
                        → Scale by config.VAL weight multiplier
                        → Export to CSV
```

### Recent Changes Made (This Session)
1. **Gray Line Erasure** (line 29): `cv2.threshold(gray, 200, 255, THRESH_BINARY)` — converts light gray drafting/dimension lines to pure white so they don't interfere with matching
2. **Template Auto-Cropping** (lines 49-56): Strips excessive white padding from template images using `cv2.findNonZero` + `cv2.boundingRect` with 2px margin — prevents adjacent annotations from penalizing correlation
3. **4-Axis Rotation** (lines 64-76): Matches templates at 0°, 90°, 180°, 270° — catches symbols mounted on perpendicular walls
4. **Threshold Recalibration**: Lowered from 0.72 to 0.65 — necessary because tighter auto-crop removes the artificial white-space correlation boost
5. **PermissionError Safety** (lines 146-152): CSV export gracefully falls back to `_safe_copy.csv` if the original is locked by Excel
6. **Removed Model Isolation**: The `crop_building_quadrants` call and `ISOLATED_MODELS_DIR` were removed from the pipeline

### Weight Multiplier System
The raw match counts are multiplied by `config.VAL` weights before CSV export:
- `IDX` maps description file numbers to positions
- `VAL` applies fractional multipliers (3x, 2x, 1x, 0.5x, 0.4x, 0.9x, 0.2x, 0.1x, 0x)
- This means a raw count of 10 hits could become 2 in the CSV if the weight is 0.2

---

## ⚠️ 4. Known Issues & What Needs Fixing

### Primary Problem: Low Detection Rate for Symbols with Adjacent Geometry
**Example:** DUPLEX GROUND FAULT RECEPTACLE — only 3 detections, should be ~15+

**Root Cause Analysis:**
- The symbol on the blueprint often has a `+` (plus sign) physically adjacent or overlapping its bounding box
- `cv2.matchTemplate(TM_CCOEFF_NORMED)` is a rigid pixel-grid correlator — ANY extra black pixels inside the template's search window penalize the score
- Top correlation scores for this symbol: 0.708, 0.67, 0.66 — the plus-sign adjacency drags scores below the 0.65 threshold
- The 4-axis rotation helped find raw matches (796 candidates at 0.65) but NMS aggressively suppresses most, and many are false positives from other similar shapes

**Recommended Fix Approaches:**
1. **Feature-Based Matching (SIFT/ORB)**: Match keypoints instead of rigid pixel grids — inherently tolerant of adjacent geometry
2. **Template Mask**: Create a circular/elliptical mask for each template so only the core symbol shape participates in correlation, ignoring surrounding annotations
3. **Multiple Template Variants**: For high-value symbols, store 2-3 template variants (bare symbol, symbol+plus, symbol+text) and union their detections
4. **Adaptive Per-Symbol Thresholds**: Instead of global 0.65, calibrate per-template based on their specific score distribution

### Secondary Issues
- **Execution Time**: 4-axis rotation quadrupled runtime from ~30s to ~112s
- **False Positive Risk**: Lower threshold (0.65) + rotations may over-count simpler/smaller symbols
- **OCR Sensitivity**: Tesseract description extraction is sensitive to overlapping structural lines

---

## 📂 5. Directory Structure
```text
modular_parser/
├── inputs/                      ← User drops 'legend.*' and 'floor_plan.*' here
├── symbol_template_images/
│   ├── parts_images/            ← Symbol template chips (.png) — ~40 files
│   └── description_images/      ← OCR text bounds for each symbol
├── pages_images/                ← Rendered PDF pages (image_4.png = floor plan)
├── csv_files/
│   ├── extracted_details.csv    ← Final symbol count output
│   ├── visual_takeoff_report.png ← Annotated floor plan with bounding boxes
│   └── diagnostic_clean_background.png ← Gray-line-erased floor plan
│
├── analyze_floorplan.py         ← Main entry point
├── build_library.py             ← Legend extraction entry point
├── config.py                    ← All paths, arrays, weights
├── image_utils.py               ← CV2 image manipulation utilities
├── ocr_extractor.py             ← Tesseract OCR wrapper
├── pdf_processor.py             ← PyMuPDF page rendering
├── symbol_matcher.py            ← Core matching engine (MODIFY THIS)
└── AI_HANDOVER.md               ← This file
```

---

## 🚀 6. How to Resume Work

### Immediate Priority: Fix Symbol Detection Accuracy
1. Open `symbol_matcher.py` — all matching logic is in `extract_symbols_and_match()`
2. The user's specific complaint: symbols with adjacent `+` signs are missed
3. Look at the template images in `symbol_template_images/parts_images/` to understand the shapes
4. The `visual_takeoff_report.png` shows colored bounding boxes on detected symbols — use it to visually verify

### Quick Commands
```bash
# Run the full pipeline
python analyze_floorplan.py

# Rebuild symbol library from legend
python build_library.py
```

### Dependencies
- Python 3.x, OpenCV (`cv2`), NumPy, Pandas, Pillow, PyMuPDF (`fitz`), pytesseract
- Tesseract OCR installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`

### Key Config Values to Know
- `TARGET_FLOOR_PLAN_DRAWING = "E1-1"` — which drawing to auto-detect in the PDF
- `match_threshold = 0.65` in `symbol_matcher.py` line 65 — global correlation cutoff
- NMS overlap threshold = `0.3` in `symbol_matcher.py` line 103
- `config.VAL` weight multipliers scale raw counts before CSV export
