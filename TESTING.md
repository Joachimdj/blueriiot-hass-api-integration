# Connection Testing Guide

This guide explains how to test connectivity to your Blueriot Blue Connect hub.

## Quick Test

### 1. Start the Mock Hub (Optional)

For testing without a real hub:

```bash
python3 mock_hub.py
```

This starts a mock hub server on `http://localhost:8080` with simulated pool analyzer data.

### 2. Run the Connection Test

```bash
python3 test_connection.py <host> <port> [api_key]
```

**Examples:**

```bash
# Test local mock hub
python3 test_connection.py localhost 8080

# Test real hub with IP address
python3 test_connection.py 192.168.1.100 8080

# Test with API key authentication
python3 test_connection.py 192.168.1.100 8080 "your_api_key_here"

# Interactive mode (will prompt for details)
python3 test_connection.py
```

## Test Output

### Successful Connection

```
============================================================
Blueriot Blue Connect - Hub Connection Test
============================================================

🔍 Testing connection to hub at localhost:8080...
  📡 Fetching devices from http://localhost:8080/api/devices...

✅ Successfully connected to hub!
   Found 1 device(s):

   📦 Device: Pool Analyzer
      ID: device_001
      Type: pool_analyzer
      Sensors: 6 found
        • ph: 7.2
        • chlorine: 1.5
        • temperature: 25.3
        • alkalinity: 80
        • orp: 650
        • conductivity: 1200

============================================================
✅ Connection test PASSED - Hub is accessible!
============================================================
```

### Failed Connection

```
============================================================
Blueriot Blue Connect - Hub Connection Test
============================================================

🔍 Testing connection to hub at 192.168.1.100:8080...
  📡 Fetching devices from http://192.168.1.100:8080/api/devices...

❌ API Error: Connection error: ...

============================================================
❌ Connection test FAILED - Unable to reach hub
Troubleshooting steps:
  1. Verify hub IP address is correct
  2. Verify hub port is correct (default: 8080)
  3. Ensure hub is powered on and connected to network
  4. Check firewall allows connection to hub port
  5. Verify API key if required by hub
============================================================
```

## Testing Workflow

### Step 1: Test Mock Hub

Start with the mock hub to verify the integration code works:

```bash
# Terminal 1: Start mock hub
python3 mock_hub.py

# Terminal 2: Test connection
python3 test_connection.py localhost 8080
```

### Step 2: Test Real Hub

Once working with mock hub, test with your real Blueriot hub:

```bash
# Get your hub's IP address
# (from your router or hub settings)

python3 test_connection.py <hub_ip_address> 8080
```

### Step 3: Verify Hub API

You can also test the hub API directly:

```bash
# Test with curl
curl http://localhost:8080/api/devices
curl http://localhost:8080/api/devices/device_001
curl http://localhost:8080/api/devices/device_001/status
```

## What the Test Does

1. **Connects to Hub**: Establishes HTTP connection to specified host/port
2. **Fetches Devices**: Requests device list from `/api/devices` endpoint
3. **Validates Response**: Checks for proper JSON structure and device data
4. **Displays Details**: Shows each device and its sensor readings
5. **Reports Status**: Success or failure with troubleshooting tips

## Expected Hub Response

The hub should return a response like this:

```json
{
  "devices": [
    {
      "id": "device_001",
      "name": "Pool Analyzer",
      "type": "pool_analyzer",
      "status": {
        "connected": true,
        "last_update": "2026-05-15T19:55:05.020198Z",
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
  ]
}
```

## Troubleshooting

### "Connection error"

**Cause**: Hub is not reachable at the specified address

**Solutions**:
1. Verify hub IP address: `ping <hub_ip>`
2. Check hub is powered on
3. Verify correct port (usually 8080)
4. Check firewall rules allow port 8080

### "401 Unauthorized"

**Cause**: API authentication failed

**Solutions**:
1. Verify API key is correct
2. Check hub requires authentication
3. Try without API key if optional

### "404 Not Found"

**Cause**: Hub endpoint doesn't match expected structure

**Solutions**:
1. Verify hub API implements required endpoints
2. Check hub firmware version
3. Review HUB_API_GUIDE.md for specifications

### "No devices found"

**Cause**: Hub returned empty device list

**Solutions**:
1. Verify hub has devices connected
2. Check device type matches "pool_analyzer"
3. Verify devices have sensor data

## Mock Hub Features

The mock hub (`mock_hub.py`) simulates:

- **Device Discovery**: Returns a pool analyzer device
- **Sensor Data**: Provides realistic pool water readings
- **Multiple Endpoints**: Implements all required API endpoints
- **Error Handling**: Returns proper HTTP status codes
- **Logging**: Prints request/response details

### Mock Hub Endpoints

```
GET /                           # API info
GET /api/devices                # All devices
GET /api/devices/{device_id}    # Specific device
GET /api/devices/{device_id}/status  # Device status
```

## Testing Integration with Home Assistant

Once connection test passes:

1. Copy integration to Home Assistant custom_components:
   ```bash
   cp -r custom_components/blueriot_blue_connect ~/.homeassistant/custom_components/
   ```

2. Restart Home Assistant

3. Add integration:
   - Settings → Devices & Services → Create Integration
   - Search "Blueriot Blue Connect"
   - Enter hub details from successful connection test

## CI/CD Testing

### Automated Testing

For GitHub Actions or other CI/CD:

```yaml
- name: Test Hub Connection
  run: |
    python3 -m pip install aiohttp
    python3 test_connection.py localhost 8080
```

### Docker Testing

```dockerfile
FROM python:3.11
WORKDIR /app
COPY . /app
RUN pip install aiohttp
CMD ["python3", "test_connection.py", "localhost", "8080"]
```

## Performance Testing

To measure response times:

```python
import time
import asyncio
from custom_components.blueriot_blue_connect.api import BlueriotBlueConnectAPI

async def measure_performance():
    api = BlueriotBlueConnectAPI("localhost", 8080)
    
    start = time.time()
    devices = await api.async_get_devices()
    elapsed = time.time() - start
    
    print(f"Response time: {elapsed:.3f}s")
    print(f"Devices: {len(devices.get('devices', []))}")
    
    await api.async_close()

asyncio.run(measure_performance())
```

## Next Steps

After successful connection test:

1. ✅ Integration code is working
2. ✅ Hub is reachable and responsive
3. → Install in Home Assistant
4. → Configure in Home Assistant UI
5. → Monitor sensors in Home Assistant dashboard
