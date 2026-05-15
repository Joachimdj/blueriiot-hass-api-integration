# Blueriot Blue Connect Integration - Complete Setup Guide

## 📋 Project Overview

This is a complete Home Assistant integration for the **Blueriot Blue Connect** pool water analyzer system. The integration is fully HACS-compatible and production-ready.

## ✅ What's Included

### Core Integration Files

- **`__init__.py`** - Main integration entry point and setup logic
- **`manifest.json`** - Integration metadata for HACS
- **`const.py`** - Configuration constants and sensor definitions
- **`api.py`** - HTTP API client for communicating with the hub
- **`config_flow.py`** - User-friendly configuration interface
- **`sensor.py`** - Pool analyzer sensor entities (pH, chlorine, temperature, etc.)
- **`strings.json`** - Translatable strings for UI

### Documentation

- **`README.md`** - Main documentation with installation and usage instructions
- **`HUB_API_GUIDE.md`** - Detailed API specification for hub developers
- **`HACS_SUBMISSION.md`** - Guide for submitting to HACS
- **`DEVELOPMENT.md`** - Development setup and testing guide
- **`CHANGELOG.md`** - Version history
- **`LICENSE`** - MIT License

### Configuration Files

- **`requirements.txt`** - Python dependencies
- **`.gitignore`** - Git ignore rules

## 🚀 Quick Start

### For Users (Install via HACS)

1. Open Home Assistant
2. Go to **HACS** → **Integrations**
3. Click **+** → Search "Blueriot Blue Connect"
4. Click **Install**
5. Restart Home Assistant
6. Go to **Settings** → **Devices & Services** → **Integrations**
7. Click **Create Integration** → "Blueriot Blue Connect"
8. Enter your hub's IP address and port

### For Developers (Local Installation)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/blueriot-hass.git
   cd blueriot-hass
   ```

2. Copy to Home Assistant custom_components:
   ```bash
   cp -r custom_components/blueriot_blue_connect ~/.homeassistant/custom_components/
   ```

3. Restart Home Assistant

4. Set up integration (see user steps above)

## 🔧 Configuration

### Minimum Configuration

```
Hub IP Address: 192.168.1.100
Port: 8080
```

### Full Configuration

```
Hub IP Address: 192.168.1.100
Port: 8080
API Key: (if required by your hub)
Polling Interval: 60 (seconds)
```

## 📊 Supported Entities

The integration creates sensor entities for:

| Entity | Unit | Range | Description |
|--------|------|-------|-------------|
| pH Level | pH | 0-14 | Water acidity/alkalinity |
| Chlorine Level | ppm | 0-10 | Chlorine concentration |
| Water Temperature | °C | 0-50 | Pool water temperature |
| Alkalinity | ppm | 0-300 | Total alkalinity |
| ORP Level | mV | 400-800 | Oxidation-reduction potential |
| Conductivity | µS/cm | 0-5000 | Water conductivity |

## 🎯 Hub Requirements

Your Blueriot Blue Connect hub must provide the following API endpoints:

### GET /api/devices
Returns list of all connected devices with current sensor data.

### GET /api/devices/{device_id}
Returns information for a specific device.

### GET /api/devices/{device_id}/status
Returns current status and sensor data.

See [HUB_API_GUIDE.md](HUB_API_GUIDE.md) for complete API specifications and implementation examples.

## 🔄 How It Works

1. **Connection**: Integration establishes HTTP connection to hub
2. **Discovery**: Retrieves list of pool analyzer devices
3. **Entity Creation**: Creates Home Assistant sensor entities for each device
4. **Polling**: Periodically fetches sensor data from hub
5. **Updates**: Updates sensor values in Home Assistant

## 🛠️ Development

### Project Structure

```
blueriot-hass/
├── custom_components/
│   └── blueriot_blue_connect/
│       ├── __init__.py           # Integration setup
│       ├── manifest.json         # HACS metadata
│       ├── const.py              # Constants
│       ├── api.py                # Hub API client
│       ├── config_flow.py        # Configuration UI
│       ├── sensor.py             # Sensor entities
│       ├── strings.json          # Translations
│       └── translations/
│           └── en.json           # English translations
├── README.md                      # User documentation
├── HUB_API_GUIDE.md              # API specification
├── HACS_SUBMISSION.md            # HACS submission guide
├── DEVELOPMENT.md                # Developer guide
├── CHANGELOG.md                  # Version history
├── LICENSE                       # MIT License
├── requirements.txt              # Python dependencies
└── .gitignore                    # Git ignore rules
```

### Running Locally

```bash
# Set up development environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Test with mock hub
python test_mock_hub.py

# In another terminal, add integration in Home Assistant
# with IP: localhost, Port: 8080
```

## 🚀 Publishing to HACS

1. Push to GitHub repository
2. Create GitHub release with proper version tag
3. Submit integration via [HACS Repository Issues](https://github.com/hacs/default/issues/new/choose)
4. HACS maintainers will review and accept
5. Integration becomes available to all HACS users

See [HACS_SUBMISSION.md](HACS_SUBMISSION.md) for detailed instructions.

## 📝 Manifest Configuration

The integration's `manifest.json` includes:

- **domain**: Unique integration identifier
- **name**: Display name in HACS
- **version**: Current version (semantic versioning)
- **requirements**: Python package dependencies
- **integration_type**: Set to "hub" for hub-based integrations

## 🔐 Security

- ✅ No hardcoded credentials
- ✅ Optional API key support
- ✅ HTTPS-ready architecture
- ✅ Secure error handling
- ✅ Input validation

## 🐛 Troubleshooting

### Hub Not Connecting

```bash
# Test hub connectivity
curl http://<hub_ip>:8080/api/devices
```

### Sensors Not Appearing

1. Check Home Assistant logs
2. Verify hub returns device type containing "pool"
3. Verify sensor data structure matches API specification

### API Errors

- **401 Unauthorized**: Check API key configuration
- **404 Not Found**: Verify endpoint paths match specification
- **Connection Failed**: Verify IP address, port, and network connectivity

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| README.md | User guide for installation and usage |
| HUB_API_GUIDE.md | Technical API specification for hub developers |
| HACS_SUBMISSION.md | Instructions for submitting to HACS |
| DEVELOPMENT.md | Setup guide for contributors/developers |
| CHANGELOG.md | Version history and release notes |

## 🤝 Contributing

To contribute improvements:

1. Fork the repository
2. Create a feature branch
3. Make changes with clear commit messages
4. Test thoroughly
5. Submit a pull request

## 📄 License

This integration is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Home Assistant Documentation](https://developers.home-assistant.io/)
- [HACS Project](https://hacs.xyz/)
- [Integration Development Guide](https://developers.home-assistant.io/docs/integration_index/)
- [Blueriot](https://blueriot.com/)

## 📞 Support

- **Documentation**: See README.md and HUB_API_GUIDE.md
- **Issues**: Create an issue on GitHub
- **Questions**: Use Home Assistant Community Forum

---

**Ready to get started?**

1. For users: Install via HACS (when available)
2. For developers: Follow [DEVELOPMENT.md](DEVELOPMENT.md)
3. For hub developers: See [HUB_API_GUIDE.md](HUB_API_GUIDE.md)
