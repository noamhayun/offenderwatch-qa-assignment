import re

from playwright.sync_api import Page, expect

from automation.config import UI_BASE_URL


class OffenderWatchPage:
    PAGE_SIZE = 5

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self) -> None:
        self.page.goto(UI_BASE_URL)
        self.page.wait_for_load_state("networkidle")

    @property
    def search_input(self):
        return self.page.locator("input.search")

    def search(self, query: str) -> None:
        def matches_search_response(response) -> bool:
            if "/Noam/api/offenders" not in response.url or response.request.method != "GET":
                return False
            if query:
                return f"search={query}" in response.url
            return "search=" not in response.url

        with self.page.expect_response(matches_search_response):
            self.search_input.fill(query)

    def clear_search(self) -> None:
        self.search("")

    def offender_rows(self):
        return self.page.locator("table.grid tbody tr")

    def get_total_offender_count(self) -> int:
        stat = self.page.locator(".stats .stat").filter(has_text="Offenders").locator("b")
        return int(stat.inner_text())

    def get_pagination_text(self) -> str:
        return self.page.get_by_text(re.compile(r"Page \d+ of \d+")).inner_text()

    def parse_pagination(self) -> tuple[int, int, int]:
        match = re.search(r"Page (\d+) of (\d+) \((\d+) results\)", self.get_pagination_text())
        assert match, f"Unexpected pagination text: {self.get_pagination_text()!r}"
        current_page, total_pages, total_results = map(int, match.groups())
        return current_page, total_pages, total_results

    def get_visible_page_size(self) -> int:
        return self.offender_rows().count()

    def go_to_next_page(self) -> None:
        self.page.get_by_role("button", name=re.compile(r"Next", re.I)).click()
        self.page.wait_for_load_state("networkidle")

    def go_to_previous_page(self) -> None:
        self.page.get_by_role("button", name=re.compile(r"Prev", re.I)).click()
        self.page.wait_for_load_state("networkidle")

    def collect_visible_offender_names(self) -> list[str]:
        return [row.locator(".name-cell").inner_text().strip() for row in self.offender_rows().all()]

    def collect_all_accessible_offender_names(self) -> list[str]:
        self.clear_search()
        prev_button = self.page.get_by_role("button", name=re.compile(r"Prev", re.I))
        while prev_button.is_enabled():
            self.go_to_previous_page()

        _, total_pages, _ = self.parse_pagination()
        collected: list[str] = []

        for page_number in range(1, total_pages + 1):
            current_page, _, _ = self.parse_pagination()
            assert current_page == page_number
            collected.extend(self.collect_visible_offender_names())
            if page_number < total_pages:
                self.go_to_next_page()

        return collected

    def offender_row_by_name(self, full_name: str):
        first_name, last_name = full_name.split(" ", 1)
        display_name = f"{last_name}, {first_name}"
        return self.offender_rows().filter(has_text=display_name)

    def select_offender_by_name(self, full_name: str) -> None:
        row = self.offender_row_by_name(full_name)
        expect(row).to_have_count(1)
        with self.page.expect_response(lambda response: "/trail" in response.url):
            row.click()
        expect(self.page.get_by_text(re.compile(r"Latest reading", re.I))).to_be_visible()

    def click_add_offender(self) -> None:
        self.page.get_by_role("button", name=re.compile(r"Add Offender", re.I)).click()

    def fill_offender_form(
        self,
        *,
        first_name: str,
        last_name: str,
        national_id: str,
        date_of_birth: str,
        risk_level: str,
        status: str,
    ) -> None:
        expect(self.page.get_by_role("heading", name=re.compile(r"Add Offender", re.I))).to_be_visible()
        self.page.get_by_role("textbox", name=re.compile(r"First name", re.I)).fill(first_name)
        self.page.get_by_role("textbox", name=re.compile(r"Last name", re.I)).fill(last_name)
        self.page.get_by_role("textbox", name="National ID (unique)").fill(national_id)
        self.page.get_by_role("textbox", name=re.compile(r"Date of birth", re.I)).fill(date_of_birth)
        self.page.get_by_role("combobox", name=re.compile(r"Risk level", re.I)).select_option(risk_level)
        self.page.get_by_role("combobox", name=re.compile(r"Status", re.I)).select_option(status)

    def save_offender_form(self) -> None:
        with self.page.expect_response(
            lambda response: "/Noam/api/offenders" in response.url and response.request.method == "POST"
        ):
            self.page.get_by_role("button", name=re.compile(r"Create", re.I)).click()

    def delete_offender_by_name(self, full_name: str) -> None:
        row = self.offender_row_by_name(full_name)
        if row.count() == 0:
            self.search(full_name.split()[-1])
            row = self.offender_row_by_name(full_name)
        if row.count() == 0:
            return
        self.page.once("dialog", lambda dialog: dialog.accept())
        row.get_by_role("button", name=re.compile(r"Delete", re.I)).click()
        self.page.wait_for_load_state("networkidle")

    def delete_offender_by_national_id(self, national_id: str) -> None:
        row = self.offender_rows().filter(has_text=national_id)
        if row.count() == 0:
            self.clear_search()
            self.search(national_id)
            row = self.offender_rows().filter(has_text=national_id)
        if row.count() == 0:
            return
        self.page.once("dialog", lambda dialog: dialog.accept())
        row.get_by_role("button", name=re.compile(r"Delete", re.I)).click()
        self.page.wait_for_load_state("networkidle")

    def get_latest_reading_values(self) -> dict[str, str]:
        panel_text = self.page.locator(".detail-panel").inner_text()

        speed_match = re.search(r"([\d.]+)\s*km/h", panel_text, re.I)
        battery_match = re.search(r"([\d.]+)%\s*battery", panel_text, re.I)
        signal_match = re.search(r"(\d+)\s*/\s*5\s*signal", panel_text, re.I)
        last_seen_match = re.search(r"Last seen:\s*([^\n]+)", panel_text, re.I)

        return {
            "speed": speed_match.group(1) if speed_match else "",
            "battery": battery_match.group(1) if battery_match else "",
            "signal": signal_match.group(1) if signal_match else "",
            "last_seen": last_seen_match.group(1).strip() if last_seen_match else "",
        }
