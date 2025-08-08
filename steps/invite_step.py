from __future__ import annotations

import os

from pages.auth_pages import InvitePage
from config.test_data import UserData

DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes")


def run(driver) -> None:
    """Step 8: Invitation block checks: remove invalids, copy link, invite later, send."""
    page = InvitePage(driver)
    data = UserData()

    if not DRY_RUN:
        page.paste_emails(list(data.invite_emails))
        page.click_copy_link()
        page.click_invite_later()
        # Alternatively: page.click_send()
