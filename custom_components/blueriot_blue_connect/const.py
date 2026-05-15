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
    # Core measurements (all devices)
    "ph": {"unit": "pH", "icon": "mdi:water-opacity", "device_class": None},
    "temperature": {"unit": "°C", "icon": "mdi:thermometer-water", "device_class": None},
    "orp": {"unit": "mV", "icon": "mdi:flash", "device_class": None},
    # Blue Connect Plus
    "conductivity": {"unit": "µS/cm", "icon": "mdi:flash-triangle-outline", "device_class": None},
    "salinity": {"unit": "g/L", "icon": "mdi:shaker-outline", "device_class": None},
    # Strip / manual measurements returned by the API
    "chlorine": {"unit": "mg/L", "icon": "mdi:chemical-weapon", "device_class": None},
    "free_chlorine": {"unit": "mg/L", "icon": "mdi:chemical-weapon", "device_class": None},
    "total_chlorine": {"unit": "mg/L", "icon": "mdi:chemical-weapon", "device_class": None},
    "bromine": {"unit": "mg/L", "icon": "mdi:water-alert", "device_class": None},
    "alkalinity": {"unit": "mg/L", "icon": "mdi:water-check", "device_class": None},
    "total_alkalinity": {"unit": "mg/L", "icon": "mdi:water-check", "device_class": None},
    "calcium_hardness": {"unit": "mg/L", "icon": "mdi:water-minus", "device_class": None},
    "cyanuric_acid": {"unit": "mg/L", "icon": "mdi:molecule", "device_class": None},
    "tds": {"unit": "mg/L", "icon": "mdi:water-percent", "device_class": None},
    "magnesium": {"unit": "mg/L", "icon": "mdi:atom-variant", "device_class": None},
    "biguanide": {"unit": "mg/L", "icon": "mdi:flask", "device_class": None},
    "biguanide_shock": {"unit": "mg/L", "icon": "mdi:flask-plus", "device_class": None},
    "salt": {"unit": "g/L", "icon": "mdi:shaker-outline", "device_class": None},
    "balance": {"unit": "", "icon": "mdi:scale-balance", "device_class": None},
}

# Update intervals
SCAN_INTERVAL = DEFAULT_POLLING_INTERVAL
