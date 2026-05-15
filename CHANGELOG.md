# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.7] - 2026-05-15

### Fixed
- Icon and logo now display correctly on the HA Integrations page
- Fixed HACS "icon not available" error — icon converted to RGB 256×256 PNG
- Added `icon.png` to repository root for HACS store card display

## [1.0.6] - 2026-05-15

### Added
- Expanded sensor support to 19 measurement types: pH, temperature, ORP, conductivity, salinity, chlorine, free chlorine, total chlorine, bromine, alkalinity, total alkalinity, calcium hardness, cyanuric acid, TDS, magnesium, biguanide, biguanide shock, salt, water balance
- Two new timestamp sensors per device: **Last Measurement (BLE)** and **Last Measurement (Sigfox)**
- Unknown measurement types returned by the API are now exposed as sensors rather than silently dropped
- Proper entity translations for all new sensor types

## [1.0.5] - 2026-05-15

### Fixed
- Data fetch no longer crashes with `UserPreferences.__init__() missing required positional arguments` — replaced `BlueConnectSimpleAPI.fetch_data()` with direct `BlueConnectApi` method calls to avoid internal `get_user()` call that breaks against the live API

## [1.0.4] - 2026-05-15

### Fixed
- Credential validation no longer crashes with `UserPreferences` missing fields — switched to direct HTTP POST to the login endpoint instead of using `blueconnect`'s `get_user()`
- Config flow now correctly distinguishes `invalid_auth` from `cannot_connect` errors
- Raised error log level from DEBUG to WARNING so failures are visible in HA logs

## [1.0.3] - 2026-05-15

### Fixed
- Credential errors were silently swallowed at DEBUG log level
- All errors incorrectly reported as "cannot connect" rather than "invalid credentials"

## [1.0.2] - 2026-05-15

### Fixed
- Corrected API method name from `get_user_info()` to `get_user()` (blueconnect package)

## [1.0.1] - 2026-05-15

### Added
- Brand logo and icon images

## [1.0.0] - 2026-05-15

### Added
- Initial release — cloud-based integration using the Blue Connect API
- Sensor entities for pH, ORP, temperature, salinity, conductivity, chlorine
- Credential-based setup via HA config flow
- HACS compatibility (`hacs.json`, versioned GitHub releases)
- DataUpdateCoordinator for efficient polling
- English translations
