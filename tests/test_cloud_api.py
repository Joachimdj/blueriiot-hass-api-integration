"""Unit tests for cloud API wrapper.

These tests mock the upstream ``blueconnect`` package so they can run locally
without network access or real credentials.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import importlib.util
import sys
import types
import unittest
from unittest.mock import AsyncMock


class _FakeBlueConnectApi:
    """Fake cloud auth API."""

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.get_user_info = AsyncMock(return_value={"id": "user"})
        self.close_async = AsyncMock()


class _FakeBlueConnectSimpleAPI:
    """Fake cloud data API."""

    def __init__(self, username: str, password: str, language: str) -> None:
        self.username = username
        self.password = password
        self.language = language
        self.fetch_data = AsyncMock()
        self.close_async = AsyncMock()
        self.pool = types.SimpleNamespace(swimming_pool_id=1234, name="Main Pool")
        self.blue_device = types.SimpleNamespace(serial="ABC123", battery_low=False)
        self.measurements = [
            types.SimpleNamespace(
                name="ph",
                value=7.2,
                timestamp=datetime(2026, 5, 15, 12, 0, 0),
                trend=types.SimpleNamespace(value="stable"),
                ok_min=7.0,
                ok_max=7.6,
                warning_low=6.8,
                warning_high=7.8,
                issuer="sensor",
            )
        ]


def _load_api_module():
    """Load api module with mocked ``blueconnect`` dependency."""
    fake_mod = types.ModuleType("blueconnect")
    fake_mod.BlueConnectApi = _FakeBlueConnectApi
    fake_mod.BlueConnectSimpleAPI = _FakeBlueConnectSimpleAPI
    sys.modules["blueconnect"] = fake_mod

    module_path = (
        Path(__file__).resolve().parents[1]
        / "custom_components"
        / "blueriot_blue_connect"
        / "api.py"
    )
    spec = importlib.util.spec_from_file_location("blueriot_api_under_test", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load API module spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestCloudApi(unittest.IsolatedAsyncioTestCase):
    """Tests for Blueriot cloud wrapper behavior."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.api_module = _load_api_module()

    def setUp(self) -> None:
        self.api_module.BlueConnectApi = _FakeBlueConnectApi
        self.api_module.BlueConnectSimpleAPI = _FakeBlueConnectSimpleAPI

    async def test_validate_credentials_success(self):
        """Credential validation returns true on valid user info."""
        result = await self.api_module.BlueriotBlueConnectCloudAPI.async_validate_credentials(
            "user@example.com", "secret"
        )
        self.assertTrue(result)

    async def test_validate_credentials_failure(self):
        """Credential validation returns false on API error."""

        class _FailingApi(_FakeBlueConnectApi):
            def __init__(self, username: str, password: str) -> None:
                super().__init__(username, password)
                self.get_user_info = AsyncMock(side_effect=RuntimeError("bad creds"))

        self.api_module.BlueConnectApi = _FailingApi
        result = await self.api_module.BlueriotBlueConnectCloudAPI.async_validate_credentials(
            "user@example.com", "wrong"
        )
        self.assertFalse(result)

    async def test_fetch_data_normalizes_measurements(self):
        """Fetched cloud data is normalized to integration payload format."""
        api = self.api_module.BlueriotBlueConnectCloudAPI("user", "secret", "en")
        payload = await api.async_fetch_data()

        self.assertEqual(payload["pool"]["id"], "1234")
        self.assertEqual(payload["pool"]["name"], "Main Pool")
        self.assertEqual(payload["device_serial"], "ABC123")
        self.assertFalse(payload["battery_low"])

        self.assertEqual(len(payload["measurements"]), 1)
        measurement = payload["measurements"][0]
        self.assertEqual(measurement["name"], "ph")
        self.assertEqual(measurement["value"], 7.2)
        self.assertEqual(measurement["trend"], "stable")
        self.assertEqual(measurement["ok_min"], 7.0)
        self.assertEqual(measurement["ok_max"], 7.6)
        self.assertEqual(measurement["warning_low"], 6.8)
        self.assertEqual(measurement["warning_high"], 7.8)
        self.assertEqual(measurement["issuer"], "sensor")

    async def test_fetch_data_wraps_errors(self):
        """Cloud fetch exceptions are wrapped in integration-specific error."""

        class _FailingSimpleAPI(_FakeBlueConnectSimpleAPI):
            def __init__(self, username: str, password: str, language: str) -> None:
                super().__init__(username, password, language)
                self.fetch_data = AsyncMock(side_effect=RuntimeError("network down"))

        self.api_module.BlueConnectSimpleAPI = _FailingSimpleAPI

        api = self.api_module.BlueriotBlueConnectCloudAPI("user", "secret", "en")
        with self.assertRaises(self.api_module.BlueriotBlueConnectAPIError):
            await api.async_fetch_data()


if __name__ == "__main__":
    unittest.main(verbosity=2)
