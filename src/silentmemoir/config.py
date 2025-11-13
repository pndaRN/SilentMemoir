"""
Configuration constants for SilentMemoir application.

This module centralizes all configuration values, magic strings, and constants
used throughout the application.
"""

import os

# ----------------------------
# File System Paths
# ----------------------------

JOURNALS_BASE_PATH = os.path.expanduser("~/.silentmemoir/journals/")
"""Base directory where all journals are stored."""

# ----------------------------
# File Formats
# ----------------------------

MARKDOWN_EXTENSION = ".md"
"""File extension for journal entries."""

TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
"""Format string for generating timestamp-based entry names."""

# ----------------------------
# UI Configuration
# ----------------------------

ERROR_MESSAGE_DISPLAY_DURATION = 3
"""Duration in seconds to display error messages before clearing them."""

# ----------------------------
# Default Entry Content
# ----------------------------

DEFAULT_ENTRY_PREFIX = "entry_"
"""Prefix for auto-generated entry names."""

EMPTY_PREVIEW_MESSAGE = "# Empty Entry\n\nNo content to preview"
"""Message to display when previewing an empty entry."""

NEW_ENTRY_PLACEHOLDER = "# New Entry\n\nstart writing your markdown here..."
"""Placeholder text for new entries."""
