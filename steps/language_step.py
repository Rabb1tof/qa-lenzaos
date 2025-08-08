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
    """Step 1: Смена языка: открыть dropdown, получить языки, выбрать случайный 2 раза, затем /ru."""
    page = AuthLandingPage(driver).open()

    if DRY_RUN:
        print("[lang] DRY_RUN enabled: только открыли страницу без действий")
        return

    try:
        # Ensure landing and close banners
        page = AuthLandingPage(driver).open()
        page.dismiss_cookies()

        def lang_label():
            return page.get_language_label()

        initial_label = lang_label()
        print(f"[lang] initial label: '{initial_label}'")

        def open_and_get():
            print("[lang] opening dropdown")
            page.open_language_dropdown()
            # Quick diagnostics about menu containers
            diag = driver.execute_script(
                """
                (function(){
                  function cnt(sel){try{return document.querySelectorAll(sel).length}catch(e){return -1}}
                  const info = {
                    ctxRoot: !!document.querySelector('#context-root'),
                    ctxRootNotEmpty: !!document.querySelector('#context-root:not(.empty)'),
                    dialogRoot: !!document.querySelector('#dialog-root'),
                    menuList: cnt('.context-menu__list'),
                    roleMenu: cnt('[role="menu"]'),
                    roleItem: cnt('[role="menuitem"]'),
                    anyMenus: cnt('.menu, .dropdown, .menu-items'),
                    langButtons: cnt("button, a, li"),
                  };
                  return info;
                })();
                """
            )
            print(f"[lang][diag] containers: {diag}")
            # Try to wait a bit for any of expected containers
            try:
                WebDriverWait(driver, 5).until(
                    EC.any_of(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, ".context-menu__list")),
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "#context-root *")),
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "#dialog-root *")),
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "[role='menu']")),
                    )
                )
            except Exception:
                pass
            # Dump page source for post-mortem
            try:
                import os
                dump_dir = os.path.join(os.getcwd(), "_dom_dumps")
                os.makedirs(dump_dir, exist_ok=True)
                with open(os.path.join(dump_dir, "step_after_lang_open.html"), "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print("[lang][diag] saved DOM dump to _dom_dumps/step_after_lang_open.html")
            except Exception as e:
                print(f"[lang][diag] failed dumping DOM: {e}")

            # Wait for menu to appear
            try:
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".context-menu__list"))
                )
            except Exception:
                # Allow fallback: any generic menu
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "[role='menu'], .menu, .dropdown, .menu-items"))
                )
            data = page.get_language_items()
            items = (data or {}).get("items", [])
            texts = (data or {}).get("texts", [])
            print(f"[lang] languages available (n={len(texts)}): {texts}")
            assert items, "Не удалось получить список языков из dropdown"
            return items, texts

        # Do two random switches
        for i in range(1, 3):
            items, texts = open_and_get()
            current = lang_label()
            # Prefer a language different from current
            candidates = [t for t in texts if t and t != current]
            pick = random.choice(candidates or texts)
            print(f"[lang] random pick #{i}: '{pick}' -> clicking")
            try:
                page.click_language_by_text(pick)
            except Exception:
                # fallback using select_language if needed
                page.select_language(pick)
            # Wait label change (or confirmation it matches pick)
            try:
                WebDriverWait(driver, 6).until(
                    lambda d: lang_label() != current or (pick in (lang_label() or ""))
                )
            except Exception:
                # Not fatal: still log what we have
                pass
            print(f"[lang] now label: '{lang_label()}'")

        # Finally normalize to RU via URL
        try:
            base = get_base_url().rstrip('/')
            target = f"{base}/ru"
            print(f"[lang] navigating to RU via URL: {target}")
            driver.get(target)
            # wait URL contains '/ru'
            WebDriverWait(driver, 10).until(EC.url_contains('/ru'))
            print("[lang] RU via URL loaded")
        except Exception as e:
            raise AssertionError(f"Не удалось перейти на RU через URL: {e}")
    except TimeoutException as e:
        raise AssertionError(f"Language step timeout: {e}")
