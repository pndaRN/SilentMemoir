from textual.app import App

from silentmemoir.screens.opening_screen import OpeningScreen
from silentmemoir.screens.view_journals import ViewJournals


class SilentMemoir(App):
    CSS_PATH = "assets/css.tcss"

    SCREENS = {
        "Opening Screen": OpeningScreen,
        "View Journals": ViewJournals,
    }

    def on_mount(self):
        self.push_screen("Opening Screen")

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


def run():
    app = SilentMemoir()
    app.run()


if __name__ == "__main__":
    app = SilentMemoir()
    app.run()
