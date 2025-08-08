from __future__ import annotations

import os

from pages.auth_pages import DashboardPage
from config.test_data import UserData

DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes")


def run(driver) -> None:
    """Step 10: Verify user is in workspace/dashboard and profile data shown."""
    page = DashboardPage(driver)
    data = UserData()

    if not DRY_RUN:
        name = page.get_profile_name()
        email = page.get_profile_email()
        assert data.first_name in name and data.last_name in name, "Profile name mismatch"
        assert email == data.email_valid, "Profile email mismatch"
