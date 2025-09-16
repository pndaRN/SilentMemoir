from textual.app import ComposeResult
from textual.widgets import Label, TextArea
from textual.screen import ModalScreen
from textual.events import Key
from textual.containers import Vertical
from screens.view_journals import Journal

import os

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
        with open(self.filepath) as f:
            return f.read()

    def exists(self) -> bool:
        return os.path.exists(self.filepath)


class Entry(ModalScreen):
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

        if journal and entry_name:
            self.journal_entry = JournalEntry(journal, entry_name.replace(".md", ""))
        else:
            self.journal_entry = None

    def compose(self) -> ComposeResult:
        if self.is_new_entry:
            yield Label(f"Create New Entry in: {self.journal.name}")
            yield Label("Enter your entry content below:")
            self.text_area = TextArea("", id="entry_content")
            yield self.text_area
            yield Label("Press 'Ctrl+S' to save, 'Esc' to go back without saving")
        else:
            yield Label(f"Editing: {self.entry_name} in {self.journal.name}")

            content = ""
            if self.journal_entry and self.journal_entry.exists():
                content = self.journal_entry.read()

            self.text_area = TextArea(content, id="entry_content")
            yield self.text_area
            yield Label("Press 'Ctrl+S' to save, 'Esc' to go back")

    def on_key(self, event: Key):
        if event.key == "escape":
            self.dismiss(None)
        elif event.key == "ctrl+s":
            self.save_entry()

    def save_entry(self):
        if not self.journal:
            return

        content = self.text_area.text

        if self.is_new_entry:
            import datetime

            if not self.entry_name:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                self.entry_name = f"entry_{timestamp}"

            self.journal_entry = JournalEntry(self.journal, self.entry_name)

        if self.journal_entry:
            self.journal_entry.save(content)
            self.dismiss(f"Saved: {self.entry_name}")

    def on_mount(self):
        if hasattr(self, "text_area"):
            self.text_area.focus()
