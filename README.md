# offenderwatch-qa-assignment
QA home assignment for OffenderWatch – test design, execution, defect reporting, UI/API automation, and quality summary.

> **Source of Truth**
> This document is the assignment specification and PRD.
> Do not infer or invent requirements, validation rules, expected behavior, or API behavior that are not explicitly defined here.
> If a behavior is not specified, treat it as unspecified rather than making an assumption.
> The deployed application's current behavior must not be treated as expected behavior when it conflicts with this document.

# OffenderWatch — QA Home Assignment Requirements

## Assignment Context

**Application:** OffenderWatch — Offender Monitoring Console

**Application URL:**
https://svcdemoaz.puremonitor.supercom.com/AQApplication/Noam

**API Documentation (Swagger):**
https://svcdemoaz.puremonitor.supercom.com/AQApplication/swagger

**Expected effort:** 4–6 hours

**Deliverables:**

* Test case suite
* Bug reports
* Automation project
* QA dashboard

The application is a web console used by monitoring-center operators to track offenders wearing GPS devices. Operators manage the offender roster and review each offender's movement trail, including time, speed, device battery, and signal strength.

The Product Requirements below define the intended application behavior. Any deviation between these requirements and the actual application should be treated as a potential defect.

Requirement IDs must be referenced in test cases and bug reports.

---

# Product Requirements

## Offender Management

### FR-01 — Offender List and Pagination

The offender list displays all offenders, sorted alphabetically by last name, 5 per page.

The pager must give access to every offender:

* Number of pages = ceiling(total ÷ page size)
* The result count shown must match what is reachable.

### FR-02 — Search

Search filters offenders by:

* First name
* Last name
* National ID

Matching is:

* Partial (substring)
* Case-insensitive

### FR-03 — Create Offender

An operator can create an offender with:

* First name — required
* Last name — required
* National ID — required and must be unique across the system
* Date of birth — must be a date in the past
* Risk level — Low / Medium / High
* Status — Active / Inactive

Invalid input is rejected with a clear error message and nothing is saved.

### FR-04 — Edit Offender

An operator can edit an offender.

Saving the form must persist exactly the values shown in the form.

Fields the operator did not change must keep their previous values.

### FR-05 — Delete Offender

An operator can delete an offender after a confirmation prompt.

Deletion removes:

* The offender
* All of their location/trail data from the system

### FR-06 — Date Display

All dates in the UI are displayed in:

`DD/MM/YYYY`

The displayed date must match the stored value.

---

## Trail & Map

### FR-07 — Movement Trail

Selecting an offender shows their movement trail on the map.

Trail points are ordered chronologically:

`oldest → newest`

This ordering applies to:

* The trail table
* The line drawn on the map

The line must therefore follow the offender's actual movement.

### FR-08 — Trail Point Details

Clicking a trail point on the map shows that point's recorded data:

* Timestamp
* Speed (km/h)
* Battery (%)
* Signal strength (1–5)

### FR-09 — Latest Reading

The **Latest reading** panel shows the following values from the **most recent trail point**:

* Speed
* Battery
* Signal

**Last seen** shows the timestamp of the most recent trail point.

### FR-10 — Add Location Point

An operator can add a location point manually.

Validation:

* Latitude and longitude must be valid coordinates
* Speed ≥ 0
* Battery between 0 and 100
* Signal between 1 and 5

Invalid values are rejected.

---

## Dashboard & Statistics

### FR-11 — Top Bar Statistics

The top bar shows live, accurate totals for:

* Number of offenders
* Number of Active offenders
* Total trail points stored

Counts update after every create/delete operation, including deletion of trail data together with its offender.

---

# REST API Requirements

The full API is documented in Swagger.

The API is a first-class interface and must be tested directly, not only through the UI.

### API-01 — Offender List

`GET /api/offenders`

Supports:

* `search`
* `page`
* `pageSize`

Returns:

* `items`
* `total`
* `page`
* `pageSize`
* `totalPages`

Paging metadata must be consistent with the data.

### API-02 — HTTP Status Codes

Requesting a resource that does not exist returns:

`HTTP 404`

Examples include:

* `GET /api/offenders/{id}` for an unknown ID
* Trail request for an unknown resource

Successful creation returns:

`HTTP 201`

Successful deletion returns:

`HTTP 204`

### API-03 — API Validation

POST/PUT endpoints enforce the same validation rules as the UI defined by:

* FR-03
* FR-10

Invalid payloads return:

`HTTP 400`

with an error description.

### API-04 — Trail Ordering

`GET /api/offenders/{id}/trail`

returns the offender's trail points in chronological order.

### API-05 — Statistics

`GET /api/stats`

returns totals consistent with the actual stored data at all times.

---

# Assignment Deliverables

## Part 1 — Test Case Suite

Design a test suite that verifies the application against the PRD.

Each test case must include:

* ID and title
* Covered requirement ID(s) — FR-xx / API-xx
* Preconditions
* Steps
* Expected result
* Priority — High / Medium / Low
* Type — UI / API / Data / Negative

Selection and prioritization are valued over volume.

A focused suite of well-chosen cases, including negative and edge cases, is preferred over an exhaustive list of shallow tests.

---

## Part 2 — Test Execution & Bug Reports

Execute the test suite against the deployed application.

For every identified defect, submit a bug report containing:

* Clear one-line title
* Severity
* Priority
* Requirement violated — FR-xx / API-xx
* Steps to reproduce
* Actual result
* Expected result
* Suspected defect layer — UI / API / data
* Evidence supporting the layer analysis

Where relevant, compare API responses with UI behavior before determining the defect layer.

---

## Part 3 — Automation

Automate a meaningful subset of the test suite.

Minimum:

* 5 automated UI scenarios
* 5 automated API scenarios

Automated tests must assert expected behavior defined by the PRD.

A test that fails because of a real product defect should remain failing, be clearly marked, and reference the corresponding bug report.

The automation project should have a clean structure using page objects, fixtures, and helpers where appropriate.

A README must explain:

* Installation
* How to run the tests
* How to interpret the results

---

## Part 4 — QA Dashboard

Create a dashboard populated with real results from testing and automation.

It must show at least:

### Test execution

* Total test cases
* Executed
* Passed
* Failed
* Blocked / not run

### Requirement coverage

* Which FR/API requirements are covered
* Their pass/fail state

### Defects

Counts by:

* Severity
* Status — Open / Fixed / Retest

### Automation

* Automated vs. manual cases
* Latest automation run result

### Release Recommendation

One-line overall:

**Go / No-Go**

The recommendation must be based on the actual testing data.

---

# Submission

Deliverables:

1. Test case suite with requirement traceability
2. Bug reports
3. Automation project with README
4. QA dashboard populated with real results

Submit everything as:

* A single ZIP file, or
* A Git repository link

---

# Practical Notes

* Seeded test data contains 11 offenders and their trails.
* Additional offenders may be created during testing.
* Map tiles load from OpenStreetMap and require internet access.
* Trail data comes from the application's own API.
* Test through both the UI and directly against the API.
* Some defects may only become visible when comparing UI and API behavior.
* If application data becomes unusable during testing, request a reset.
* During the interview follow-up, the candidate will walk through the dashboard, defend the bug analysis, and run the automation live.
