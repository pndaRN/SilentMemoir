# SilentMemoir
> Your thoughts, your space, your silence."

My boot.dev personal project
## Project Overview
**SilentMemoir** is a minimalist, terminal-based journaling app built with Textual, crafted for users who value quiet focus and keyboard-native interfaces. It offers a distraction-free space to write and reflect, presenting your journal entries in a clean, date-organized layout with rich Markdown rendering. Each entry is stored locally in a secure JSON file, with no need for internet access or external services.

**SilentMemoir** supports multiple journals allowing you to organize your writing into separate themes like work, travel, dreams, or daily reflections. On launch, you can choose or create a journal, and all the writing, searching, and browsing happens within that context. The app features a split-screen editor that shows a live Markdown preview as you type, allowing for expressive formatting without leaving the terminal. A fuzzy search interface makes it easy to rediscover thoughts from the past, filtering entries dynamically as you type. Designed for simplicity and speed, **SilentMemoir** is your private, offline writing companion always just a terminal away.

### Project Structure
| File | Description|
| ----------- | ----------- |
|main.py|Entry point|
|journal_view.py|View/search previous enties|
|editor_view.py|Markdown editor with live preview|
|storage.py|Local JSON read/write logic|
|app.tcss|Textual Styles
|README.md|Project Docs|

