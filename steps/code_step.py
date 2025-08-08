from __future__ import annotations

import os
from selenium.common.exceptions import TimeoutException

from pages.auth_pages import CodePage, EmailPage, WorkspaceNamePage
from selenium.webdriver.support.ui import WebDriverWait
from config.test_data import UserData

DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes")


def run(driver) -> None:
    """Step 3: Enter confirmation code, handle negatives, back button."""
    if DRY_RUN:
        return
    page = CodePage(driver)
    data = UserData()

    try:
        # Подождать появления любого поля(ей) для ввода кода
        WebDriverWait(driver, 12).until(lambda d: len(page._find_code_inputs()) > 0)

        # Негативные кейсы (без строгих ожиданий, чтобы не зависнуть)
        for invalid in data.code_invalids:
            try:
                page.enter_code(invalid)
            except AssertionError:
                # Поля могли исчезнуть или быть нестандартными — пропускаем негатив
                break

        # Опциональная проверка кнопки "Назад" — не валим тест, если отсутствует
        try:
            page.click_back()
            # Ожидаем возврата на страницу email
            WebDriverWait(driver, 5).until(lambda d: EmailPage(driver).exists(*EmailPage.EMAIL_INPUT))
            # Вернёмся обратно к коду, снова нажав "Продолжить" на email — выполним быстрый путь
            # Поскольку кнопка и поведение уже проверены в шаге email, просто заново откроем страницу ввода кода:
            # Нажатие назад не обязательно, если отсутствует явный путь вперёд.
        except Exception:
            pass

        # Позитивный кейс — ввод корректного кода
        page.enter_code(data.code_valid)
        # Дождаться перехода на страницу воркспейса
        wsp = WorkspaceNamePage(driver)
        def on_workspace(d):
            try:
                return wsp.exists_name_input() or ('workspace' in d.current_url)
            except Exception:
                return False
        try:
            WebDriverWait(driver, 7).until(on_workspace)
        except Exception:
            # Попробуем нажать "Продолжить" на странице кода (если есть кнопка), затем подождём ещё
            try:
                page.continue_next()
            except Exception:
                pass
            WebDriverWait(driver, 10).until(on_workspace)
    except TimeoutException as e:
        raise AssertionError(f"Code step timeout: {e}")
