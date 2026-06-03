import reflex as rx


class LegalState(rx.State):
    """Manages the visibility of legal content on the public landing page."""

    # Current view: "login", "terms", or "privacy"
    current_view: str = "login"

    @rx.event
    def set_view(self, view: str):
        """Switch the public view."""
        self.current_view = view

    @rx.event
    def show_terms(self):
        self.current_view = "terms"

    @rx.event
    def show_privacy(self):
        self.current_view = "privacy"

    @rx.event
    def show_login(self):
        self.current_view = "login"

    @rx.event
    def check_legal_params(self):
        """Check query parameters for deployment-safe direct links."""
        view = self.router.page.params.get("view", "login")
        if view in ["terms", "privacy", "login"]:
            self.current_view = view