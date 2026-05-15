#!/usr/bin/env python3
"""
Mock hub server for testing the Blueriot Blue Connect integration.

Run this to simulate a hub on localhost:8080 for local integration testing.
"""

import json
from datetime import datetime
from aiohttp import web


# Mock device data
MOCK_DEVICES = {
    "device_001": {
        "id": "device_001",
        "name": "Pool Analyzer",
        "type": "pool_analyzer",
        "mac_address": "00:1A:2B:3C:4D:5E",
        "firmware_version": "1.2.3",
    }
}

# Mock sensor data (simulated pool readings)
MOCK_SENSORS = {
    "device_001": {
        "ph": 7.2,
        "chlorine": 1.5,
        "temperature": 25.3,
        "alkalinity": 80,
        "orp": 650,
        "conductivity": 1200,
    }
}


async def get_devices(request):
    """GET /api/devices - Return all devices and their sensor data."""
    print(f"📥 Request: GET /api/devices")
    
    devices = []
    for device_id, device_info in MOCK_DEVICES.items():
        devices.append({
            "id": device_info["id"],
            "name": device_info["name"],
            "type": device_info["type"],
            "status": {
                "connected": True,
                "last_update": datetime.now().isoformat() + "Z",
                "sensors": MOCK_SENSORS.get(device_id, {})
            }
        })
    
    response = {"devices": devices}
    print(f"📤 Response: {json.dumps(response, indent=2)}\n")
    
    return web.json_response(response)


async def get_device(request):
    """GET /api/devices/{device_id} - Return specific device."""
    device_id = request.match_info['device_id']
    print(f"📥 Request: GET /api/devices/{device_id}")
    
    if device_id not in MOCK_DEVICES:
        print(f"📤 Response: 404 Not Found\n")
        return web.json_response(
            {"error": {"code": "NOT_FOUND", "message": "Device not found"}},
            status=404
        )
    
    device = MOCK_DEVICES[device_id]
    response = {
        "id": device["id"],
        "name": device["name"],
        "type": device["type"],
        "mac_address": device["mac_address"],
        "firmware_version": device["firmware_version"],
        "status": {
            "connected": True,
            "last_update": datetime.now().isoformat() + "Z",
            "sensors": MOCK_SENSORS.get(device_id, {})
        }
    }
    
    print(f"📤 Response: {json.dumps(response, indent=2)}\n")
    return web.json_response(response)


async def get_device_status(request):
    """GET /api/devices/{device_id}/status - Return device status."""
    device_id = request.match_info['device_id']
    print(f"📥 Request: GET /api/devices/{device_id}/status")
    
    if device_id not in MOCK_DEVICES:
        print(f"📤 Response: 404 Not Found\n")
        return web.json_response(
            {"error": {"code": "NOT_FOUND", "message": "Device not found"}},
            status=404
        )
    
    response = {
        "connected": True,
        "last_update": datetime.now().isoformat() + "Z",
        "sensors": MOCK_SENSORS.get(device_id, {})
    }
    
    print(f"📤 Response: {json.dumps(response, indent=2)}\n")
    return web.json_response(response)


async def handle_index(request):
    """GET / - Return API info."""
    print(f"📥 Request: GET /")
    response = {
        "api": "Blueriot Blue Connect Mock Hub",
        "version": "1.0.0",
        "endpoints": [
            "GET /api/devices",
            "GET /api/devices/{device_id}",
            "GET /api/devices/{device_id}/status"
        ]
    }
    print(f"📤 Response: {json.dumps(response, indent=2)}\n")
    return web.json_response(response)


def create_app():
    """Create the aiohttp application."""
    app = web.Application()
    
    # Routes
    app.router.add_get('/', handle_index)
    app.router.add_get('/api/devices', get_devices)
    app.router.add_get('/api/devices/{device_id}', get_device)
    app.router.add_get('/api/devices/{device_id}/status', get_device_status)
    
    return app


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Mock Blueriot Blue Connect Hub")
    print("=" * 60)
    print("\n📍 Listening on http://0.0.0.0:8080")
    print("\n Available endpoints:")
    print("   GET http://localhost:8080/")
    print("   GET http://localhost:8080/api/devices")
    print("   GET http://localhost:8080/api/devices/device_001")
    print("   GET http://localhost:8080/api/devices/device_001/status")
    print("\n💡 Test the connection with:")
    print("   python test_connection.py localhost 8080")
    print("\n" + "=" * 60)
    print("Press Ctrl+C to stop the server\n")
    
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=8080)
