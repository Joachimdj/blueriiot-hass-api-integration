# Development Setup Guide

## Quick Start

### Prerequisites

- Python 3.11+
- pip
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/blueriot-hass.git
cd blueriot-hass
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Home Assistant Testing

### Using Home Assistant Dev Container

1. Install Home Assistant development container:
```bash
git clone https://github.com/home-assistant/core.git
cd core
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Copy integration to custom_components:
```bash
cp -r /path/to/blueriot-hass/custom_components/blueriot_blue_connect \
  home-assistant/custom_components/
```

3. Run Home Assistant:
```bash
hass -c ./config
```

### Using Docker

1. Create a test Home Assistant instance:
```bash
docker run --rm \
  -v /path/to/blueriot-hass/custom_components:/config/custom_components \
  -p 8123:8123 \
  homeassistant/home-assistant:latest
```

2. Access at http://localhost:8123

## Code Quality

### Linting

```bash
# Install linting tools
pip install flake8 black isort mypy

# Format code
black custom_components/

# Sort imports
isort custom_components/

# Check for issues
flake8 custom_components/

# Type checking
mypy custom_components/
```

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

## Testing

### Mock Hub Setup

For local testing without a real hub, use the mock API:

```python
# test_mock_hub.py
import aiohttp
from aiohttp import web
import json

async def get_devices(request):
    return web.json_response({
        "devices": [{
            "id": "test_device",
            "name": "Test Pool Analyzer",
            "type": "pool_analyzer",
            "status": {
                "sensors": {
                    "ph": 7.2,
                    "chlorine": 1.5,
                    "temperature": 25.3,
                    "alkalinity": 80,
                    "orp": 650,
                    "conductivity": 1200
                }
            }
        }]
    })

app = web.Application()
app.router.add_get('/api/devices', get_devices)

if __name__ == '__main__':
    web.run_app(app, port=8080)
```

Run: `python test_mock_hub.py`

Then in Home Assistant, add integration with:
- Host: localhost
- Port: 8080

## Documentation

### API Documentation

See [HUB_API_GUIDE.md](HUB_API_GUIDE.md) for detailed hub API specifications.

### Integration Flow

1. User configures integration in Home Assistant
2. Integration connects to hub via HTTP API
3. Hub returns list of devices and sensor data
4. Integration creates Home Assistant sensor entities
5. DataUpdateCoordinator polls hub on interval
6. Sensor values update in Home Assistant

## Debugging

### Enable Verbose Logging

Add to `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.blueriot_blue_connect: debug
```

### Check Logs

Home Assistant UI → Settings → System → Logs

Search for "blueriot"

## Common Issues

### ImportError: No module named 'custom_components.blueriot_blue_connect'

- Ensure integration is in correct directory: `custom_components/blueriot_blue_connect/`
- Restart Home Assistant

### API Connection Failed

- Check hub IP address and port
- Verify hub is running: `curl http://<hub_ip>:8080/api/devices`
- Check firewall settings

### Sensors Not Appearing

- Check Home Assistant logs for errors
- Verify hub returns correct device type (should contain "pool")
- Verify sensor data structure matches expected format

## Building and Packaging

### Create Distribution

```bash
python setup.py sdist bdist_wheel
```

### Submit to PyPI (Optional)

```bash
pip install twine
twine upload dist/*
```

## Release Process

1. Update version in `custom_components/blueriot_blue_connect/manifest.json`
2. Update `CHANGELOG.md`
3. Commit: `git commit -am "Release v1.x.x"`
4. Tag: `git tag v1.x.x`
5. Push: `git push origin --tags`
6. Create GitHub Release with changelog
7. HACS will auto-detect the new version

## Useful Links

- [Home Assistant Dev Docs](https://developers.home-assistant.io/)
- [Integration Development](https://developers.home-assistant.io/docs/integration_index/)
- [HACS Documentation](https://hacs.xyz/)
- [Python Testing](https://docs.pytest.org/)
