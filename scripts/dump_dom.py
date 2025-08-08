from __future__ import annotations

import os
from pathlib import Path
import sys

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.browser import get_driver, get_base_url
from pages.auth_pages import AuthLandingPage


OUT_DIR = Path("_dom_dumps")
OUT_DIR.mkdir(exist_ok=True)


def main():
    driver = get_driver(headless=os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes"))
    try:
        # Open landing
        lp = AuthLandingPage(driver).open()
        # Click Start ("Начать") to move to email screen
        try:
            lp.click_start()
        except Exception as e:
            print(f"[warn] couldn't click Start: {e}")
        # Dump email page
        html = driver.page_source
        f1 = OUT_DIR / "step_after_start.html"
        f1.write_text(html)
        print(f"[ok] wrote DOM to {f1}")

        # Try to fill email and continue
        try:
            email_input = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input#email-input"))
            )
            email_input.clear()
            email_input.send_keys("user@test.com")
            continue_btn = driver.find_element(By.XPATH, "//button[span[contains(normalize-space(.), 'Продолжить')]]")
            continue_btn.click()
        except Exception as e:
            print(f"[warn] couldn't proceed to code page: {e}")

        # Dump next page
        html2 = driver.page_source
        f2 = OUT_DIR / "step_after_email.html"
        f2.write_text(html2)
        print(f"[ok] wrote DOM to {f2}")
    except TimeoutException as e:
        print(f"[err] timeout: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
