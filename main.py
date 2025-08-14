from textual.app import App, ComposeResult
from textual.widgets import Input, Label


class SilentMemoir(App):

    CSS_PATH = "CSS.tcss"

    def compose(self) -> ComposeResult:
        yield Label("[b]SilentMemoir[/]", classes = "box") 
        # yield Input(placeholder="Content")


if __name__ == "__main__":
    app = SilentMemoir()
    app.run()

