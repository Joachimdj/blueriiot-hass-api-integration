"""Constants for the Blueriot Blue Connect integration."""

DOMAIN = "blueriot_blue_connect"
MANUFACTURER = "Blueriot"
MODEL = "Blue Connect"

# Configuration keys
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_LANGUAGE = "language"
CONF_POLLING_INTERVAL = "polling_interval"

# Default values
DEFAULT_POLLING_INTERVAL = 1800  # seconds
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["fr", "es", "en", "nl", "de", "it", "pt", "cs"]

ATTR_LAST_UPDATE = "last_update"
ATTR_TREND = "trend"
ATTR_OK_MIN = "ok_min"
ATTR_OK_MAX = "ok_max"
ATTR_WARNING_LOW = "warning_low"
ATTR_WARNING_HIGH = "warning_high"
ATTR_ISSUER = "issuer"

# Entity types - Pool water analyzer sensors
SENSOR_TYPES = {
    "ph": {"unit": "pH", "icon": "mdi:water-opacity", "device_class": None},
    "temperature": {
        "unit": "°C",
        "icon": "mdi:thermometer-water",
        "device_class": None,
    },
    "orp": {"unit": "mV", "icon": "mdi:flash", "device_class": None},
    "salinity": {
        "unit": "ppm",
        "icon": "mdi:shaker-outline",
        "device_class": None,
    },
    "conductivity": {
        "unit": "µS/cm",
        "icon": "mdi:flash-triangle-outline",
        "device_class": None,
    },
    "chlorine": {
        "unit": "ppm",
        "icon": "mdi:chemical-weapon",
        "device_class": None,
    },
}

# Update intervals
SCAN_INTERVAL = DEFAULT_POLLING_INTERVAL
