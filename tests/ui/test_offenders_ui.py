import math
import uuid
from datetime import datetime

import pytest
from playwright.sync_api import Page, expect

from automation.api.client import ApiClient
from automation.ui.offender_watch_page import OffenderWatchPage


def _parse_api_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _find_offender_with_trail(api_client: ApiClient, min_points: int = 2) -> dict:
    response = api_client.get("offenders", params={"pageSize": 100})
    assert response.status_code == 200

    for offender in response.json()["items"]:
        trail_response = api_client.get(f"offenders/{offender['id']}/trail")
        assert trail_response.status_code == 200
        trail = trail_response.json()
        if len(trail) >= min_points:
            return offender

    pytest.fail(f"No offender with at least {min_points} trail points was found")


def _get_latest_trail_point(api_client: ApiClient, offender_id: int) -> dict:
    response = api_client.get(f"offenders/{offender_id}/trail")
    assert response.status_code == 200
    trail = response.json()
    assert trail, f"Expected trail points for offender {offender_id}"
    return max(trail, key=lambda point: _parse_api_timestamp(point["timestamp"]))


@pytest.fixture
def offender_watch(page: Page) -> OffenderWatchPage:
    app = OffenderWatchPage(page)
    app.open()
    return app


def test_fr_01_pagination_provides_access_to_all_offenders(offender_watch: OffenderWatchPage) -> None:
    """FR-01: Pagination must expose all offenders across the expected number of pages."""
    total_offenders = offender_watch.get_total_offender_count()
    page_size = offender_watch.get_visible_page_size()
    assert page_size == OffenderWatchPage.PAGE_SIZE

    _, accessible_pages, total_results = offender_watch.parse_pagination()
    assert total_results == total_offenders

    expected_pages = math.ceil(total_offenders / OffenderWatchPage.PAGE_SIZE)
    assert accessible_pages == expected_pages

    collected_names = offender_watch.collect_all_accessible_offender_names()
    assert len(collected_names) == len(set(collected_names))
    assert len(collected_names) == total_offenders


def test_fr_02_partial_search_by_national_id(offender_watch: OffenderWatchPage) -> None:
    """FR-02: Search supports partial National ID matching."""
    national_id = "205432198"
    national_id_substring = national_id[:6]

    offender_watch.search(national_id_substring)

    row = offender_watch.offender_rows().filter(has_text=national_id)
    expect(row).to_have_count(1)
    expect(row.locator(".name-cell")).to_contain_text("Amar, Noa")


def test_fr_02_search_is_case_insensitive(offender_watch: OffenderWatchPage) -> None:
    """FR-02: Search is case-insensitive for alphabetic name data."""
    search_substring = "cohen"

    offender_watch.search(search_substring)

    row = offender_watch.offender_rows().filter(has_text="Cohen")
    expect(row).to_have_count(1)
    expect(row.locator(".name-cell")).to_contain_text("Cohen, David")


def test_fr_03_create_offender_with_valid_data(offender_watch: OffenderWatchPage) -> None:
    """FR-03: A valid offender can be created through the UI."""
    national_id = str(uuid.uuid4().int)[:9]
    first_name = "UIAuto"
    last_name = "Created"

    try:
        offender_watch.click_add_offender()
        offender_watch.fill_offender_form(
            first_name=first_name,
            last_name=last_name,
            national_id=national_id,
            date_of_birth="1990-03-25",
            risk_level="Low",
            status="Active",
        )
        offender_watch.save_offender_form()

        offender_watch.search(national_id)
        row = offender_watch.offender_rows().filter(has_text=national_id)
        expect(row).to_have_count(1)
        expect(row.locator(".name-cell")).to_contain_text(f"{last_name}, {first_name}")
    finally:
        try:
            offender_watch.delete_offender_by_national_id(national_id)
        except Exception:
            pass


def test_fr_09_latest_reading_matches_most_recent_trail_point(
    offender_watch: OffenderWatchPage,
    api_client: ApiClient,
) -> None:
    """FR-09: Latest Reading reflects the most recent trail point."""
    offender = _find_offender_with_trail(api_client)
    latest_point = _get_latest_trail_point(api_client, offender["id"])
    full_name = f"{offender['firstName']} {offender['lastName']}"

    offender_watch.search(full_name.split()[-1])
    offender_watch.select_offender_by_name(full_name)

    ui_values = offender_watch.get_latest_reading_values()

    assert float(ui_values["speed"]) == float(latest_point["speedKmh"])
    assert int(ui_values["battery"]) == int(latest_point["batteryPct"])
    assert int(ui_values["signal"]) == int(latest_point["signal"])
    assert ui_values["last_seen"], "Expected Last seen to be displayed in the UI"
