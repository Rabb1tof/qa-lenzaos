from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from .base_page import BasePage
from core.browser import get_base_url
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AuthLandingPage(BasePage):
    """Start page: language switch, go to email input."""

    # Real selectors from live DOM
    # Language switcher button in header
    LANG_DROPDOWN = (By.CSS_SELECTOR, "button.lang-switch")
    TITLE = (By.CSS_SELECTOR, "p.pr_slider_title")
    # Multiple locale variants for the Start button
    START_BTN_XPATHS = [
        "//button[span[contains(normalize-space(.), 'Начать')]]",
        "//button[span[contains(normalize-space(.), 'Start')]]",
        "//button[contains(normalize-space(.), 'Начать')]",
        "//button[contains(normalize-space(.), 'Start')]",
    ]

    def open(self):
        self.driver.get(get_base_url())
        # Wait for main title to ensure page is loaded
        try:
            WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located(self.TITLE))
        except Exception:
            pass
        # Try close cookie banner if exists
        try:
            self.dismiss_cookies()
        except Exception:
            pass
        return self

    def open_language_dropdown(self):
        self.click(*self.LANG_DROPDOWN)
        # Wait for any menu container or items to appear
        try:
            WebDriverWait(self.driver, 6).until(
                EC.visibility_of_element_located((
                    By.CSS_SELECTOR,
                    ".context-menu.context-menu--modal .context-menu__list"
                ))
            )
        except Exception:
            pass

    def _switch_to_default(self):
        try:
            self.driver.switch_to.default_content()
        except Exception:
            pass

    def _find_menu_in_current_context(self):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, ".context-menu.context-menu--modal .context-menu__list")
        except Exception:
            return None

    def _switch_to_menu_context(self):
        """Try to ensure driver context points to the iframe (if any) containing the language menu.
        Returns the menu WebElement if found, otherwise None. Restores default content if not found.
        """
        # First, try in default content
        self._switch_to_default()
        menu = self._find_menu_in_current_context()
        if menu is not None:
            return menu
        # Try top-level iframes
        frames = self.driver.find_elements(By.TAG_NAME, "iframe")
        for fr in frames:
            try:
                self.driver.switch_to.frame(fr)
                menu = self._find_menu_in_current_context()
                if menu is not None:
                    return menu
                # Try one nested level
                nested = self.driver.find_elements(By.TAG_NAME, "iframe")
                for fr2 in nested:
                    try:
                        self.driver.switch_to.frame(fr2)
                        menu = self._find_menu_in_current_context()
                        if menu is not None:
                            return menu
                    finally:
                        self.driver.switch_to.parent_frame()
            except Exception:
                pass
            finally:
                self.driver.switch_to.default_content()
        # Not found
        self._switch_to_default()
        return None

    def get_language_items(self):
        # Use Selenium DOM to extract items; handle iframes if needed
        menu = self._switch_to_menu_context()
        if menu is None:
            return {"items": [], "texts": []}
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".context-menu__option .list-item__title"))
            )
        except Exception:
            pass
        titles = menu.find_elements(By.CSS_SELECTOR, ".context-menu__option .list-item__title")
        texts: list[str] = []
        items = []
        for i, t in enumerate(titles):
            try:
                txt = (t.text or "").strip()
                if not txt:
                    continue
                texts.append(txt)
                items.append({"text": txt, "index": i})
            except Exception:
                continue
        return {"items": items, "texts": texts}

    def click_language_by_text(self, label: str):
        """Click a language option by visible text within the dropdown menu.
        Prefers searching within .context-menu__list; falls back to a global search.
        Assumes the dropdown has already been opened.
        """
        # Click the option by text strictly inside the modal menu in #context-root
        container = self._switch_to_menu_context()
        if container is None:
            # Fallback: try a global search as last resort
            try:
                target = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        f"//*[self::li or self::button or self::a or self::div][normalize-space(.)='{label}' or .//span[normalize-space(text())='{label}']]"
                    ))
                )
                target.click()
                return True
            except Exception:
                return False

        # Ensure the list is present and the label exists before clicking
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#context-root .context-menu__list"))
            )
        except Exception:
            pass

        try:
            # Wait for the specific label span, then click its ancestor option element
            item_span = WebDriverWait(container, 6).until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    f".//span[contains(@class,'list-item__title')][normalize-space(text())='{label}']"
                ))
            )
            option = item_span.find_element(By.XPATH, "ancestor::*[contains(@class,'context-menu__option')][1]")
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option)
            except Exception:
                pass
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(option))
            option.click()
            self._switch_to_default()
            return True
        except Exception:
            # Fallback global search
            self._switch_to_default()
            try:
                target = WebDriverWait(self.driver, 6).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        f"//*[self::li or self::button or self::a or self::div][normalize-space(.)='{label}' or .//span[normalize-space(text())='{label}']]"
                    ))
                )
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
                except Exception:
                    pass
                target.click()
                return True
            except Exception:
                return False

    def get_title_text(self) -> str:
        return self.get_text(*self.TITLE)

    def click_start(self):
        # Try multiple variants in different locales with safe click
        for xp in self.START_BTN_XPATHS:
            els = self.driver.find_elements(By.XPATH, xp)
            if els:
                try:
                    els[0].click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", els[0])
                return
        raise AssertionError("Start button not found on landing page")

    def get_language_label(self) -> str:
        try:
            return self.wait_visible(*self.LANG_DROPDOWN).text.strip()
        except Exception:
            return ""

    def select_language(self, label: str):
        """Open dropdown and click the language by its visible label.
        Works for e.g. "English" or "Русский".
        """
        # Ensure dropdown button is visible and clickable
        btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.LANG_DROPDOWN))
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

        # Wait for a menu container to appear (try common patterns)
        menu_candidates = [
            (By.CSS_SELECTOR, "[role='menu']"),
            (By.CSS_SELECTOR, ".dropdown-menu, .menu, .dropdown, .menu-items"),
            (By.XPATH, "//ul[contains(@class,'dropdown') or contains(@class,'menu')]"),
        ]
        menu = None
        for by, sel in menu_candidates:
            try:
                menu = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((by, sel)))
                if menu:
                    break
            except Exception:
                continue

        # Build option XPath; prefer searching within discovered menu
        opt_xpath = (
            f".//*[self::button or self::a or self::div][normalize-space(.)='{label}' or .//span[normalize-space(text())='{label}']]"
        )
        if menu is not None:
            opt = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, opt_xpath))
            )
        else:
            # Fallback: global search
            opt = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, opt_xpath.lstrip('.')))
            )
        try:
            opt.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", opt)

    def dismiss_cookies(self):
        """Try to close cookie/consent banners if present."""
        candidates = [
            (By.XPATH, "//button[contains(., 'Принять') or contains(., 'Согласен') or contains(., 'Хорошо')]") ,
            (By.XPATH, "//button[contains(., 'Accept') or contains(., 'I agree') or contains(., 'Got it')]") ,
            (By.CSS_SELECTOR, "button.cookie-accept, button[data-testid='cookie-accept']"),
        ]
        for by, sel in candidates:
            try:
                el = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((by, sel)))
                try:
                    el.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", el)
                break
            except Exception:
                continue


