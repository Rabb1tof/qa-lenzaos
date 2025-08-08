from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


DEFAULT_TIMEOUT = 10


@dataclass
class BasePage:
    driver: WebDriver

    def wait_visible(self, by: By, value: str, timeout: int = DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )

    def wait_clickable(self, by: By, value: str, timeout: int = DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )

    def click(self, by: By, value: str, timeout: int = DEFAULT_TIMEOUT):
        el = self.wait_clickable(by, value, timeout)
        el.click()
        return el

    def type(self, by: By, value: str, text: str, clear: bool = True, timeout: int = DEFAULT_TIMEOUT):
        el = self.wait_visible(by, value, timeout)
        if clear:
            el.clear()
        el.send_keys(text)
        return el

    def get_text(self, by: By, value: str, timeout: int = DEFAULT_TIMEOUT) -> str:
        el = self.wait_visible(by, value, timeout)
        return el.text.strip()

    def exists(self, by: By, value: str, timeout: int = 3) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except Exception:
            return False

    def url_contains(self, fragment: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.url_contains(fragment))
            return True
        except Exception:
            return False
