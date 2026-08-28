import math
import uuid
from datetime import datetime

import pytest

from automation.api.client import ApiClient


def _valid_offender_payload(**overrides: str) -> dict[str, str]:
    payload = {
        "firstName": "Auto",
        "lastName": "Test",
        "nationalId": str(uuid.uuid4().int)[:9],
        "dateOfBirth": "1990-01-15",
        "riskLevel": "Low",
        "status": "Active",
    }
    payload.update(overrides)
    return payload


def _find_offender_by_national_id(api_client: ApiClient, national_id: str) -> dict | None:
    page = 1
    page_size = 100
    offenders: list[dict] = []
    total = None

    while True:
        response = api_client.get("offenders", params={"page": page, "pageSize": page_size})
        assert response.status_code == 200
        data = response.json()
        if total is None:
            total = data["total"]
        offenders.extend(data["items"])
        if len(offenders) >= total or not data["items"]:
            break
        page += 1

    return next((offender for offender in offenders if offender.get("nationalId") == national_id), None)


def _assert_non_empty_error_description(response) -> None:
    text = response.text.strip()
    assert text, "Expected a non-empty error description in the response body"

    try:
        body = response.json()
    except ValueError:
        return

    if isinstance(body, str):
        assert body.strip()
        return

    if isinstance(body, dict):
        descriptions = [value for value in body.values() if isinstance(value, str) and value.strip()]
        assert descriptions, "Expected a non-empty error description in the response body"
        return

    if isinstance(body, list):
        descriptions = [value for value in body if isinstance(value, str) and value.strip()]
        assert descriptions, "Expected a non-empty error description in the response body"


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _find_offender_with_trail(api_client: ApiClient, min_points: int = 2) -> tuple[int, list]:
    response = api_client.get("offenders", params={"pageSize": 100})
    assert response.status_code == 200

    for offender in response.json()["items"]:
        trail_response = api_client.get(f"offenders/{offender['id']}/trail")
        assert trail_response.status_code == 200
        trail = trail_response.json()
        if len(trail) >= min_points:
            return offender["id"], trail

    pytest.fail(f"No offender with at least {min_points} trail points was found")


def test_api_01_pagination_metadata_consistency(api_client: ApiClient) -> None:
    """API-01: Pagination metadata must be consistent with total and pageSize."""
    response = api_client.get("offenders", params={"page": 1, "pageSize": 5})
    assert response.status_code == 200

    data = response.json()
    for field in ("items", "total", "page", "pageSize", "totalPages"):
        assert field in data, f"Missing pagination field: {field}"

    assert data["page"] == 1
    assert data["pageSize"] == 5
    assert isinstance(data["items"], list)
    assert len(data["items"]) <= data["pageSize"]

    expected_total_pages = math.ceil(data["total"] / data["pageSize"])
    assert data["totalPages"] == expected_total_pages


def test_api_02_unknown_offender_returns_404(api_client: ApiClient) -> None:
    """API-02: Requesting a non-existing offender returns HTTP 404."""
    page = 1
    page_size = 100
    existing_ids: set[int] = set()
    total = None

    while True:
        list_response = api_client.get("offenders", params={"page": page, "pageSize": page_size})
        assert list_response.status_code == 200
        data = list_response.json()
        if total is None:
            total = data["total"]
        existing_ids.update(offender["id"] for offender in data["items"])
        if len(existing_ids) >= total or not data["items"]:
            break
        page += 1

    unknown_id = max(existing_ids, default=0) + 1
    response = api_client.get(f"offenders/{unknown_id}")
    assert response.status_code == 404


def test_api_02_successful_creation_returns_201(api_client: ApiClient) -> None:
    """API-02: Successful offender creation returns HTTP 201."""
    payload = _valid_offender_payload()
    national_id = payload["nationalId"]
    created_id = None

    try:
        response = api_client.post("offenders", json=payload)
        assert response.status_code == 201

        persisted = _find_offender_by_national_id(api_client, national_id)
        assert persisted is not None
        created_id = persisted["id"]
    finally:
        if created_id is not None:
            api_client.delete(f"offenders/{created_id}")


def test_api_03_invalid_offender_payload_is_rejected(api_client: ApiClient) -> None:
    """API-03 / FR-03: Invalid offender payloads are rejected with HTTP 400."""
    payload = _valid_offender_payload()
    national_id = payload["nationalId"]
    del payload["lastName"]

    response = api_client.post("offenders", json=payload)
    try:
        assert response.status_code == 400
        _assert_non_empty_error_description(response)

        persisted = _find_offender_by_national_id(api_client, national_id)
        assert persisted is None
    finally:
        persisted = _find_offender_by_national_id(api_client, national_id)
        if persisted is not None:
            api_client.delete(f"offenders/{persisted['id']}")


def test_api_04_trail_points_returned_oldest_to_newest(api_client: ApiClient) -> None:
    """API-04: Trail points are returned in chronological order (oldest to newest)."""
    offender_id, trail = _find_offender_with_trail(api_client)

    response = api_client.get(f"offenders/{offender_id}/trail")
    assert response.status_code == 200
    trail = response.json()
    assert len(trail) >= 2

    timestamps = [_parse_timestamp(point["timestamp"]) for point in trail]
    expected_order = sorted(timestamps)
    assert timestamps == expected_order
