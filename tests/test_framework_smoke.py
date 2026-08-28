from automation.api.client import ApiClient
from automation.config import API_BASE_URL, UI_BASE_URL


def test_ui_base_url_configured() -> None:
    assert UI_BASE_URL == "https://svcdemoaz.puremonitor.supercom.com/AQApplication/Noam"


def test_api_base_url_configured() -> None:
    assert API_BASE_URL == "https://svcdemoaz.puremonitor.supercom.com/AQApplication/Noam/api"


def test_api_client_fixture(api_client: ApiClient) -> None:
    assert isinstance(api_client, ApiClient)
    assert api_client.base_url == API_BASE_URL
    assert api_client.session is not None


def test_page_fixture(page) -> None:
    assert page.context is not None
