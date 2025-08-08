from __future__ import annotations

import os
import sys
from typing import Callable

from core.browser import get_driver

# Steps
from steps.language_step import run as step1
from steps.email_step import run as step2
from steps.code_step import run as step3
from steps.workspace_open_step import run as step4
from steps.workspace_name_step import run as step5
from steps.profile_step import run as step6
from steps.birthdate_step import run as step7
from steps.invite_step import run as step8
from steps.approved_domains_step import run as step9
from steps.final_checks_step import run as step10


STEPS: list[tuple[str, Callable]] = [
    ("1. Смена языка", step1),
    ("2. Ввод email", step2),
    ("3. Ввод кода", step3),
    ("4. Открытие страницы воркспейса", step4),
    ("5. Имя воркспейса", step5),
    ("6. Профиль", step6),
    ("7. Дата рождения", step7),
    ("8. Приглашения", step8),
    ("9. Approved domains", step9),
    ("10. Финальные проверки", step10),
]


def main() -> int:
    print("🚀 Запуск factory теста регистрации")
    driver = get_driver()

    try:
        for name, fn in STEPS:
            print(f"\n▶️  {name}")
            fn(driver)
            print(f"✅ {name} пройден")
        print("\n🎉 Все шаги пройдены успешно")
        return 0
    except AssertionError as e:
        print(f"❌ Тест упал: {e}")
        return 2
    except Exception as e:
        print(f"💥 Неожиданная ошибка: {e}")
        return 3
    finally:
        driver.quit()


if __name__ == "__main__":
    sys.exit(main())
