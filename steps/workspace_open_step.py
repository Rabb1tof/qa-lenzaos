from __future__ import annotations

import os
from pages.auth_pages import WorkspaceNamePage
from selenium.webdriver.support.ui import WebDriverWait

DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes")


def run(driver) -> None:
    """Step 4: Verify workspace creation page is shown (after code)."""
    if DRY_RUN:
        return
    page = WorkspaceNamePage(driver)
    # Дождаться появления поля имени воркспейса
    ok = False
    try:
        WebDriverWait(driver, 12).until(lambda d: page.exists_name_input())
        ok = True
    except Exception:
        ok = False
    assert ok, "Workspace name input not visible"
