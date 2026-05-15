"""Test script to verify hub connectivity."""

import asyncio
import sys
import os

# Add custom_components to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'blueriot_blue_connect'))

from api import BlueriotBlueConnectAPI, BlueriotBlueConnectAPIError


async def test_hub_connection(host: str, port: int, api_key: str | None = None) -> bool:
    """Test connection to the Blueriot Blue Connect hub."""
    
    print(f"\n🔍 Testing connection to hub at {host}:{port}...")
    
    api = BlueriotBlueConnectAPI(host, port, api_key)
    
    try:
        # Test API connection
        print(f"  📡 Fetching devices from {api.base_url}/devices...")
        devices = await api.async_get_devices()
        
        if not devices:
            print("  ⚠️  No devices found on hub")
            await api.async_close()
            return False
        
        device_list = devices.get("devices", [])
        
        if not device_list:
            print("  ⚠️  Hub returned empty device list")
            await api.async_close()
            return False
        
        # Display devices found
        print(f"\n✅ Successfully connected to hub!")
        print(f"   Found {len(device_list)} device(s):\n")
        
        for device in device_list:
            device_id = device.get("id", "Unknown")
            device_name = device.get("name", "Unknown")
            device_type = device.get("type", "Unknown")
            
            print(f"   📦 Device: {device_name}")
            print(f"      ID: {device_id}")
            print(f"      Type: {device_type}")
            
            # Check for sensor data
            status = device.get("status", {})
            sensors = status.get("sensors", {})
            
            if sensors:
                print(f"      Sensors: {len(sensors)} found")
                for sensor_key, sensor_value in sensors.items():
                    print(f"        • {sensor_key}: {sensor_value}")
            else:
                print(f"      ⚠️  No sensor data available")
            print()
        
        await api.async_close()
        return True
        
    except BlueriotBlueConnectAPIError as err:
        print(f"\n❌ API Error: {err}")
        await api.async_close()
        return False
    except Exception as err:
        print(f"\n❌ Unexpected error: {err}")
        await api.async_close()
        return False


async def main():
    """Main test function."""
    
    print("=" * 60)
    print("Blueriot Blue Connect - Hub Connection Test")
    print("=" * 60)
    
    # Get connection details from user or use defaults
    if len(sys.argv) > 1:
        host = sys.argv[1]
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
        api_key = sys.argv[3] if len(sys.argv) > 3 else None
    else:
        # Default values for testing
        host = input("Enter hub IP address (default: localhost): ").strip() or "localhost"
        port_str = input("Enter hub port (default: 8080): ").strip() or "8080"
        port = int(port_str)
        api_key = input("Enter API key (optional, press Enter to skip): ").strip() or None
    
    # Run the connection test
    success = await test_hub_connection(host, port, api_key)
    
    print("=" * 60)
    if success:
        print("✅ Connection test PASSED - Hub is accessible!")
    else:
        print("❌ Connection test FAILED - Unable to reach hub")
        print("\nTroubleshooting steps:")
        print("  1. Verify hub IP address is correct")
        print("  2. Verify hub port is correct (default: 8080)")
        print("  3. Ensure hub is powered on and connected to network")
        print("  4. Check firewall allows connection to hub port")
        print("  5. Verify API key if required by hub")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
