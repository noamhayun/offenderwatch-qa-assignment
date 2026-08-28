import os

import pytest
from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from automation.api.client import ApiClient
from automation.config import API_BASE_URL, UI_BASE_URL


@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Browser:
    headless = os.getenv("HEADLESS", "true").lower() != "false"
    browser = playwright_instance.chromium.launch(headless=headless)
    yield browser
    browser.close()


@pytest.fixture
def page(browser: Browser) -> Page:
    context = browser.new_context(base_url=UI_BASE_URL)
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def api_client() -> ApiClient:
    client = ApiClient(API_BASE_URL)
    yield client
    client.close()
