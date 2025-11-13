# CLAUDE.md - AI Assistant Guide for SilentMemoir

> **Last Updated:** 2025-11-13
> **Version:** 0.1.0a3
> **Status:** Alpha Development

This document provides comprehensive guidance for AI assistants working on the SilentMemoir codebase.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Structure](#codebase-structure)
3. [Architecture & Design Patterns](#architecture--design-patterns)
4. [Development Workflow](#development-workflow)
5. [Code Conventions](#code-conventions)
6. [Testing Guidelines](#testing-guidelines)
7. [Key Files Reference](#key-files-reference)
8. [Common Tasks](#common-tasks)
9. [Troubleshooting](#troubleshooting)

---

## Project Overview

**SilentMemoir** is a minimalist, terminal-based journaling application built with [Textual](https://textual.textualize.io/), a modern Python TUI (Text User Interface) framework.

### Core Mission
Provide a distraction-free, keyboard-native journaling experience directly in the terminal without cloud dependencies, tabs, or browser-based interfaces.

### Key Statistics
- **Language:** Python 3.9+
- **Lines of Code:** ~519 lines (core application)
- **Main Dependencies:** Textual >=5.3.0, PyFiglet >=1.0.4
- **License:** MIT
- **Development Stage:** Alpha (0.1.0a3)

### Primary Features
- Multiple journal organization
- Custom entry titles with auto-timestamping
- Markdown editing with live preview toggle
- Keyboard-driven navigation (no mouse required)
- Local-only file storage (`~/.silentmemoir/journals/`)
- Dark/light theme support
- Inspirational quotes on launch

### Known Limitations
- No cloud sync/backup
- No search functionality (yet)
- No deletion confirmation prompts
- UI refinement ongoing

---

## Codebase Structure

```
SilentMemoir/
├── .github/
│   └── workflows/
│       └── ci.yml                    # CI/CD pipeline (test matrix + releases)
├── src/silentmemoir/                 # Main source code
│   ├── __init__.py                   # Package initialization
│   ├── main.py                       # Application entry point (32 lines)
│   ├── assets/
│   │   └── css.tcss                  # Textual CSS styling (151 lines)
│   ├── data/
│   │   ├── __init__.py
│   │   └── quotes.py                 # Inspirational quotes database (14 lines)
│   └── screens/
│       ├── __init__.py
│       ├── opening_screen.py         # Splash screen with quotes (39 lines)
│       ├── view_journals.py          # Journal/entry management (274 lines)
│       └── entry.py                  # Markdown editor with preview (196 lines)
├── .gitignore                        # Standard Python ignores
├── .python-version                   # Python 3.12
├── pyproject.toml                    # Project metadata & configuration
├── uv.lock                           # Locked dependencies (UV package manager)
└── README.md                         # User-facing documentation
```

### File Responsibilities

| File | Purpose | Lines | Key Classes/Functions |
|------|---------|-------|----------------------|
| `main.py` | App initialization & theme toggle | 32 | `SilentMemoir(App)`, `run()` |
| `opening_screen.py` | Splash screen with rotating quotes | 39 | `OpeningScreen(Screen)` |
| `view_journals.py` | Two-panel journal/entry browser | 274 | `Journal`, `ViewJournals`, `NewJournal`, `JournalListItem`, `EntryListItem` |
| `entry.py` | Dual-mode Markdown editor | 196 | `JournalEntry`, `Entry` |
| `quotes.py` | Static quote database | 14 | `QUOTES` list |
| `css.tcss` | TUI styling rules | 151 | N/A (CSS-like syntax) |

---

## Architecture & Design Patterns

### Application Architecture

**Pattern:** Multi-screen Textual application with modal overlays

```
┌─────────────────────────────────────────┐
│   SilentMemoir App (main.py)            │
│   - Loads CSS from assets/css.tcss      │
│   - Registers screens                   │
│   - Manages theme toggle                │
└────────────┬────────────────────────────┘
             │
             ├─→ OpeningScreen (opening_screen.py)
             │   - ASCII art title (PyFiglet)
             │   - Random quote display
             │   - Press 'e' to enter app
             │
             └─→ ViewJournals (view_journals.py)
                 - Two-panel layout (journals | entries)
                 - Keyboard navigation (h/n/d/arrows/Enter)
                 - Modal dialogs for new journals
                 │
                 └─→ Entry Modal (entry.py)
                     - Edit mode (TextArea)
                     - Preview mode (Markdown)
                     - Tab to toggle, Ctrl+S to save
```

### Data Flow

```
User Input (Keyboard)
    ↓
Textual Event Handlers (on_key, on_button_pressed, etc.)
    ↓
Data Models (Journal, JournalEntry)
    ↓
File System (~/.silentmemoir/journals/)
    ↓
UI Updates (ListView refresh, screen transitions)
```

### Key Design Patterns

1. **Screen-Based Navigation**
   - Textual's `Screen` abstraction separates concerns
   - `app.push_screen()` for modals, `app.pop_screen()` to return
   - Screens are registered in `main.py:SCREENS`

2. **Data Models as Pure Logic**
   - `Journal` class (view_journals.py:11-64): Handles journal CRUD operations
   - `JournalEntry` class (entry.py:18-68): Manages entry read/write
   - Models are filesystem-backed (no database)

3. **Custom Widgets**
   - `JournalListItem`, `EntryListItem`: Extend Textual's `ListItem`
   - Enables metadata storage (new vs. existing entries)

4. **Callback-Based Modals**
   - Entry editor accepts `callback` parameter
   - After save, executes callback to refresh parent screen

### File Storage Schema

```
~/.silentmemoir/journals/
├── Work Journal/                  # Journal = directory
│   ├── entry_2025-11-13_09-30-15.md
│   ├── Sprint Planning.md         # Custom title
│   └── Retrospective.md
├── Travel/
│   └── Tokyo Trip.md
└── Personal/
    └── entry_2025-11-12_20-45-00.md
```

**Rules:**
- Journal names become directory names
- Entry filenames: `entry_YYYY-MM-DD_HH-MM-SS.md` (auto) or custom title
- All entries are plain Markdown (`.md`)

---

## Development Workflow

### Initial Setup

```bash
# Clone repository
git clone https://github.com/pndaRN/SilentMemoir.git
cd SilentMemoir

# Install UV package manager (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync

# Run from source
python -m silentmemoir.main

# Or install as tool
uv tool install .
silentmemoir
```

### Branch Strategy

- **Main branch:** Stable releases
- **Develop branch:** Integration branch for features
- **Claude branches:** AI-assisted development (prefix: `claude/`)
- **Feature branches:** Use descriptive names (`feature/search-functionality`)

### Making Changes

1. **Create or switch to feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make code changes** following conventions (see below)

3. **Lint code** (must pass before commit)
   ```bash
   uv run ruff check src/
   ```

4. **Test manually** (no automated tests yet)
   ```bash
   python -m silentmemoir.main
   ```

5. **Build package** (verify no build errors)
   ```bash
   uv build
   ```

6. **Commit with clear messages**
   ```bash
   git add .
   git commit -m "Add: search functionality for journal entries"
   ```

7. **Push to remote**
   ```bash
   git push -u origin feature/your-feature-name
   ```

### CI/CD Pipeline

**Trigger:** Push to `main`/`develop` or PR to `main`

**Test Matrix:**
- **OS:** Ubuntu, Windows, macOS
- **Python:** 3.9, 3.10, 3.11, 3.12 (16 combinations)

**Steps:**
1. Checkout code
2. Install UV
3. Install Python version
4. Sync dependencies (`uv sync`)
5. Lint with Ruff (conditional)
6. Build package (`uv build`)
7. Test wheel installation

**Release Job:**
- Triggers on tag push (e.g., `v0.1.0a3`)
- Builds distributions
- Creates GitHub Release with artifacts
- Auto-generates release notes

---

## Code Conventions

### Python Style (Ruff Configuration)

```toml
[tool.ruff]
line-length = 88
target-version = "py39"

[tool.ruff.lint]
select = ["E", "F", "W", "C90", "I", "N", "UP", "B", "A", "C4", "T20"]
ignore = ["E501"]  # Line too long (handled by formatter)
```

**Enabled Checks:**
- `E`: PEP 8 errors
- `F`: Pyflakes (undefined names, unused imports)
- `W`: Warnings (deprecated syntax)
- `C90`: McCabe complexity
- `I`: Import sorting (isort)
- `N`: Naming conventions
- `UP`: Python upgrade syntax
- `B`: Bugbear (common bugs)
- `A`: Shadowing built-ins
- `C4`: Comprehension simplification
- `T20`: Print statement detection (avoid in production)

### File Organization Rules

1. **Imports:** Group by standard library → third-party → local
   ```python
   import os
   from pathlib import Path

   from textual.app import App
   from textual.widgets import Button

   from silentmemoir.data.quotes import QUOTES
   ```

2. **Class Structure:**
   ```python
   class ClassName:
       """Docstring explaining purpose."""

       # Class variables
       CSS_PATH = "path/to/css"

       # __init__ first
       def __init__(self):
           pass

       # Public methods
       def public_method(self):
           pass

       # Event handlers (on_* methods)
       def on_mount(self):
           pass

       # Actions (action_* methods)
       def action_something(self):
           pass

       # Private methods last
       def _private_method(self):
           pass
   ```

3. **Naming Conventions:**
   - Classes: `PascalCase` (e.g., `ViewJournals`, `JournalEntry`)
   - Functions/methods: `snake_case` (e.g., `get_journals`, `save_entry`)
   - Constants: `UPPER_SNAKE_CASE` (e.g., `QUOTES`, `DEFAULT_PATH`)
   - Private members: `_leading_underscore`
   - Widget IDs: `#lowercase_with_underscores` (TCSS convention)

4. **Line Length:** 88 characters (Black standard)

### Textual-Specific Conventions

1. **CSS Binding:**
   ```python
   class MyScreen(Screen):
       CSS_PATH = "assets/css.tcss"  # Preferred method
       # OR
       CSS = """
       #my_widget { ... }
       """
   ```

2. **Event Handlers:**
   - Use `on_<event>` methods (e.g., `on_mount`, `on_key`, `on_button_pressed`)
   - Return values rarely needed (event propagation)

3. **Actions:**
   - Define as `action_<name>` methods
   - Bind in `BINDINGS` class variable:
     ```python
     BINDINGS = [
         ("h", "home", "Home"),
         ("n", "new_journal", "New Journal"),
     ]
     ```

4. **Widget Queries:**
   - Use `self.query_one("#widget_id", WidgetType)`
   - Raises `NoMatches` if not found (handle appropriately)

5. **Screen Transitions:**
   - `self.app.push_screen(ScreenName())` for new screen
   - `self.app.pop_screen()` to return
   - Pass callbacks for modal results:
     ```python
     self.app.push_screen(Entry(journal, callback=self.refresh))
     ```

### File Paths

- **Always use `Path` from `pathlib`** (not `os.path`)
- **Home directory:** `Path.home() / ".silentmemoir" / "journals"`
- **Create directories:** `path.mkdir(parents=True, exist_ok=True)`
- **Check existence:** `path.exists()`, `path.is_file()`, `path.is_dir()`

### Error Handling

```python
# For file operations
from pathlib import Path

try:
    content = Path(file_path).read_text()
except FileNotFoundError:
    # Handle missing file
    pass
except PermissionError:
    # Handle permission issues
    pass

# For Textual queries
from textual.css.query import NoMatches

try:
    widget = self.query_one("#my_widget", Button)
except NoMatches:
    # Widget not found
    pass
```

---

## Testing Guidelines

### Current State
**⚠️ No automated tests exist yet.** The project is in alpha and relies on manual testing.

### Configuration (Ready for Implementation)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
```

### Testing Strategy (When Implemented)

1. **Unit Tests** (`tests/unit/`)
   - Test data models: `Journal`, `JournalEntry`
   - Test utility functions
   - Mock filesystem operations

2. **Integration Tests** (`tests/integration/`)
   - Test screen workflows
   - Test file persistence
   - Use Textual's `pilot` for UI testing

3. **Manual Testing Checklist**
   - [ ] Create new journal
   - [ ] Create entry with auto-timestamp
   - [ ] Create entry with custom title
   - [ ] Edit existing entry
   - [ ] Delete journal (empty and with entries)
   - [ ] Delete entry
   - [ ] Toggle edit/preview mode (Tab)
   - [ ] Save entry (Ctrl+S)
   - [ ] Navigate between panels (arrows)
   - [ ] Theme toggle (dark/light)
   - [ ] Return to home screen (h)
   - [ ] Exit application (Esc from home)

### Example Test Structure (Future)

```python
# tests/unit/test_journal.py
from pathlib import Path
from silentmemoir.screens.view_journals import Journal

def test_journal_creation(tmp_path):
    journal = Journal("Test Journal", base_path=tmp_path)
    journal_path = journal.path
    assert journal_path.exists()
    assert journal_path.is_dir()

def test_get_journals(tmp_path):
    Journal("Journal 1", base_path=tmp_path)
    Journal("Journal 2", base_path=tmp_path)
    journals = Journal.get_journals(base_path=tmp_path)
    assert len(journals) == 2
```

---

## Key Files Reference

### 1. `src/silentmemoir/main.py`

**Purpose:** Application entry point and configuration

**Key Components:**
- `SilentMemoir(App)`: Main app class
  - `CSS_PATH`: Points to `assets/css.tcss`
  - `SCREENS`: Registry of available screens
  - `on_mount()`: Pushes opening screen on launch
  - `action_toggle_dark()`: Theme toggle action

- `run()`: Entry point function (called by CLI command)

**When to Modify:**
- Adding new screens to registry
- Changing default theme
- Adding global app-level actions
- Modifying CSS path

**Example Addition:**
```python
# Adding a new screen
SCREENS = {
    "opening": OpeningScreen,
    "view_journals": ViewJournals,
    "settings": SettingsScreen,  # NEW
}
```

### 2. `src/silentmemoir/screens/view_journals.py`

**Purpose:** Main journal/entry management interface

**Key Components:**

1. **`Journal` class (lines 11-64):**
   - Data model for journal operations
   - Methods: `__init__`, `get_journals()`, `get_entries()`, `delete()`
   - Properties: `name`, `path`, `entries`

2. **`ViewJournals` screen (lines 118-272):**
   - Two-panel layout (journals left, entries right)
   - Key bindings: h, n, d, arrows, Enter
   - Methods to know:
     - `refresh_journals()`: Reload journal list
     - `refresh_entries()`: Reload entry list for selected journal
     - `action_new_journal()`: Open new journal modal
     - `on_list_view_selected()`: Handle selection events
     - `on_key()`: Handle delete ('d') key

3. **`NewJournal` modal (lines 274+):**
   - Simple input dialog for journal creation

**When to Modify:**
- Changing journal storage location
- Adding journal metadata (description, color, etc.)
- Implementing search functionality
- Adding entry filtering/sorting
- Changing keyboard shortcuts

**Important Notes:**
- Line 141: `self._entries_list_loading` flag prevents race conditions
- Refresh methods are called after create/delete operations
- Uses callbacks to communicate with entry modal

### 3. `src/silentmemoir/screens/entry.py`

**Purpose:** Markdown editor with live preview

**Key Components:**

1. **`JournalEntry` class (lines 18-68):**
   - Data model for individual entries
   - Methods:
     - `get(file_path, journal)`: Factory method to load existing entry
     - `save()`: Write to filesystem
   - Properties: `journal`, `title`, `content`, `file_path`

2. **`Entry` modal (lines 70-196):**
   - Dual-mode interface (edit/preview)
   - Components:
     - `#title_input`: Entry title input
     - `#edit_area`: TextArea for editing
     - `#preview_area`: Markdown renderer
   - Methods:
     - `action_save()`: Save without exiting (Ctrl+S)
     - `action_toggle_preview()`: Switch edit/preview (Tab)
     - `on_input_submitted()`: Save on title submit
     - `on_unmount()`: Cleanup on exit

**When to Modify:**
- Adding auto-save functionality
- Implementing Markdown toolbar/shortcuts
- Adding entry templates
- Changing default filename format
- Adding metadata (tags, categories)

**Important Notes:**
- Entry filenames sanitize special characters (line 64)
- Preview mode disables title input
- Callback is invoked after successful save

### 4. `src/silentmemoir/screens/opening_screen.py`

**Purpose:** Splash screen with branding

**Key Components:**
- ASCII art title using PyFiglet
- Random quote display (updates every 10s)
- 'e' key to enter app

**When to Modify:**
- Changing app title/branding
- Adding version display
- Modifying quote rotation interval
- Adding onboarding tips

### 5. `src/silentmemoir/assets/css.tcss`

**Purpose:** Textual CSS styling

**Key Selectors:**
- `#main_container`: Two-column grid layout (40/60 split)
- `#journal_panel`, `#entries_panel`: Panel borders and styling
- `#modal_container`: Semi-transparent overlay (70% opacity)
- `.titleText`: Large ASCII art text
- `.accent`: Highlighted text (cyan color)
- `.entry_item`, `.journal-entry`, `.new_entry`: List item styling

**When to Modify:**
- Changing color scheme
- Adjusting panel widths
- Modifying layout breakpoints
- Adding new widget styles

**TCSS Reference:**
- Uses CSS-like syntax with Textual-specific properties
- `dock: top` for positioning
- `layers: base overlay` for z-index
- `text-style: bold italic` for typography

### 6. `src/silentmemoir/data/quotes.py`

**Purpose:** Inspirational quotes database

**Current Content:** 11 quotes from various philosophers/authors

**When to Modify:**
- Adding more quotes
- Categorizing quotes (themes)
- Implementing quote search/favorites

---

## Common Tasks

### Task 1: Add a New Keyboard Shortcut

**Example:** Add `Ctrl+F` for future search functionality

1. **Add binding to screen class:**
   ```python
   # In view_journals.py
   class ViewJournals(Screen):
       BINDINGS = [
           ("h", "home", "Home"),
           ("n", "new_journal", "New Journal"),
           ("ctrl+f", "search", "Search"),  # NEW
       ]
   ```

2. **Implement action handler:**
   ```python
   def action_search(self):
       # TODO: Implement search
       self.app.push_screen(SearchModal())
   ```

3. **Update README.md** with new shortcut

### Task 2: Add a New Screen

**Example:** Create a Settings screen

1. **Create new file:** `src/silentmemoir/screens/settings.py`
   ```python
   from textual.app import ComposeResult
   from textual.screen import Screen
   from textual.widgets import Static

   class SettingsScreen(Screen):
       def compose(self) -> ComposeResult:
           yield Static("Settings", classes="titleText")

       def on_key(self, event):
           if event.key == "escape":
               self.app.pop_screen()
   ```

2. **Register in main.py:**
   ```python
   from silentmemoir.screens.settings import SettingsScreen

   class SilentMemoir(App):
       SCREENS = {
           "opening": OpeningScreen,
           "view_journals": ViewJournals,
           "settings": SettingsScreen,  # NEW
       }
   ```

3. **Add navigation from another screen:**
   ```python
   # In ViewJournals, add binding
   ("s", "settings", "Settings")

   def action_settings(self):
       self.app.push_screen("settings")
   ```

### Task 3: Modify File Storage Location

**Current:** `~/.silentmemoir/journals/`

**Change to:** `~/.config/silentmemoir/journals/`

1. **Update in `view_journals.py`:**
   ```python
   # Line ~14 in Journal.__init__
   if base_path is None:
       base_path = Path.home() / ".config" / "silentmemoir" / "journals"
   ```

2. **Update in `entry.py`:**
   ```python
   # Line ~25 in JournalEntry.__init__
   journal_base = Path.home() / ".config" / "silentmemoir" / "journals"
   ```

3. **Update README.md** to reflect new location

4. **Add migration script** (optional) to move old data

### Task 4: Add Entry Metadata (Tags)

1. **Update `JournalEntry` class:**
   ```python
   class JournalEntry:
       def __init__(self, journal, title=None, content="", tags=None):
           self.journal = journal
           self.title = title or self._generate_timestamp()
           self.content = content
           self.tags = tags or []  # NEW
   ```

2. **Store tags in YAML front matter:**
   ```python
   def save(self):
       front_matter = f"---\ntags: {', '.join(self.tags)}\n---\n\n"
       full_content = front_matter + self.content
       self.file_path.write_text(full_content)
   ```

3. **Parse tags when loading:**
   ```python
   @classmethod
   def get(cls, file_path, journal):
       content = file_path.read_text()
       # Parse YAML front matter
       tags = []  # Extract from front matter
       return cls(journal, file_path.stem, content, tags=tags)
   ```

4. **Update UI** to display/edit tags

### Task 5: Implement Search Functionality

1. **Create search modal:** `src/silentmemoir/screens/search.py`
   ```python
   class SearchModal(Screen):
       def compose(self):
           yield Input(placeholder="Search entries...")
           yield ListView()

       def on_input_changed(self, event):
           query = event.value
           results = self._search_entries(query)
           self._update_results(results)

       def _search_entries(self, query):
           # Scan all journals/entries for matches
           results = []
           journals_path = Path.home() / ".silentmemoir" / "journals"
           for journal_dir in journals_path.iterdir():
               for entry_file in journal_dir.glob("*.md"):
                   content = entry_file.read_text()
                   if query.lower() in content.lower():
                       results.append((journal_dir.name, entry_file))
           return results
   ```

2. **Add search binding** in `ViewJournals` (see Task 1)

3. **Optimize with indexing** (future enhancement)

---

## Troubleshooting

### Issue: App won't start

**Symptoms:** `ModuleNotFoundError` or import errors

**Solutions:**
1. Verify dependencies installed: `uv sync`
2. Check Python version: `python --version` (must be >=3.9)
3. Ensure you're in project root: `pwd` should show `/path/to/SilentMemoir`
4. Try: `uv run python -m silentmemoir.main`

### Issue: Journal/entry not appearing

**Symptoms:** Created journal/entry doesn't show in list

**Solutions:**
1. Check file system: `ls ~/.silentmemoir/journals/`
2. Verify file permissions: `ls -la ~/.silentmemoir/journals/`
3. Check for refresh bugs in `view_journals.py:refresh_journals()`
4. Add debug logging:
   ```python
   journals = Journal.get_journals()
   print(f"Found {len(journals)} journals")  # Temporary debug
   ```

### Issue: Markdown preview not rendering

**Symptoms:** Preview shows raw Markdown instead of formatted text

**Solutions:**
1. Verify Textual version: `uv pip list | grep textual` (should be >=5.3.0)
2. Check if `#preview_area` is a `Markdown` widget (not `TextArea`)
3. Ensure `action_toggle_preview()` updates `display` property correctly

### Issue: Delete not working

**Symptoms:** Pressing 'd' doesn't delete journal/entry

**Solutions:**
1. Check if item is highlighted (selection required)
2. Verify `on_key` handler receives event:
   ```python
   def on_key(self, event):
       print(f"Key pressed: {event.key}")  # Debug
   ```
3. Check file permissions on journal directory
4. Confirm `Journal.delete()` or entry file deletion succeeds

### Issue: Build fails

**Symptoms:** `uv build` errors

**Solutions:**
1. Lint first: `uv run ruff check src/`
2. Fix linting errors
3. Verify `pyproject.toml` syntax
4. Check `src/silentmemoir/__init__.py` exists
5. Ensure all `.py` files have valid syntax

### Issue: CI pipeline fails

**Symptoms:** GitHub Actions shows red X

**Solutions:**
1. Check logs in Actions tab
2. Common failures:
   - Ruff linting errors → Fix locally, push
   - Build errors → Test `uv build` locally
   - Import errors → Verify dependencies in `pyproject.toml`
3. Test across Python versions locally:
   ```bash
   uv run --python 3.9 python -m silentmemoir.main
   uv run --python 3.12 python -m silentmemoir.main
   ```

---

## Additional Resources

### Textual Documentation
- **Official Docs:** https://textual.textualize.io/
- **Widget Gallery:** https://textual.textualize.io/widget_gallery/
- **Guide:** https://textual.textualize.io/guide/
- **CSS Reference:** https://textual.textualize.io/css_types/

### UV Package Manager
- **Documentation:** https://docs.astral.sh/uv/
- **Installation:** https://docs.astral.sh/uv/#installation

### Ruff Linter
- **Rules Reference:** https://docs.astral.sh/ruff/rules/
- **Configuration:** https://docs.astral.sh/ruff/configuration/

### Python Packaging
- **pyproject.toml Guide:** https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- **setuptools Documentation:** https://setuptools.pypa.io/

---

## Contributing Guidelines

### For AI Assistants

1. **Always read this file first** before making changes
2. **Follow code conventions** strictly (Ruff will enforce)
3. **Test manually** before committing (no automated tests yet)
4. **Update this file** if architecture changes significantly
5. **Commit frequently** with clear, descriptive messages
6. **Respect the minimalist philosophy** - avoid feature bloat

### For Human Developers

See README.md for general contribution guidelines. This document is specifically tailored for AI assistants working on the codebase.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0a3 | 2025-11-13 | Current version, added journal right-click features, improved gitignore |
| 0.1.0a2 | 2025-11-12 | Bug fixes and UI improvements |
| 0.1.0a0 | 2025-11-10 | Initial alpha release |

---

**Maintained by:** AI Assistant (Claude)
**Repository:** https://github.com/pndaRN/SilentMemoir
**Issues:** https://github.com/pndaRN/SilentMemoir/issues
