"""Parser for PickSmart (gicisky) BLE advertisements."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from sensor_state_data import SensorLibrary

from ..base import DevicePreset, ProtocolParser
from .const import MANUFACTURER_ID, SERVICE_UUIDS
from .devices import get_device_preset

if TYPE_CHECKING:
    from home_assistant_bluetooth import BluetoothServiceInfoBleak

_LOGGER = logging.getLogger(__name__)


def is_picksmart_advertisement(data: BluetoothServiceInfoBleak) -> bool:
    """Return True if advertisement matches PickSmart manufacturer data or service UUIDs."""
    if MANUFACTURER_ID in data.manufacturer_data:
        return True
    for uuid in data.service_uuids:
        if isinstance(uuid, str) and uuid.lower() in SERVICE_UUIDS:
            return True
    return False


def parse_manufacturer_data(data: bytes) -> dict | None:
    """Parse 5-byte 0x5053 manufacturer advertisement payload."""
    if len(data) != 5:
        return None
    device_id = ((data[4] << 8) | data[0]) & 0x3FFF
    battery_dv = data[1]
    firmware = (data[2] << 8) + data[3]
    hardware = (data[4] << 8) | data[0]
    return {
        "device_id": device_id,
        "model_key": f"0x{device_id:04X}",
        "battery_v": battery_dv / 10.0,
        "battery_mv": battery_dv * 100,
        "firmware": firmware,
        "hardware": hardware,
    }


class PickSmartBluetoothDeviceData(ProtocolParser):
    """Data parser for PickSmart Bluetooth ESL devices."""

    def __init__(self, preset: DevicePreset | None = None) -> None:
        super().__init__()
        self.preset = preset
        self.last_service_info: BluetoothServiceInfoBleak | None = None

    def set_preset(self, preset: DevicePreset) -> None:
        """Update active device preset."""
        self.preset = preset
        if self.last_service_info is not None:
            self._update_device_info(self.last_service_info)

    def supported(self, data: BluetoothServiceInfoBleak) -> bool:
        """Return True if this advertisement is from a PickSmart device."""
        return is_picksmart_advertisement(data)

    def _update_device_info(self, service_info: BluetoothServiceInfoBleak) -> None:
        identifier = service_info.address.replace(":", "")[-8:]
        display_name = self.preset.display_name if self.preset else "PickSmart"
        res = (
            f" {self.preset.width}x{self.preset.height}"
            if self.preset and f"{self.preset.width}x{self.preset.height}" not in display_name
            else ""
        )
        self.set_title(f"{identifier} ({display_name})")
        self.set_device_name(f"Zhsunyco {identifier}")
        self.set_device_type(f"{display_name}{res}")
        self.set_device_manufacturer("Zhsunyco (PickSmart)")

    def _start_update(self, service_info: BluetoothServiceInfoBleak) -> None:
        """Update from BLE advertisement data."""
        if not is_picksmart_advertisement(service_info):
            return
        self.last_service_info = service_info
        self._update_device_info(service_info)

        mfr_bytes = service_info.manufacturer_data.get(MANUFACTURER_ID)
        if not mfr_bytes:
            return

        parsed = parse_manufacturer_data(mfr_bytes)
        if not parsed:
            return

        device_id = parsed["device_id"]
        firmware = parsed["firmware"]
        preset = get_device_preset(device_id, firmware)
        if preset:
            self.preset = preset
            self._update_device_info(service_info)

        self.set_device_sw_version(f"0x{firmware:04X}")
        self.set_device_hw_version(f"0x{parsed['hardware']:04X}")

        volt = parsed["battery_v"]
        min_volt = (self.preset.extra.get("min_voltage", 2.2)) if self.preset else 2.2
        max_volt = (self.preset.extra.get("max_voltage", 3.0)) if self.preset else 3.0

        batt = (volt - min_volt) * 100.0 / (max_volt - min_volt)
        batt = max(0.0, min(100.0, batt))

        self.update_predefined_sensor(
            SensorLibrary.BATTERY__PERCENTAGE, round(batt, 1)
        )
        self.update_predefined_sensor(
            SensorLibrary.VOLTAGE__ELECTRIC_POTENTIAL_VOLT, round(volt, 1)
        )
