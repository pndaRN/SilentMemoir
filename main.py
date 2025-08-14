from textual.app import App, ComposeResult
from textual.widgets import Input


class SilentMemoir(App):

    CSS_PATH = "CSS.tcss"

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Title")
        yield Input(placeholder="Content")


if __name__ == "__main__":
    app = SilentMemoir()
    app.run()

