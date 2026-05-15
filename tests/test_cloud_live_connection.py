"""Optional live connectivity test for Blue Connect cloud.

Set environment variables to enable:
- BLUERIIOT_USERNAME
- BLUERIIOT_PASSWORD
- BLUERIIOT_LANGUAGE (optional, default: en)
"""

from __future__ import annotations

import os
import unittest


@unittest.skipUnless(
    os.getenv("BLUERIIOT_USERNAME") and os.getenv("BLUERIIOT_PASSWORD"),
    "Set BLUERIIOT_USERNAME and BLUERIIOT_PASSWORD to run live test",
)
class TestCloudLiveConnection(unittest.IsolatedAsyncioTestCase):
    """Live test against Blue Connect cloud."""

    async def test_live_credentials_and_fetch(self) -> None:
        from custom_components.blueriot_blue_connect.api import BlueriotBlueConnectCloudAPI

        username = os.environ["BLUERIIOT_USERNAME"]
        password = os.environ["BLUERIIOT_PASSWORD"]
        language = os.getenv("BLUERIIOT_LANGUAGE", "en")

        valid = await BlueriotBlueConnectCloudAPI.async_validate_credentials(
            username, password
        )
        self.assertTrue(valid, "Cloud credential validation failed")

        api = BlueriotBlueConnectCloudAPI(username, password, language)
        try:
            payload = await api.async_fetch_data()
        finally:
            await api.async_close()

        self.assertIn("pool", payload)
        self.assertIn("measurements", payload)
        self.assertIsInstance(payload["measurements"], list)
