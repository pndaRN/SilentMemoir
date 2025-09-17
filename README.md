# SilentMemoir  
> *Your thoughts, your space, your silence.*

SilentMemoir is a minimalist, terminal-based journaling app built with [Textual](https://textual.textualize.io/). It provides a quiet, keyboard-native space for writing — no tabs, no browser, no distractions.  

---

## ✨ Features (Alpha)
- **Multiple journals**: organize writing by theme (work, travel, reflections, etc.).  
- **Custom entry titles**: name entries yourself instead of relying only on timestamps.  
- **Markdown editing & preview**: write in a text area and toggle to preview formatted Markdown.  
- **Keyboard shortcuts**:
  - `Ctrl+S` — save entry  
  - `Tab` — toggle between edit/preview  
  - `d` — delete the highlighted journal or entry  
  - `Esc` — exit screens  
- **Automatic list refresh** after creating, saving, or deleting journals and entries.  
- **Local storage only**: entries are saved as Markdown files under `~/.silentmemoir/journals/`.  
- **Quotes on launch**: a random inspirational quote when opening the app.  

---

## 🚀 Installation
SilentMemoir is distributed as a Python package. The easiest way to try it is with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install git+https://github.com/pndaRN/SilentMemoir.git
silentmemoir
```

Or, if you’ve downloaded a release wheel (`.whl`):

```bash
uv tool install silentmemoir-0.1.0a0-py3-none-any.whl
silentmemoir
```

---

## 🗂 Storage
All journals and entries are saved locally in your home directory:

```
~/.silentmemoir/journals/
```

- Journals are folders.  
- Entries are Markdown files (`.md`).  

---

## ⚠️ Current Limitations
- No sync or cloud backup — data lives only on your machine.  
- No search yet.  
- No confirmation prompt before delete.  
- UI and keyboard bindings may change before beta.  

---

## 🛠 Development
Clone and install locally for development:

```bash
git clone https://github.com/pndaRN/SilentMemoir.git
cd SilentMemoir
uv tool install .
```

Run from source:
```bash
python -m silentmemoir.main
```

---

## 📜 License
MIT  
