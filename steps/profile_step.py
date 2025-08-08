from __future__ import annotations

import os
from pathlib import Path

from pages.auth_pages import ProfilePage
from config.test_data import UserData

DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes")

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
VALID_AVATAR = str(ASSETS_DIR / "avatar.png")
INVALID_FILE = str(ASSETS_DIR / "virus.exe")


def run(driver) -> None:
    """Step 6: Upload avatar, fill first/last name, verify Continue state."""
    if DRY_RUN:
        return
    page = ProfilePage(driver)
    data = UserData()

    # Ensure assets exist or skip upload in DRY_RUN
    if not Path(VALID_AVATAR).exists():
        # Skip upload in dry mode
        pass
    else:
        if not DRY_RUN:
            page.upload_avatar(VALID_AVATAR)

    page.fill_names(data.first_name, data.last_name)

    if not DRY_RUN:
        assert page.can_continue(), "Continue must be enabled after filling names"
        page.continue_next()
