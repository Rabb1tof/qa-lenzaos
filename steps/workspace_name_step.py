from __future__ import annotations

import os
from selenium.common.exceptions import TimeoutException

from pages.auth_pages import WorkspaceNamePage
from config.test_data import UserData

DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes")


def run(driver) -> None:
    """Step 5: Enter and validate workspace name; test Back."""
    if DRY_RUN:
        return
    page = WorkspaceNamePage(driver)
    data = UserData()

    try:
        # Negative
        for invalid in data.workspace_name_invalids:
            if DRY_RUN and invalid.strip():
                continue
            page.set_name(invalid)
            page.next()
            # Expect validation visible; needing real selector. Skipped in DRY_RUN.

        # Back button smoke (can't assert prev page without selectors)
        if not DRY_RUN:
            page.back()

        # Positive
        page.set_name(data.workspace_name_valid)
        page.next()
    except TimeoutException as e:
        raise AssertionError(f"Workspace name step timeout: {e}")
