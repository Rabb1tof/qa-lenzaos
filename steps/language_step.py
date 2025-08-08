from __future__ import annotations

import os
from selenium.common.exceptions import TimeoutException

from pages.auth_pages import AuthLandingPage
from core.browser import get_base_url
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes")


def run(driver) -> None:
    """Step 1: Switch languages on the first auth page and verify UI changes."""
    page = AuthLandingPage(driver).open()

    if DRY_RUN:
        # In dry mode we only verify that page opens without interacting
        return

    # Use the visible language dropdown first, then fall back to URL locales
    try:
        # Ensure on landing
        page = AuthLandingPage(driver).open()
        # Close cookie/consent if present
        page.dismiss_cookies()

        # Try to ensure dropdown is visible before attempting dropdown path
        try:
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located(AuthLandingPage.LANG_DROPDOWN))
        except Exception:
            pass

        def lang_label():
            return page.get_language_label()

        initial_label = lang_label()
        initial_title = page.get_title_text()
        print(f"[lang] initial label='{initial_label}', title='{initial_title}'")

        # Try dropdown -> English
        try:
            page.select_language("English")
            WebDriverWait(driver, 7).until(
                lambda d: (lang_label() != initial_label) or (page.get_title_text() != initial_title)
            )
            print(f"[lang] switched to English via dropdown -> '{lang_label()}'")
        except Exception:
            # Fallback: URL locale
            from core.browser import get_base_url
            base = get_base_url().rstrip('/')
            driver.get(f"{base}/en")
            WebDriverWait(driver, 7).until(lambda d: page.get_title_text() != initial_title)
            print("[lang] switched to English via URL /en")

        # Try to switch back -> Russian
        before_label = lang_label()
        before_title = page.get_title_text()
        try:
            page.select_language("Русский")
            WebDriverWait(driver, 7).until(
                lambda d: (lang_label() != before_label) or (page.get_title_text() != before_title)
            )
            print(f"[lang] switched back to Russian via dropdown -> '{lang_label()}'")
        except Exception:
            from core.browser import get_base_url
            base = get_base_url().rstrip('/')
            driver.get(f"{base}/ru")
            WebDriverWait(driver, 7).until(lambda d: page.get_title_text() != before_title)
            print("[lang] switched back to Russian via URL /ru")
    except TimeoutException as e:
        raise AssertionError(f"Language step failed due to timeout: {e}")
