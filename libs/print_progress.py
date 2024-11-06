# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Print Progress Reporter."""

import streamlit as st

class PrintProgressReporter():
    """A progress reporter that does nothing."""

    prefix: str

    def __init__(self, prefix: str):
        """Create a new progress reporter."""
        self.prefix = prefix
  

    def __call__(self, update: any) -> None:
        """Update progress."""
  

    def dispose(self) -> None:
        """Dispose of the progress reporter."""

    def child(self, prefix: str, transient: bool = True) -> "any":
        """Create a child progress bar."""


    def stop(self) -> None:
        """Stop the progress reporter."""

    def force_refresh(self) -> None:
        """Force a refresh."""

    def error(self, message: str) -> None:
        """Report an error."""
        st.error(f"\n{self.prefix}ERROR: {message}")  # noqa T201

    def warning(self, message: str) -> None:
        """Report a warning."""
        st.warning(f"\n{self.prefix}WARNING: {message}")  # noqa T201

    def info(self, message: str) -> None:
        """Report information."""
        st.info(f"\n{self.prefix}INFO: {message}")  # noqa T201

    def success(self, message: str) -> None:
        """Report success."""
        st.success(f"\n{self.prefix}SUCCESS: {message}")  # noqa T201
