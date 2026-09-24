from datetime import datetime, timezone

from app.contracts import (
    DISPLAY_TIMEZONE_NAME,
    as_display,
    as_utc,
    iso_display,
    iso_utc,
    utcnow,
)


def test_contracts_normalize_naive_values_as_utc() -> None:
    value = as_utc("2026-09-24T12:00:00")

    assert value == datetime(2026, 9, 24, 12, tzinfo=timezone.utc)
    assert iso_utc(value) == "2026-09-24T12:00:00+00:00"


def test_contracts_present_values_in_official_timezone() -> None:
    value = as_display("2026-09-24T12:00:00+00:00")

    assert DISPLAY_TIMEZONE_NAME == "America/Campo_Grande"
    assert value is not None
    assert value.hour == 8
    assert iso_display(value) == "2026-09-24T08:00:00-04:00"


def test_utcnow_is_naive_for_database_columns() -> None:
    value = utcnow()

    assert value.tzinfo is None
