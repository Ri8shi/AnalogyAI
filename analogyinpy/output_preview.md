# RepoExplainer Output Preview
**Repo:** `https://github.com/Ri8shi/pngtojpgconverter`

## Visual Mockup

Streamlit app output for pngtojpgconverter repo

---

## Exact Output Data (from real repo files)

Below is what each section would display, computed from the actual repo contents:

---

### Metrics Row (6 columns)

| Directories | Total Files | Files Sent to AI | Total LOC | Languages | Est. Tokens |
|:-----------:|:-----------:|:----------------:|:---------:|:---------:|:-----------:|
| 0 | 3 | 2 | ~107 | 2 | ~620 |



---

### Language Breakdown (expander)
```
  Python                  1 files  (33.3%)
  Markdown                1 files  (33.3%)
```
`.gitattributes` has no mapped language.

---

### Largest Files (top 10) (expander)
```
  README.md                                               1.6 KB
  pngtojpg.py                                             1.6 KB
  .gitattributes                                          0.1 KB
```

---

### File Tree (expander)
```
      .gitattributes
      README.md
      pngtojpg.py
```
No directories — it's a flat repo.

---

### Files Analyzed (2) (expander)

**Files sent to Gemini:**
1. `README.md` (priority file) — 1,607 chars → truncated to 600 chars
2. `pngtojpg.py` (code file) — 1,590 chars → truncated to 600 chars

**Files NOT sent:** `.gitattributes` (not code, not priority)

---

### Repository Explanation (AI-generated)

This is what Gemini would return (simulated based on actual code):

---

## Overview
A lightweight Python GUI tool that converts PNG images to JPG format using Tkinter and Pillow (PIL).

## Tech Stack
- **Python** — Core language
- **Tkinter** — Built-in GUI framework
- **Pillow (PIL)** — Image processing & format conversion

## Structure
Simple flat repo with a single Python script and README.

## Key Components
- **`pngtojpg.py`** — Main application: GUI window + conversion logic
- **`README.md`** — Project docs, installation, usage

## How It Works
1. User launches the Tkinter GUI window (400×250, dark theme)
2. Clicks **"Select PNG File"** button → file dialog opens
3. PIL opens the PNG and converts to RGB mode
4. User picks save location → image saved as JPEG
5. Success/error messagebox shown

## Setup
```bash
pip install pillow
python pngtojpg.py
```

---

### Footer Caption
```
Prompt: ~2,480 chars / ~620 tokens | Response: 2.3s
```

<!-- ---

## Token Usage Comparison

| | Old Code | New Code | Savings |
|---|---|---|---|
| **Files sent** | 3 (all) | 2 (skip .gitattributes) | 33% fewer |
| **Chars per file** | 1,500 max | 600 max | 60% fewer |
| **Total chars cap** | 25,000 | 8,000 | 68% fewer |
| **Tree in prompt** | All files+dirs | Dirs only | ~50% fewer tree tokens |
| **System instruction** | 3 sentences | 6 words | ~80% fewer |
| **Output tokens cap** | 1,500 | 800 | 47% fewer |
| **Model cached** | No | Yes (@st.cache_resource) | No re-init |
| **Download cached** | No | Yes (@st.cache_data) | No re-download |
| **Prompt built** | Twice | Once | 50% compute saved |
 -->
