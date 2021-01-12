from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch

from homeassistant.components.lock import STATE_LOCKED, STATE_UNLOCKED
from homeassistant.const import STATE_UNAVAILABLE

from custom_components.tuya_local.geco_heater.const import (
    ATTR_CHILD_LOCK,
    ATTR_HVAC_MODE,
    PROPERTY_TO_DPS_ID,
)
from custom_components.tuya_local.geco_heater.lock import GoldairGECOHeaterChildLock

from ..const import GECO_HEATER_PAYLOAD
from ..helpers import assert_device_properties_set


class TestGoldairGECOHeaterChildLock(IsolatedAsyncioTestCase):
    def setUp(self):
        device_patcher = patch("custom_components.tuya_local.device.TuyaLocalDevice")
        self.addCleanup(device_patcher.stop)
        self.mock_device = device_patcher.start()

        self.subject = GoldairGECOHeaterChildLock(self.mock_device())

        self.dps = GECO_HEATER_PAYLOAD.copy()
        self.subject._device.get_property.side_effect = lambda id: self.dps[id]

    def test_should_poll(self):
        self.assertTrue(self.subject.should_poll)

    def test_name_returns_device_name(self):
        self.assertEqual(self.subject.name, self.subject._device.name)

    def test_unique_id_returns_device_unique_id(self):
        self.assertEqual(self.subject.unique_id, self.subject._device.unique_id)

    def test_device_info_returns_device_info_from_device(self):
        self.assertEqual(self.subject.device_info, self.subject._device.device_info)

    def test_state(self):
        self.dps[PROPERTY_TO_DPS_ID[ATTR_CHILD_LOCK]] = True
        self.assertEqual(self.subject.state, STATE_LOCKED)

        self.dps[PROPERTY_TO_DPS_ID[ATTR_CHILD_LOCK]] = False
        self.assertEqual(self.subject.state, STATE_UNLOCKED)

        self.dps[PROPERTY_TO_DPS_ID[ATTR_CHILD_LOCK]] = None
        self.assertEqual(self.subject.state, STATE_UNAVAILABLE)

    def test_is_locked(self):
        self.dps[PROPERTY_TO_DPS_ID[ATTR_CHILD_LOCK]] = True
        self.assertEqual(self.subject.is_locked, True)

        self.dps[PROPERTY_TO_DPS_ID[ATTR_CHILD_LOCK]] = False
        self.assertEqual(self.subject.is_locked, False)

    async def test_lock(self):
        async with assert_device_properties_set(
            self.subject._device, {PROPERTY_TO_DPS_ID[ATTR_CHILD_LOCK]: True}
        ):
            await self.subject.async_lock()

    async def test_unlock(self):
        async with assert_device_properties_set(
            self.subject._device, {PROPERTY_TO_DPS_ID[ATTR_CHILD_LOCK]: False}
        ):
            await self.subject.async_unlock()

    async def test_update(self):
        result = AsyncMock()
        self.subject._device.async_refresh.return_value = result()

        await self.subject.async_update()

        self.subject._device.async_refresh.assert_called_once()
        result.assert_awaited()
