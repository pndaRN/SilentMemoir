import os

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer, Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Markdown, TextArea

from silentmemoir.screens.view_journals import Journal

# -------------------------------
# DATA
# -------------------------------


class JournalEntry:
    def __init__(self, journal: Journal, title=None):
        self.journal = journal
        self.title = title
        self.filepath = os.path.join(self.journal.journal_path, f"{title}.md")

    def save(self, content: str):
        with open(self.filepath, "w") as f:
            f.write(content)

    def read(self) -> str:
        if os.path.exists(self.filepath):
            with open(self.filepath) as f:
                return f.read()
        return ""

    def exists(self) -> bool:
        return os.path.exists(self.filepath)


# ------------------------------------
# ENTRY SCREEN
# ------------------------------------


class Entry(ModalScreen):
    BINDINGS = [
        Binding("ctrl+s", "save_entry", "Save", show=True),
        Binding("escape", "dismiss_screen", "Exit", show=True),
        Binding("tab", "toggle_preview", "Toggle Mode", show=True, priority=True),
    ]

    def __init__(
        self,
        journal: Journal = None,
        entry_name: str = None,
        is_new_entry: bool = False,
    ):
        super().__init__()
        self.journal = journal
        self.entry_name = entry_name
        self.is_new_entry = is_new_entry
        self.editing_mode = True

        self.text_area = None
        self.markdown_viewer = None
        self.status_label = None
        self.scroll_container = None
        self.title_input = None

        if journal and entry_name:
            self.journal_entry = JournalEntry(journal, entry_name.replace(".md", ""))
        else:
            self.journal_entry = None

    def compose(self) -> ComposeResult:
        if self.is_new_entry:
            journal_name = getattr(self.journal, "name", "Unknown")
            yield Label(f"Create New Entry in: {self.journal.name}")
            self.title_input = Input(
                placeholder="Enter custom title (optional)", id="title_input"
            )
            yield self.title_input
        else:
            journal_name = getattr(self.journal, "name", "Unknown")
            entry_name = self.entry_name or "Unknown"
            yield Label(f"Editing: {entry_name} in {journal_name}")

        self.status_label = Label(
            "Mode: Editing | Tab: Toggle Preview | Ctrl+S: Save | Esc: Exit"
        )
        yield self.status_label

        content = ""
        if not self.is_new_entry and self.journal_entry and self.journal_entry.exists():
            content = self.journal_entry.read()

        with Vertical(id="contentcontainer"):
            self.text_area = TextArea(content, id="entry_content")
            yield self.text_area

            self.scroll_container = ScrollableContainer(id="markdown_scroll")
            with self.scroll_container:
                self.markdown_viewer = Markdown(
                    content or "# New Entry\n\\start writing your markdown here...",
                    id="markdown_preview",
                )
                yield self.markdown_viewer
            self.scroll_container.display = False

    # ------------------------------------
    # ACTIONS
    # ------------------------------------

    def action_save_entry(self):
        self.save_entry(exit_after=False)

    def action_dismiss_screen(self):
        self.save_entry(exit_after=True)

    def action_toggle_preview(self):
        self.toggle_mode()

    def action_toggle_mode(self):
        self.toggle_mode()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "title_input" and self.text_area:
            self.text_area.focus()

    # ------------------------------------
    # TOGGLE
    # ------------------------------------

    def toggle_mode(self):
        if self.editing_mode:
            self.save_entry(exit_after=False)

            current_content = self.text_area.text
            if current_content.strip():
                self.markdown_viewer.update(current_content)
            else:
                self.markdown_viewer.update("# Empty Entry\n\nNo content to preview")

            self.text_area.display = False
            self.scroll_container.display = True

            self.editing_mode = False
            self.status_label.update(
                "Mode: Preview | Tab: Back to Editing | Ctrl+S: Save | Esc: Exit"
            )

        else:
            self.text_area.display = True
            self.scroll_container.display = False

            self.text_area.focus()

            self.editing_mode = True
            self.status_label.update(
                "Mode: Editing | Tab: Toggle Preview | Ctrl+S: Save | Esc: Exit"
            )

    # ------------------------------------
    # SAVE
    # ------------------------------------

    def save_entry(self, exit_after: bool = False):
        if not self.journal:
            return

        content = self.text_area.text

        if self.is_new_entry:
            import datetime

            if not self.entry_name:
                custom_title = ""
                if self.title_input:
                    custom_title = self.title_input.value.strip()

                if custom_title:
                    self.entry_name = custom_title
                else:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    self.entry_name = f"entry_{timestamp}"

            self.journal_entry = JournalEntry(self.journal, self.entry_name)

        if self.journal_entry:
            self.journal_entry.save(content)
            if exit_after:
                self.dismiss(f"Saved: {self.entry_name}")

    def on_mount(self):
        if self.is_new_entry and self.title_input:
            self.title_input.focus()
        else:
            if hasattr(self, "text_area"):
                self.text_area.focus()
