# Blueriot Blue Connect Hub API Guide

This guide provides detailed information about the expected API structure for the Blueriot Blue Connect hub.

## Overview

The integration communicates with your hub via REST HTTP API endpoints. Your hub must expose these endpoints for the integration to function properly.

## Base URL

```
http://<hub_ip>:<hub_port>/api
```

**Default Port**: 8080

## Authentication

If your hub supports authentication, the integration will send an Authorization header:

```
Authorization: Bearer <api_key>
```

## Required Endpoints

### 1. Get All Devices

**Endpoint**: `GET /api/devices`

**Description**: Retrieve a list of all connected devices and their current sensor data.

**Response**:
```json
{
  "devices": [
    {
      "id": "device_001",
      "name": "Pool Analyzer",
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
    },
    {
      "id": "device_002",
      "name": "Backup Analyzer",
      "type": "pool_analyzer",
      "status": {
        "sensors": {
          "ph": 7.1,
          "chlorine": 1.6,
          "temperature": 25.5,
          "alkalinity": 85,
          "orp": 680,
          "conductivity": 1250
        }
      }
    }
  ]
}
```

**Field Descriptions**:

| Field | Type | Description |
|-------|------|-------------|
| `devices` | array | List of connected devices |
| `devices[].id` | string | Unique device identifier |
| `devices[].name` | string | Human-readable device name |
| `devices[].type` | string | Device type (e.g., "pool_analyzer") |
| `devices[].status.sensors` | object | Sensor data object |
| `devices[].status.sensors.ph` | float | pH level (0-14) |
| `devices[].status.sensors.chlorine` | float | Chlorine concentration (ppm) |
| `devices[].status.sensors.temperature` | float | Water temperature (°C) |
| `devices[].status.sensors.alkalinity` | float | Total alkalinity (ppm) |
| `devices[].status.sensors.orp` | float | Oxidation-Reduction Potential (mV) |
| `devices[].status.sensors.conductivity` | float | Water conductivity (µS/cm) |

### 2. Get Specific Device

**Endpoint**: `GET /api/devices/{device_id}`

**Description**: Retrieve information for a specific device.

**Parameters**:
- `device_id` (path): The unique identifier of the device

**Response**:
```json
{
  "id": "device_001",
  "name": "Pool Analyzer",
  "type": "pool_analyzer",
  "mac_address": "00:1A:2B:3C:4D:5E",
  "firmware_version": "1.2.3",
  "status": {
    "connected": true,
    "last_update": "2024-01-15T10:30:45Z",
    "sensors": {
      "ph": 7.2,
      "chlorine": 1.5,
      "temperature": 25.3,
      "alkalinity": 80,
      "orp": 650,
      "conductivity": 1200
    }
  }
}
```

### 3. Get Device Status

**Endpoint**: `GET /api/devices/{device_id}/status`

**Description**: Retrieve only the status information for a specific device.

**Parameters**:
- `device_id` (path): The unique identifier of the device

**Response**:
```json
{
  "connected": true,
  "last_update": "2024-01-15T10:30:45Z",
  "sensors": {
    "ph": 7.2,
    "chlorine": 1.5,
    "temperature": 25.3,
    "alkalinity": 80,
    "orp": 650,
    "conductivity": 1200
  }
}
```

## Error Responses

The API should return appropriate HTTP status codes:

| Status Code | Meaning | Example |
|------------|---------|---------|
| 200 | OK - Request successful | Device data retrieved |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Invalid or missing API key |
| 404 | Not Found | Device ID doesn't exist |
| 500 | Internal Server Error | Hub processing error |

**Error Response Format**:
```json
{
  "error": {
    "code": "INVALID_DEVICE",
    "message": "Device not found"
  }
}
```

## Implementation Examples

### Python Flask Hub Example

