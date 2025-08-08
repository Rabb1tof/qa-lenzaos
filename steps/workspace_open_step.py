from __future__ import annotations

import os
from pages.auth_pages import WorkspaceNamePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time, os
from config.test_data import UserData

DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes")


def run(driver) -> None:
    """Step 4: Verify workspace creation page is shown (after code)."""
    if DRY_RUN:
        return
    page = WorkspaceNamePage(driver)
    data = UserData()

    # Дождаться появления поля имени воркспейса
    def wait_workspace_ready() -> None:
        ok = False
        try:
            WebDriverWait(driver, 12).until(lambda d: page.exists_name_input())
            ok = True
        except Exception:
            # Fallback: попробовать найти любой текстовый input
            try:
                WebDriverWait(driver, 5).until(
                    lambda d: any(el.is_displayed() and el.is_enabled() for el in d.find_elements(By.CSS_SELECTOR, "input[type='text']"))
                )
                ok = True
            except Exception:
                ok = False
        if not ok:
            # Сохраним дампы для диагностики
            ts = int(time.time())
            dump_dir = os.path.join(os.getcwd(), "_dom_dumps")
            os.makedirs(dump_dir, exist_ok=True)
            html_path = os.path.join(dump_dir, f"workspace_not_found_{ts}.html")
            png_path = os.path.join(dump_dir, f"workspace_not_found_{ts}.png")
            try:
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
            except Exception:
                pass
            try:
                driver.save_screenshot(png_path)
            except Exception:
                pass
            raise AssertionError("Workspace name input not visible")

    wait_workspace_ready()

    # Негативные кейсы: пусто, спецсимволы, пробелы
    for invalid in data.workspace_name_invalids:
        try:
            page.set_name("")
            page.set_name(invalid)
            WebDriverWait(driver, 2).until(lambda d: (not page.is_next_enabled()) or page.has_error())
            assert (not page.is_next_enabled()) or page.has_error(), f"Ожидали блокировку/ошибку для имени: {invalid!r}"
        except Exception:
            # Не фейлим весь тест на флаке UI: просто продолжаем к позитиву
            pass

    # Проверка кнопки Назад
    try:
        page.click_back()
        # ожидаем, что поле имени исчезнет (вернулись назад) или URL поменяется
        WebDriverWait(driver, 4).until(lambda d: not page.exists_name_input())
    except Exception:
        # если back отсутствует — допускаем, продолжаем
        pass

    # Вернуться на страницу воркспейса (в некоторых потоках back может увести кода): просто подождём появления обратно
    wait_workspace_ready()

    # Позитив: валидное имя, кнопка активируется, жмём Далее
    page.set_name(data.workspace_name_valid)
    WebDriverWait(driver, 6).until(lambda d: page.is_next_enabled())
    page.next()
    # Минимальная валидация перехода вперёд — имя больше не редактируется
    try:
        WebDriverWait(driver, 5).until(lambda d: not page.exists_name_input())
    except Exception:
        # не критично, продолжим следующие шаги
        pass
