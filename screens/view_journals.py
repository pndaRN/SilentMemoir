from textual.app import ComposeResult
from textual.widgets import Label, ListView, ListItem, Input, Footer
from textual.screen import Screen, ModalScreen
from textual.containers import Vertical, Container, Horizontal, ScrollableContainer

from textual.binding import Binding
from textual.events import Key

import os

# ----------------------------
# DATA LAYER
# ----------------------------


class Journal:
    base_path = os.path.expanduser("~/.silentmemoir/journals/")

    def __init__(self, name: str):
        self.name = name
        self.journal_path = os.path.join(self.base_path, self.name)
        os.makedirs(self.journal_path, exist_ok=True)

    @classmethod
    def list_all(cls) -> list["Journal"]:
        os.makedirs(cls.base_path, exist_ok=True)
        return [
            cls(d)
            for d in os.listdir(cls.base_path)
            if os.path.isdir(os.path.join(cls.base_path, d))
        ]

    def list_entries(self) -> list[str]:
        return sorted(os.listidr(self.journal_path))

    def add_entry(self, title: str, content: str) -> str:
        filename = f"{title}.md"
        filepath = os.path.join(self.journal_path, filename)
        with open(filename, "w") as f:
            f.write(content)
        return filepath


class Entry:
    def __init__(self, journal: Journal, title: str):
        self.journal = journal
        self.title = title
        self.filepath = os.path.join(journal.path, f"{title}.md")

    def save(self, content: str):
        with open(self.filepath, "w") as f:
            f.write(content)

    def read(self) -> str:
        with open(self.filepath) as f:
            return f.read


# ----------------------------
# VISUAL LAYER
# ----------------------------


class ViewJournals(Screen):
    BINDINGS = [
        Binding(key="h", action="goto_home", description="Home"),
        Binding(key="a", action="select_cursor", description="Accept"),
        Binding(key="n", action="goto_new_journal", description="New Journal"),
        Binding(key="r", action="refresh_journals", description="Refresh"),
    ]

    def compose(self) -> ComposeResult:
        journals = Journal.list_all()

        self.list_view = ListView(
            *[ListItem(Label(journal.name)) for journal in journals]
        )

        with Horizontal(id="main_container"):
            with Vertical(id="journal_panel"):
                yield Label("Select a Journal")
                yield self.list_view
                yield Label("", id="journal_error")

            with Vertical(id="entries_panel"):
                yield Label("Journal Entries", id="entries_title")
                yield ScrollableContainer(id="entries_container")
                yield Label("", id="entries_error")

            yield Footer()

    def action_goto_home(self):
        self.app.push_screen("Opening Screen")

    def action_goto_new_journal(self):
        def on_new_journal_created(journal_name):
            if journal_name:
                self.refresh_journals()

        self.app.push_screen(NewJournal(), on_new_journal_created)

    def refresh_journals(self):
        journals = Journal.list_all()

        self.list_view.clear()

        for journal in journals:
            self.list_view.append(ListItem(Label(journal.name)))


class NewJournal(ModalScreen[str]):
    def __init__(self):
        super().__init__()
        self.journals_path = os.path.expanduser("~/.silentmemoir/journals")

    def compose(self) -> ComposeResult:
        yield Container(
            Vertical(
                Label("Create New Journal"),
                Input(placeholder="Enter Journal Name"),
                Label("Press 'Enter' to accept"),
                Label("Press 'Esc' to go back"),
                Label("", id="error_message"),
                id="modal_content",
            ),
            id="modal_container",
        )

    def on_key(self, event: Key):
        if event.key == "escape":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.create_journal(event)

    def create_journal(self, input):
        journal_name = input.value.strip()
        if not journal_name:
            self.query_one("#error_message", Label).update("Please enter a name")
            return
        elif journal_name in self.get_existing_journals():
            self.query_one("#error_message", Label).update("Journal alread exists")
        journal = Journal(journal_name)
        self.dismiss(journal.name)

    def get_existing_journals(self):
        return [
            d
            for d in os.listdir(self.journals_path)
            if os.path.isdir(os.path.join(self.journals_path, d))
        ]
