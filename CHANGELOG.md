# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.7] - 2026-05-15

### Added
- Icon and logo displayed on the HA Integrations page and HACS store card

## [1.0.6] - 2026-05-15

### Added
- 19 measurement sensor types: pH, temperature, ORP, conductivity, salinity, chlorine, free chlorine, total chlorine, bromine, alkalinity, total alkalinity, calcium hardness, cyanuric acid, TDS, magnesium, biguanide, biguanide shock, salt, water balance
- Last Measurement timestamp sensors (BLE and Sigfox) per device
- Unknown measurement types returned by the API are automatically exposed as sensors

## [1.0.0] - 2026-05-15

### Added
- Initial release — cloud-based integration using the Blue Connect API
- Credential-based setup via HA config flow
- HACS compatibility
- DataUpdateCoordinator for efficient polling
- English translations
