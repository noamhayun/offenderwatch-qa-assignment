# OffenderWatch QA Assignment

## Overview

This repository contains the QA deliverables for the OffenderWatch application, including:

- Manual test suite and execution results
- Bug reports
- UI automation
- API automation
- Requirements documentation

Testing was performed against the assigned Noam application instance:

- UI: `https://svcdemoaz.puremonitor.supercom.com/AQApplication/Noam`
- API: `https://svcdemoaz.puremonitor.supercom.com/AQApplication/Noam/api`

## Repository Structure

- `docs/test-cases/` — manual test suite and execution results (`OffenderWatch_Test_Suite.xlsx`)
- `bugs/` — documented defects
- `evidence/` — supporting screenshots for manual and automated findings
- `automation/` — automation framework (configuration, API client, UI page objects)
- `tests/` — automated pytest tests (`tests/ui/`, `tests/api/`)
- `docs/requirements/` — assignment and requirements documentation (`assignment.md`)

## Automation Stack

The automation project uses:

- Python
- pytest
- Playwright (UI automation)
- requests (API automation)

Dependencies are defined in `requirements.txt`.

## Prerequisites

- Python 3 with `pip`
- Network access to the deployed Noam application instance
- Network access to download Playwright browser binaries during setup

## Installation

From the repository root:

```bash
pip install -r requirements.txt
playwright install chromium
```

## Running the Automated Tests

Run all automated tests:

```bash
pytest
```

Run UI tests only:

```bash
pytest tests/ui
```

Run API tests only:

```bash
pytest tests/api
```

Optional environment variables (see `automation/config.py` and `tests/conftest.py`):

- `UI_BASE_URL` — override the default UI base URL
- `API_BASE_URL` — override the default API base URL
- `HEADLESS=false` — run Playwright in headed mode (headless is the default)

## Reading the Results

pytest reports **Passed** and **Failed** tests in the terminal.

Some automated tests intentionally fail because they expose confirmed defects in the application. These failures are valid QA results, not automation framework failures.

The automated assertions are based on expected behavior defined in the PRD (`docs/requirements/assignment.md`). When the application violates the PRD, the corresponding test is expected to fail.

Known product-defect failures are documented under `bugs/`. Examples referenced by the automated suite include:

- **BUG-001** — pagination metadata / access (FR-01, API-01)
- **BUG-002** — case-insensitive search (FR-02)

Review the terminal output and the relevant bug report for failed tests.

## Test Coverage

The automated suite includes:

- **5 UI scenarios** in `tests/ui/test_offenders_ui.py`
- **5 API scenarios** in `tests/api/test_offenders_api.py`

This is a meaningful subset of the larger manual test suite in `docs/test-cases/OffenderWatch_Test_Suite.xlsx`.

The repository also contains framework smoke checks in `tests/test_framework_smoke.py` for fixture and configuration validation.

## API Testing Note

The provided Swagger UI is configured against `/AQApplication/api` rather than the assigned `/AQApplication/Noam/api` instance.

Therefore, manual API validation was performed directly against the assigned Noam instance using Postman/browser requests.

The automated API tests use the configured base URL in `automation/config.py`:

`https://svcdemoaz.puremonitor.supercom.com/AQApplication/Noam/api`

## Known Defects and Test Evidence

Documented defects are available under `bugs/`.

Manual execution results are available in:

`docs/test-cases/OffenderWatch_Test_Suite.xlsx`

Supporting evidence screenshots are stored under `evidence/ui/` and `evidence/api/`.

## Notes

- UI tests require Playwright Chromium and internet access (the application loads map tiles from OpenStreetMap).
- API and UI tests run against the live deployed Noam instance; results depend on the current application data.
- Use `HEADLESS=false` when debugging UI tests locally in a visible browser.
