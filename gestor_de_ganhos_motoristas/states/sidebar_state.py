import reflex as rx


class SidebarState(rx.State):
    """State for managing the sidebar visibility on mobile."""

    is_open: bool = False

    @rx.event
    def toggle_sidebar(self):
        self.is_open = not self.is_open

    @rx.event
    def close_sidebar(self):
        self.is_open = False