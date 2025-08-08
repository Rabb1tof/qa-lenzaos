from __future__ import annotations

import os
from pages.auth_pages import ApprovedDomainsPage

DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes")


def run(driver) -> None:
    """Step 9: Approved domains - click Skip."""
    if DRY_RUN:
        return
    page = ApprovedDomainsPage(driver)
    page.skip()
