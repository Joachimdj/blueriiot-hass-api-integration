# Blueriot Blue Connect - Home Assistant Integration

Cloud API-backed custom integration for Blueriot Blue Connect pool analyzers.

## Features

- Cloud login with Blueriot account credentials
- Sensors for pH, chlorine, temperature, ORP, salinity, conductivity
- Measurement metadata in attributes (trend, ranges, timestamp, issuer)
- Config flow in Home Assistant UI
- HACS-compatible structure

## Installation

### HACS (Recommended)

1. Open HACS -> Integrations.
2. Add this repository as a custom repository (Integration).
3. Install Blueriot Blue Connect.
4. Restart Home Assistant.

### Manual

1. Copy [custom_components/blueriot_blue_connect](custom_components/blueriot_blue_connect) to your Home Assistant config under [custom_components](custom_components).
2. Restart Home Assistant.

## Configuration

1. Open Settings -> Devices & Services -> Add Integration.
2. Select Blueriot Blue Connect.
3. Enter:
   - Username
   - Password
   - Language (en, fr, es, nl, de, it, pt, cs)
   - Polling interval in seconds

## Notes

- This implementation is cloud-poll based, not local-hub REST based.
- Polling too frequently may hit API rate limits. A 30-minute default is recommended.

## Entities

Created sensor entities depend on measurements available in the account:

- pH
- chlorine
- temperature
- ORP
- salinity
- conductivity

## Troubleshooting

- If setup fails with authentication error, verify account credentials in the official app first.
- If entities are missing, check whether that measurement is available for your device model and firmware.
- Review Home Assistant logs for [custom_components.blueriot_blue_connect](custom_components/blueriot_blue_connect).

## Development

Main integration code is in [custom_components/blueriot_blue_connect](custom_components/blueriot_blue_connect).

## License

MIT