class EmailPage(BasePage):
    # Real selectors (from DOM dump after clicking "Начать")
    EMAIL_INPUT = (By.CSS_SELECTOR, "input#email-input")
    # Button has inner span text "Продолжить" and type="button"
    NEXT_BTN = (By.XPATH, "//button[span[contains(normalize-space(.), 'Продолжить')]]")
    # TODO: Add specific selector for validation error text when identified
    ERROR_TEXT = (By.CSS_SELECTOR, "p.hdi_description")

    def enter_email(self, email: str):
        self.type(*self.EMAIL_INPUT, text=email)

    def click_next(self):
        self.click(*self.NEXT_BTN)

    def has_error(self) -> bool:
        return self.exists(*self.ERROR_TEXT)

    def is_next_enabled(self) -> bool:
        try:
            return self.wait_visible(*self.NEXT_BTN).is_enabled()
        except Exception:
            return False


class CodePage(BasePage):
    # Flexible selectors to detect OTP/code inputs
    CODE_INPUT_CANDIDATES = [
        (By.CSS_SELECTOR, "input[autocomplete='one-time-code']"),
        (By.CSS_SELECTOR, "input[name='code']"),
        (By.CSS_SELECTOR, "input[inputmode='numeric']"),
        (By.CSS_SELECTOR, "input[type='tel']"),
        (By.CSS_SELECTOR, "input[maxlength='6']"),
        (By.CSS_SELECTOR, "input[data-otp], input[class*='otp'], input[name*='otp']"),
    ]
    BACK_BUTTON_CANDIDATES = [
        (By.CSS_SELECTOR, "[data-testid='back-button']"),
        (By.XPATH, "//button[span[contains(normalize-space(.), 'Назад')] or contains(normalize-space(.), 'Назад')]") ,
        (By.XPATH, "//a[span[contains(normalize-space(.), 'Назад')] or contains(normalize-space(.), 'Назад')]") ,
    ]
    CONTINUE_BUTTON_CANDIDATES = [
        (By.XPATH, "//button[span[contains(normalize-space(.), 'Продолжить')] or contains(normalize-space(.), 'Продолжить')]") ,
        (By.XPATH, "//button[span[contains(normalize-space(.), 'Continue')] or contains(normalize-space(.), 'Continue')]") ,
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.CSS_SELECTOR, "button.btn.btn--full-width"),
    ]

    def _find_code_inputs(self):
        # Try candidates and return list of WebElements
        for by, sel in self.CODE_INPUT_CANDIDATES:
            els = self.driver.find_elements(by, sel)
            if els:
                return els
        return []

    def enter_code(self, code: str):
        inputs = self._find_code_inputs()
        assert inputs, "Не удалось найти поле(я) ввода кода"
        if len(inputs) == 1:
            self.wait_visible(*self.CODE_INPUT_CANDIDATES[0]) if inputs[0] is None else None
            inputs[0].clear()
            inputs[0].send_keys(code)
        else:
            # Fill per character across multiple inputs
            for i, ch in enumerate(code):
                if i >= len(inputs):
                    break
                inputs[i].clear()
                inputs[i].send_keys(ch)

    def click_back(self):
        # Try all back button candidates
        for by, sel in self.BACK_BUTTON_CANDIDATES:
            els = self.driver.find_elements(by, sel)
            if els:
                els[0].click()
                return
        raise AssertionError("Кнопка 'Назад' не найдена на странице кода")

    def continue_next(self):
        # Try to click a Continue/Next button
        for by, sel in self.CONTINUE_BUTTON_CANDIDATES:
            els = self.driver.find_elements(by, sel)
            if els:
                try:
                    els[0].click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", els[0])
                return
        # If nothing found, silently return; some flows may auto-advance