```python
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

# Mock device database
DEVICES = {
    "device_001": {
        "id": "device_001",
        "name": "Pool Analyzer",
        "type": "pool_analyzer",
        "mac_address": "00:1A:2B:3C:4D:5E",
        "firmware_version": "1.2.3",
    }
}

# Mock sensor data
SENSOR_DATA = {
    "device_001": {
        "ph": 7.2,
        "chlorine": 1.5,
        "temperature": 25.3,
        "alkalinity": 80,
        "orp": 650,
        "conductivity": 1200,
    }
}

@app.route('/api/devices', methods=['GET'])
def get_devices():
    devices = []
    for device_id, device_info in DEVICES.items():
        devices.append({
            "id": device_info["id"],
            "name": device_info["name"],
            "type": device_info["type"],
            "status": {
                "connected": True,
                "last_update": datetime.now().isoformat() + "Z",
                "sensors": SENSOR_DATA.get(device_id, {})
            }
        })
    return jsonify({"devices": devices})

@app.route('/api/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    if device_id not in DEVICES:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Device not found"}}), 404
    
    device = DEVICES[device_id]
    return jsonify({
        "id": device["id"],
        "name": device["name"],
        "type": device["type"],
        "mac_address": device["mac_address"],
        "firmware_version": device["firmware_version"],
        "status": {
            "connected": True,
            "last_update": datetime.now().isoformat() + "Z",
            "sensors": SENSOR_DATA.get(device_id, {})
        }
    })

@app.route('/api/devices/<device_id>/status', methods=['GET'])
def get_device_status(device_id):
    if device_id not in DEVICES:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Device not found"}}), 404
    
    return jsonify({
        "connected": True,
        "last_update": datetime.now().isoformat() + "Z",
        "sensors": SENSOR_DATA.get(device_id, {})
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### Node.js Express Hub Example

```javascript
const express = require('express');
const app = express();

const DEVICES = {
    "device_001": {
        "id": "device_001",
        "name": "Pool Analyzer",
        "type": "pool_analyzer",
        "mac_address": "00:1A:2B:3C:4D:5E",
        "firmware_version": "1.2.3"
    }
};

const SENSOR_DATA = {
    "device_001": {
        "ph": 7.2,
        "chlorine": 1.5,
        "temperature": 25.3,
        "alkalinity": 80,
        "orp": 650,
        "conductivity": 1200
    }
};

app.get('/api/devices', (req, res) => {
    const devices = Object.entries(DEVICES).map(([id, device]) => ({
        ...device,
        status: {
            connected: true,
            last_update: new Date().toISOString(),
            sensors: SENSOR_DATA[id] || {}
        }
    }));
    res.json({ devices });
});

app.get('/api/devices/:deviceId', (req, res) => {
    const device = DEVICES[req.params.deviceId];
    if (!device) {
        return res.status(404).json({ 
            error: { code: "NOT_FOUND", message: "Device not found" } 
        });
    }
    res.json({
        ...device,
        status: {
            connected: true,
            last_update: new Date().toISOString(),
            sensors: SENSOR_DATA[req.params.deviceId] || {}
        }
    });
});

app.get('/api/devices/:deviceId/status', (req, res) => {
    if (!DEVICES[req.params.deviceId]) {
        return res.status(404).json({ 
            error: { code: "NOT_FOUND", message: "Device not found" } 
        });
    }
    res.json({
        connected: true,
        last_update: new Date().toISOString(),
        sensors: SENSOR_DATA[req.params.deviceId] || {}
    });
});

app.listen(8080, () => {
    console.log('Hub API running on http://0.0.0.0:8080');
});
```

## Sensor Data Ranges

Typical sensor value ranges for pool analysis:

| Sensor | Min | Max | Typical | Unit |
|--------|-----|-----|---------|------|
| pH | 0 | 14 | 7.0-7.6 | pH |
| Chlorine | 0 | 10 | 1.0-3.0 | ppm |
| Temperature | 0 | 50 | 20-30 | °C |
| Alkalinity | 0 | 300 | 80-120 | ppm |
| ORP | 400 | 800 | 650-750 | mV |
| Conductivity | 0 | 5000 | 1000-1500 | µS/cm |

## Connection Troubleshooting

### Hub Not Responding

1. Verify hub is running and accessible:
   ```bash
   curl http://<hub_ip>:8080/api/devices
   ```

2. Check network connectivity:
   ```bash
   ping <hub_ip>
   ```

3. Verify firewall allows traffic to port 8080

### Invalid API Response

If the hub returns unexpected data:

1. Check for JSON formatting errors
2. Verify all required fields are present
3. Ensure numeric values are proper JSON numbers (not strings)
4. Check hub logs for errors

## Future Extensions

The integration can be extended to support:

- **Device Control**: POST endpoints to control device parameters
- **Calibration**: POST endpoints to calibrate sensors
- **Firmware Updates**: Endpoints for updating device firmware
- **Historical Data**: Endpoints to retrieve sensor history
- **Alerts**: Endpoints to set and manage alerts
- **Multiple Hubs**: Support for connecting to multiple hubs
