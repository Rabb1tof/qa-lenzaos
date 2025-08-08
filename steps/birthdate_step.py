from __future__ import annotations

import os
from selenium.webdriver.support.ui import Select

from pages.auth_pages import BirthdatePage
from config.test_data import UserData

DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes")


def run(driver) -> None:
    """Step 7: Select birth date and continue."""
    if DRY_RUN:
        return
    page = BirthdatePage(driver)
    data = UserData()

    # If the page uses <select>, wrap with Select; our BasePage.type is a placeholder
    if not DRY_RUN:
        Select(page.wait_visible(*BirthdatePage.DAY)).select_by_visible_text(data.birth_day)
        Select(page.wait_visible(*BirthdatePage.MONTH)).select_by_visible_text(data.birth_month)
        Select(page.wait_visible(*BirthdatePage.YEAR)).select_by_visible_text(data.birth_year)
        page.continue_next()
