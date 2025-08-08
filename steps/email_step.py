from __future__ import annotations

import os
from selenium.common.exceptions import TimeoutException

from pages.auth_pages import EmailPage, AuthLandingPage, CodePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from config.test_data import UserData

DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes")


def run(driver) -> None:
    """Step 2: Email input validation and navigation."""
    if DRY_RUN:
        # Skip real interactions in dry mode
        return

    # Ensure we're on email page; open landing and click "Начать"
    landing = AuthLandingPage(driver).open()
    landing.click_start()
    email = EmailPage(driver)

    # Wait until email input is visible (with one retry on slow UI)
    try:
        WebDriverWait(driver, 12).until(EC.visibility_of_element_located(email.EMAIL_INPUT))
    except TimeoutException:
        # Retry clicking Start once more and wait again
        landing.click_start()
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(email.EMAIL_INPUT))

    data = UserData()

    try:
        # Negative cases
        for invalid in data.email_invalids:
            # Scroll input into view before interaction
            el = driver.find_element(*email.EMAIL_INPUT)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
            email.enter_email("")
            email.enter_email(invalid)
            # trigger blur/validation
            driver.find_element(*email.EMAIL_INPUT).send_keys(Keys.TAB)
            # For invalid emails, the Continue button remains disabled or an error appears
            WebDriverWait(driver, 2).until(lambda d: (not email.is_next_enabled()) or email.has_error())
            assert (not email.is_next_enabled()) or email.has_error(), f"Expected validation to block email: {invalid!r}"

        # Positive
        el = driver.find_element(*email.EMAIL_INPUT)
        driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
        email.enter_email("")
        email.enter_email(data.email_valid)
        # trigger blur/enable
        driver.find_element(*email.EMAIL_INPUT).send_keys(Keys.TAB)
        # Wait until Continue becomes enabled, then click
        WebDriverWait(driver, 5).until(lambda d: email.is_next_enabled())
        email.click_next()
        # Ожидаем появления следующего шага (страница ввода кода).
        cp = CodePage(driver)
        WebDriverWait(driver, 15).until(lambda d: len(cp._find_code_inputs()) > 0)
    except TimeoutException as e:
        raise AssertionError(f"Email step timeout: {e}")
