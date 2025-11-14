"""
Fuzzy finder for searching journal entries.

This screen provides a fast, fzf-style interface for finding entries across
all journals using fuzzy matching.
"""

import os

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Input, Label, ListView

from silentmemoir.config import JOURNALS_BASE_PATH, MARKDOWN_EXTENSION
from silentmemoir.models import Journal


class FinderResultItem(ListView.Item):
    """Custom ListItem for displaying a search result."""

    def __init__(self, journal_name: str, entry_name: str, snippet: str = ""):
        """
        Initialize a finder result item.

        Args:
            journal_name: The name of the journal containing this entry
            entry_name: The name of the entry file
            snippet: Optional preview snippet from the entry
        """
        display_text = f"{journal_name} > {entry_name}"
        super().__init__(Label(display_text))
        self.journal_name = journal_name
        self.entry_name = entry_name
        self.snippet = snippet
        self.add_class("finder_result")


class Finder(ModalScreen):
    """Modal screen for fuzzy finding entries across all journals."""

    BINDINGS = [
        Binding("escape", "dismiss_finder", "Close", show=True),
        Binding("enter", "open_entry", "Open", show=True),
    ]

    def __init__(self):
        """Initialize the finder screen."""
        super().__init__()
        self.search_input = None
        self.results_list = None
        self.status_label = None
        self.all_entries = []

    def compose(self) -> ComposeResult:
        """
        Compose the UI for this screen.

        Returns:
            The composed UI elements
        """
        yield Container(
            Vertical(
                Label("Fuzzy Finder - Search Entries", classes="finder_title"),
                Input(
                    placeholder="Type to search entries...",
                    id="finder_input",
                ),
                Label("", id="finder_status"),
                ListView(id="finder_results"),
                Label(
                    "↑↓: Navigate | Enter: Open | Esc: Close",
                    classes="finder_help",
                ),
                id="finder_content",
            ),
            id="finder_container",
        )

    def on_mount(self):
        """Set up the finder when mounted."""
        self.search_input = self.query_one("#finder_input", Input)
        self.results_list = self.query_one("#finder_results", ListView)
        self.status_label = self.query_one("#finder_status", Label)

        # Load all entries from all journals
        self._load_all_entries()

        # Focus the search input
        self.search_input.focus()

        # Show initial results (all entries)
        self._update_results("")

    def _load_all_entries(self):
        """Load all entries from all journals into memory."""
        self.all_entries = []

        if not os.path.exists(JOURNALS_BASE_PATH):
            return

        journals = Journal.list_all()

        for journal in journals:
            entries = journal.list_entries()
            for entry in entries:
                if entry.endswith(MARKDOWN_EXTENSION):
                    # Load first few lines for snippet
                    entry_path = os.path.join(journal.journal_path, entry)
                    snippet = self._get_entry_snippet(entry_path)
                    self.all_entries.append(
                        (journal.name, entry, entry_path, snippet)
                    )

    def _get_entry_snippet(self, entry_path: str, max_chars: int = 100) -> str:
        """
        Get a preview snippet from an entry file.

        Args:
            entry_path: Path to the entry file
            max_chars: Maximum characters to include in snippet

        Returns:
            Preview snippet from the entry
        """
        try:
            with open(entry_path, encoding="utf-8") as f:
                content = f.read(max_chars * 2)  # Read a bit more for context
                # Remove markdown headers and get first meaningful line
                lines = [
                    line.strip()
                    for line in content.split("\n")
                    if line.strip() and not line.strip().startswith("#")
                ]
                if lines:
                    snippet = lines[0][:max_chars]
                    return snippet + "..." if len(lines[0]) > max_chars else snippet
                return ""
        except OSError:
            return ""

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Handle search input changes.

        Args:
            event: The input changed event
        """
        if event.input.id == "finder_input":
            query = event.value
            self._update_results(query)

    def _update_results(self, query: str):
        """
        Update the results list based on the search query.

        Args:
            query: The search query string
        """
        self.results_list.clear()

        if not query:
            # Show all entries when query is empty
            matches = self.all_entries
        else:
            # Fuzzy match entries
            matches = self._fuzzy_match(query, self.all_entries)

        # Update results list
        for journal_name, entry_name, _entry_path, snippet in matches[:50]:  # Limit to 50 results
            self.results_list.append(
                FinderResultItem(journal_name, entry_name, snippet)
            )

        # Update status
        total = len(self.all_entries)
        shown = min(len(matches), 50)
        self.status_label.update(f"Showing {shown} of {len(matches)} matches ({total} total entries)")

        # Auto-select first result if available
        if len(self.results_list.children) > 0:
            self.results_list.index = 0

    def _fuzzy_match(
        self, query: str, entries: list[tuple[str, str, str, str]]
    ) -> list[tuple[str, str, str, str]]:
        """
        Perform fuzzy matching on entries.

        Args:
            query: The search query
            entries: List of (journal_name, entry_name, entry_path, snippet) tuples

        Returns:
            Filtered and scored list of matching entries
        """
        query_lower = query.lower()
        matches = []

        for journal_name, entry_name, entry_path, snippet in entries:
            # Calculate match score
            score = self._calculate_match_score(
                query_lower, journal_name, entry_name, snippet
            )

            if score > 0:
                matches.append((score, journal_name, entry_name, entry_path, snippet))

        # Sort by score (descending) and return without score
        matches.sort(reverse=True, key=lambda x: x[0])
        return [(j, e, p, s) for _, j, e, p, s in matches]

    def _calculate_match_score(
        self, query: str, journal_name: str, entry_name: str, snippet: str
    ) -> int:
        """
        Calculate a match score for fuzzy matching.

        Args:
            query: The lowercase search query
            journal_name: Name of the journal
            entry_name: Name of the entry
            snippet: Preview snippet from entry content

        Returns:
            Match score (higher is better, 0 means no match)
        """
        score = 0
        journal_lower = journal_name.lower()
        entry_lower = entry_name.lower()
        snippet_lower = snippet.lower()

        # Exact match in entry name (highest priority)
        if query in entry_lower:
            score += 1000
            # Bonus for match at start
            if entry_lower.startswith(query):
                score += 500

        # Match in journal name
        if query in journal_lower:
            score += 500

        # Match in snippet
        if query in snippet_lower:
            score += 200

        # Fuzzy character sequence match
        if self._fuzzy_char_match(query, entry_lower):
            score += 100
        elif self._fuzzy_char_match(query, journal_lower):
            score += 50

        return score

    def _fuzzy_char_match(self, query: str, text: str) -> bool:
        """
        Check if query characters appear in order in text (fzf-style).

        Args:
            query: The search query
            text: The text to search in

        Returns:
            True if all query characters appear in order in text
        """
        query_idx = 0
        for char in text:
            if query_idx < len(query) and char == query[query_idx]:
                query_idx += 1
        return query_idx == len(query)

    def action_open_entry(self):
        """Open the currently selected entry."""
        if not self.results_list.highlighted_child:
            return

        selected = self.results_list.highlighted_child
        if isinstance(selected, FinderResultItem):
            # Pass the selected entry info back to caller
            result = {
                "journal_name": selected.journal_name,
                "entry_name": selected.entry_name,
            }
            self.dismiss(result)

    def action_dismiss_finder(self):
        """Close the finder without opening an entry."""
        self.dismiss(None)

    def on_key(self, event: Key):
        """
        Handle keyboard events.

        Args:
            event: The keyboard event
        """
        # Allow arrow keys to navigate results
        if event.key in ("up", "down"):
            self.results_list.focus()
