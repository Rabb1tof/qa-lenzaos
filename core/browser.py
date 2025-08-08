import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def get_driver(headless: bool | None = None) -> webdriver.Chrome:
     """
     Create and return a configured Chrome WebDriver instance.

     Respects env vars:
       HEADLESS=true/false
     """
     if headless is None:
         headless_env = os.getenv("HEADLESS", "true").lower()
         headless = headless_env in ("1", "true", "yes")

     options = Options()
     if headless:
         options.add_argument("--headless=new")
     options.add_argument("--window-size=1440,900")
     options.add_argument("--no-sandbox")
     options.add_argument("--disable-dev-shm-usage")
     options.add_argument("--disable-gpu")

     service = Service(ChromeDriverManager().install())
     driver = webdriver.Chrome(service=service, options=options)
     driver.implicitly_wait(2)
     return driver

def get_base_url() -> str:
     """Return base URL for auth app, overridable via BASE_URL env."""
     return os.getenv("BASE_URL", "https://auth.lenzaos.com")
