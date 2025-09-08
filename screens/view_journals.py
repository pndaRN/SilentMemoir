from textual.app import ComposeResult
from textual.widgets import Label, ListView, ListItem, Input, Footer
from textual.screen import Screen, ModalScreen
from textual.containers import Vertical, Container, Horizontal

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
        return sorted(os.listdir(self.journal_path))


class Entry:
    def __init__(self, journal: Journal, title: str):
        self.journal = journal
        self.title = title
        self.filepath = os.path.join(journal.journal_path, f"{title}.md")

    def save(self, content: str):
        with open(self.filepath, "w") as f:
            f.write(content)

    def read(self) -> str:
        with open(self.filepath) as f:
            return f.read()


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

        self.journals_list = ListView(
            *[ListItem(Label(journal.name)) for journal in journals], id="journals_list"
        )

        self.entries_list = ListView(
            ListItem(Label("Create New Entry"), id="new_entry"),
            id="entries_list",
        )
        with Horizontal(id="main_container"):
            with Vertical(id="journal_panel"):
                yield Label("Journals")
                yield self.journals_list
                yield Label("", id="journal_error")

            with Vertical(id="entries_panel"):
                yield Label("Entries")
                yield self.entries_list
                yield Label("", id="entries_error")

            yield Footer()

    def on_key(self, event: Key):
        if event.key == "right":
            self.set_focus(self.entries_list)
            event.prevent_default()
        if event.key == "left":
            self.set_focus(self.journals_list)
            event.prevent_default()

    # ----------------------------
    # JOURNAL HANDLING
    # ----------------------------

    def action_goto_home(self):
        self.app.push_screen("Opening Screen")

    def action_goto_new_journal(self):
        def on_new_journal_created(journal_name):
            if journal_name:
                self.refresh_journals()

        self.app.push_screen(NewJournal(), on_new_journal_created)

    def refresh_journals(self):
        journals = Journal.list_all()

        self.journals_list.clear()

        for journal in journals:
            self.journals_list.append(ListItem(Label(journal.name)))

    # ----------------------------
    # ENTRY HANDLING
    # ----------------------------

    def rebuild_entries_list(self, journal: Journal):
        """Rebuild the entries list completely"""
        # Remove all children and rebuild
        self.entries_list.clear()

        # Add the "Create New Entry" item
        new_entry_item = ListItem(Label("Create New Entry"))
        new_entry_item.add_class("new-entry")  # Use classes for identification
        self.entries_list.append(new_entry_item)

        # Add actual entries
        for entry in journal.list_entries():
            entry_item = ListItem(Label(entry))
            entry_item.add_class("journal-entry")
            self.entries_list.append(entry_item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "journals_list":
            selected_item = event.item
            label = selected_item.query_one(Label)
            journal_name = str(label.renderable)
            journal = Journal(journal_name)

            self.rebuild_entries_list(journal)

        elif event.list_view.id == "entries_list":
            if event.item.id == "new_entry":
                pass
            else:
                pass


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
            self.query_one("#error_message", Label).update("Journal already exists")
            return
        journal = Journal(journal_name)
        self.dismiss(journal.name)

    def get_existing_journals(self):
        return [
            d
            for d in os.listdir(self.journals_path)
            if os.path.isdir(os.path.join(self.journals_path, d))
        ]