class WorkspaceNamePage(BasePage):
    # Flexible candidates for workspace name input
    NAME_INPUT_CANDIDATES = [
        (By.CSS_SELECTOR, "input[name='workspaceName']"),
        (By.CSS_SELECTOR, "input#workspace-name"),
        (By.CSS_SELECTOR, "input[type='text']"),
        (By.XPATH, "//input[contains(translate(@id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'workspace')]") ,
        (By.XPATH, "//input[contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'ворк') or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'пространств') or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'workspace') or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'company') or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'компан')]") ,
    ]
    NEXT_BTN = (By.CSS_SELECTOR, "button[type='submit']")
    BACK_BTN = (By.CSS_SELECTOR, "[data-testid='back-button']")

    def _find_name_input(self):
        for by, sel in self.NAME_INPUT_CANDIDATES:
            els = self.driver.find_elements(by, sel)
            for el in els:
                try:
                    if el.is_displayed() and el.is_enabled():
                        return el
                except Exception:
                    continue
        return None

    def exists_name_input(self) -> bool:
        return self._find_name_input() is not None

    def set_name(self, name: str):
        el = self._find_name_input()
        assert el is not None, "Поле имени воркспейса не найдено"
        el.clear()
        el.send_keys(name)

    def next(self):
        self.click(*self.NEXT_BTN)

    def click_back(self):
        try:
            self.click(*self.BACK_BTN)
        except Exception:
            # Fallback by text
            try:
                self.click(By.XPATH, "//button[contains(normalize-space(.), 'Назад')]")
            except Exception:
                pass

    def is_next_enabled(self) -> bool:
        try:
            el = self.driver.find_element(*self.NEXT_BTN)
            return el.is_enabled() and 'disabled' not in (el.get_attribute('class') or '')
        except Exception:
            return False

    def has_error(self) -> bool:
        try:
            # Common patterns: input aria-invalid, error text near input
            inp = self._find_name_input()
            if inp is not None and (inp.get_attribute('aria-invalid') == 'true'):
                return True
            err = self.driver.find_elements(By.CSS_SELECTOR, ".error, .error-text, .field-error")
            return any(e.is_displayed() for e in err)
        except Exception:
            return False

    def back(self):
        self.click(*self.BACK_BTN)


