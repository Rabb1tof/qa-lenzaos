from __future__ import annotations

import os
import random
from selenium.common.exceptions import TimeoutException

from pages.auth_pages import AuthLandingPage
from core.browser import get_base_url
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes")


def run(driver) -> None:
    """Step 1: Open dropdown, list languages, click two random ones, then normalize to RU."""
    page = AuthLandingPage(driver).open()

    if DRY_RUN:
        print("[lang] DRY_RUN enabled: только открыли страницу без действий")
        return

    try:
        page = AuthLandingPage(driver).open()
        page.dismiss_cookies()

        initial_label = page.get_language_label()

        def open_and_get():
            # Open dropdown and wait for menu visibility
            page.open_language_dropdown()
            try:
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".context-menu.context-menu--modal .context-menu__list"))
                )
            except Exception:
                pass
            # dump DOM for diagnostics
            try:
                dump_dir = os.path.join(os.getcwd(), "_dom_dumps")
                os.makedirs(dump_dir, exist_ok=True)
                with open(os.path.join(dump_dir, "step_after_lang_open.html"), "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
            except Exception:
                pass
            data = page.get_language_items()
            items = data.get("items", [])
            texts = data.get("texts", [])
            print(f"[lang] languages available (n={len(texts)}): {texts}")
            assert items, "Не удалось получить список языков из dropdown"
            return items, texts

        # Click two random languages (excluding current label if possible)
        for i in range(1, 3):
            items, texts = open_and_get()
            current = page.get_language_label()
            candidates = [t for t in texts if t and t != current]
            pick = random.choice(candidates or texts)
            print(f"[lang] random pick #{i}: '{pick}' -> clicking")
            page.click_language_by_text(pick)
            WebDriverWait(driver, 6).until(
                lambda d: page.get_language_label() != current or (pick in (page.get_language_label() or ""))
            )
            print(f"[lang] now label: '{page.get_language_label()}'")

        # Normalize to RU via URL navigation
        base = get_base_url().rstrip('/')
        print(f"[lang] navigating to RU via URL: {base}/ru")
        driver.get(f"{base}/ru")
        WebDriverWait(driver, 10).until(EC.url_contains('/ru'))
        print("[lang] RU via URL loaded")

    except TimeoutException as e:
        # dump for diagnostics
        import time
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
        import time
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
