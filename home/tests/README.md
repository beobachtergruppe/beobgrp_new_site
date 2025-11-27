# Testing Documentation

This project includes tests for the Wagtail models to protect against API changes and ensure functionality works correctly.

## Test Structure

The tests use Django's standard `TestCase` for simplicity and reliability:

- `test_setup.py` - Basic infrastructure tests (3 tests)
- `test_home_page.py` - Tests for HomePage model (4 tests)
- `test_events_simple.py` - Tests for EventPage and SingleEvent models (5 tests)
- `test_gallery_simple.py` - Tests for Gallery models (6 tests)
- `test_blocks_simple.py` - Tests for custom blocks (3 tests)
- `test_anchors.py` - Tests for anchor link functionality (15 tests)

**Total: 38 tests** covering all main Wagtail models and custom functionality.

**Note**: The simplified approach focuses on model instantiation, configuration, and basic functionality rather than full integration testing. This provides reliable, fast tests that protect against API changes.

## Running Tests

### Prerequisites

The tests require a PostgreSQL database with permissions to create test databases. Make sure your PostgreSQL user has the `CREATEDB` privilege:

```sql
ALTER USER wagtail CREATEDB;
```

### If Tests Hang

If tests hang indefinitely, drop the test database:

```bash
PGPASSWORD="$WAGTAIL_DB_PASSWORD" psql -h localhost -U wagtail -d postgres -c "DROP DATABASE IF EXISTS test_beobgrp_site;"
```

This can happen if a previous test run was interrupted or if the test database wasn't properly cleaned up.

### Run All Tests

```bash
python manage.py test home.tests
```

### Run Specific Test Files

```bash
# Test HomePage
python manage.py test home.tests.test_home_page

# Test Setup
python manage.py test home.tests.test_setup

# Test Events
python manage.py test home.tests.test_events_simple

# Test Gallery
python manage.py test home.tests.test_gallery_simple

# Test Blocks
python manage.py test home.tests.test_blocks_simple
```

### Run Specific Test Classes

```bash
python manage.py test home.tests.test_home_page.HomePageTests
```

### Run with Verbose Output

```bash
python manage.py test home.tests -v 2
```

## What the Tests Cover

The tests focus on:

1. **Model instantiation** - Ensure all models can be created with required fields
2. **Configuration validation** - Check subpage_types and field existence  
3. **Critical functionality** - Verify event types, required fields, block structures
4. **API protection** - Detect breaking changes in Wagtail/Django APIs

This approach prioritizes reliability and speed (~75ms execution time) over comprehensive integration testing.

### Test Coverage Details

**HomePage (4 tests)**
- Model instantiation
- Subpage types configuration
- StreamField body existence and content handling

**EventPage & SingleEvent (5 tests)**
- Model instantiation with required fields
- Event type constants (Vortrag, Hybrid, Online, Beobachtungsabend, Ausflug)
- Reservation logic fields
- Required field existence (event_title, start_time, referent, abstract, etc.)

**Gallery Models (6 tests)**
- GalleryIndexPage, GalleryPage, PhotoPage instantiation
- Subpage type hierarchies
- Required field existence (description, photo, date)

**Custom Blocks (3 tests)**
- LinkBlock field structure (link_type, internal_page, external_url)
- ImageWithCaptionBlock field structure

**Anchor Links (15 tests)**
- Anchor ID generation from various text inputs
- Special character handling (umlauts, punctuation, spaces)
- Anchor extraction from pages with StreamField content
- Support across different page types (HomePage, EventPage)
- Edge cases (empty body, duplicate headings, no headings)

**Setup (3 tests)**
- Basic Wagtail infrastructure (Page, Site creation)
- Model imports

## Test Approach

These tests use Django's standard `TestCase` rather than Wagtail's `WagtailPageTestCase` for better reliability and performance. They focus on model structure and configuration rather than full integration testing.

## Notes

- Tests use the same database configuration as development (PostgreSQL)
- Tests are isolated and can run in any order
- Simplified approach avoids database hanging issues with complex Wagtail page hierarchies
- Tests protect against API changes while remaining fast and reliable