class ProfilePage(BasePage):
    # TODO: Replace with real selectors
    AVATAR_INPUT = (By.CSS_SELECTOR, "input[type='file']")
    FIRST_NAME = (By.CSS_SELECTOR, "input[name='firstName']")
    LAST_NAME = (By.CSS_SELECTOR, "input[name='lastName']")
    CONTINUE = (By.CSS_SELECTOR, "button[type='submit']")

    def upload_avatar(self, path: str):
        self.wait_visible(*self.AVATAR_INPUT).send_keys(path)

    def fill_names(self, first: str, last: str):
        self.type(*self.FIRST_NAME, text=first)
        self.type(*self.LAST_NAME, text=last)

    def can_continue(self) -> bool:
        return self.wait_visible(*self.CONTINUE).is_enabled()

    def continue_next(self):
        self.click(*self.CONTINUE)


class BirthdatePage(BasePage):
    # TODO: Replace with real selectors
    DAY = (By.CSS_SELECTOR, "select[name='day']")
    MONTH = (By.CSS_SELECTOR, "select[name='month']")
    YEAR = (By.CSS_SELECTOR, "select[name='year']")
    CONTINUE = (By.CSS_SELECTOR, "button[type='submit']")

    def set_birthdate(self, day: str, month: str, year: str):
        # Placeholder approach, may need Select helper
        self.type(*self.DAY, text=day)
        self.type(*self.MONTH, text=month)
        self.type(*self.YEAR, text=year)

    def continue_next(self):
        self.click(*self.CONTINUE)


class InvitePage(BasePage):
    # TODO: Replace with real selectors
    INPUT = (By.CSS_SELECTOR, "textarea[name='emails']")
    COPY_LINK = (By.CSS_SELECTOR, "[data-testid='copy-link']")
    INVITE_LATER = (By.CSS_SELECTOR, "[data-testid='invite-later']")
    SEND = (By.CSS_SELECTOR, "[data-testid='send-invites']")

    def paste_emails(self, emails: list[str]):
        self.type(*self.INPUT, text="\n".join(emails))

    def click_copy_link(self):
        self.click(*self.COPY_LINK)

    def click_invite_later(self):
        self.click(*self.INVITE_LATER)

    def click_send(self):
        self.click(*self.SEND)


class ApprovedDomainsPage(BasePage):
    # TODO: Replace with real selectors
    SKIP = (By.CSS_SELECTOR, "[data-testid='skip']")

    def skip(self):
        self.click(*self.SKIP)


class DashboardPage(BasePage):
    # TODO: Replace with real selectors
    PROFILE_NAME = (By.CSS_SELECTOR, "[data-testid='profile-name']")
    PROFILE_EMAIL = (By.CSS_SELECTOR, "[data-testid='profile-email']")

    def get_profile_name(self) -> str:
        return self.get_text(*self.PROFILE_NAME)

    def get_profile_email(self) -> str:
        return self.get_text(*self.PROFILE_EMAIL)
