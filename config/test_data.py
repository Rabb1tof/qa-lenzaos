from dataclasses import dataclass


@dataclass(frozen=True)
class UserData:
    email_valid: str = "user@test.com"
    email_invalids: tuple[str, ...] = (
        "",
        "usertest.com",
        "@",
        "verylongemailaddress_exceeding_limits_but_for_test@example.com",
        "user!@test.com",
    )
    code_valid: str = "666555"
    code_invalids: tuple[str, ...] = ("", "123", "abc123")
    workspace_name_valid: str = "qa-lenzaos-ws"
    workspace_name_invalids: tuple[str, ...] = ("", "***", "   ")
    first_name: str = "Ivan"
    last_name: str = "Petrov"
    birth_day: str = "10"
    birth_month: str = "March"
    birth_year: str = "1995"
    invite_emails: tuple[str, ...] = ("mate1@test.com", "bad@@mail", "friend2@test.com")
