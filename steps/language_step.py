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
        page.dismiss_cookies()

        # Try to ensure dropdown is visible quickly
        try:
            WebDriverWait(driver, 3).until(EC.visibility_of_element_located(AuthLandingPage.LANG_DROPDOWN))
        except Exception:
            pass

        def lang_label():
            return page.get_language_label()
        initial_label = lang_label()
        initial_title = page.get_title_text()
        print(f"[lang] initial label='{initial_label}', title='{initial_title}'")

        # Helpers
        def matches_en(val: str) -> bool:
            v = (val or "").lower()
            return ('eng' in v) or (v.strip() in ('en', 'eng', 'english'))
        def matches_ru(val: str) -> bool:
            v = (val or "").lower()
            return ('рус' in v) or (v.strip() in ('ru', 'rus', 'russian'))

        # UI-only checks with assertions
        try:
            page.select_language("English")
            init_title = page.get_title_text()
            WebDriverWait(driver, 5).until(
                lambda d: matches_en(lang_label()) or '/en' in d.current_url or page.get_title_text() != init_title
            )
            print(f"[lang] switched to English via dropdown -> '{lang_label()}'")
        except Exception as e:
            # one more attempt
            try:
                page.select_language("English")
                init_title = page.get_title_text()
                WebDriverWait(driver, 5).until(
                    lambda d: matches_en(lang_label()) or '/en' in d.current_url or page.get_title_text() != init_title
                )
            except Exception:
                raise AssertionError(f"Language dropdown failed to switch to English: {e}")

        before_label = lang_label()
        try:
            page.select_language("Русский")
            init_title2 = page.get_title_text()
            WebDriverWait(driver, 5).until(
                lambda d: matches_ru(lang_label()) or '/ru' in d.current_url or page.get_title_text() != init_title2
            )
            print(f"[lang] switched back to Russian via dropdown -> '{lang_label()}'")
        except Exception as e:
            try:
                page.select_language("Русский")
                init_title2 = page.get_title_text()
                WebDriverWait(driver, 5).until(
                    lambda d: matches_ru(lang_label()) or '/ru' in d.current_url or page.get_title_text() != init_title2
                )
            except Exception:
                raise AssertionError(f"Language dropdown failed to switch back to Russian: {e}")

        # Restore RU via URL just to normalize state (non-blocking)
        try:
            from core.browser import get_base_url
            base = get_base_url().rstrip('/')
            driver.get(f"{base}/ru")
        except Exception:
            pass
    except TimeoutException as e:
        # dump for diagnostics
        import os, time
        ts = int(time.time())
        dump_dir = os.path.join(os.getcwd(), "_dom_dumps")
        os.makedirs(dump_dir, exist_ok=True)
        try:
            with open(os.path.join(dump_dir, f"lang_timeout_{ts}.html"), "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        except Exception:
            pass
        try:
            driver.save_screenshot(os.path.join(dump_dir, f"lang_timeout_{ts}.png"))
        except Exception:
            pass
        raise AssertionError(f"Language step timeout: {e}")
    except AssertionError as e:
        import os, time
        ts = int(time.time())
        dump_dir = os.path.join(os.getcwd(), "_dom_dumps")
        os.makedirs(dump_dir, exist_ok=True)
        try:
            with open(os.path.join(dump_dir, f"lang_fail_{ts}.html"), "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        except Exception:
            pass
        try:
            driver.save_screenshot(os.path.join(dump_dir, f"lang_fail_{ts}.png"))
        except Exception:
            pass
        raise
