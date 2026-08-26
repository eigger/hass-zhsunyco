"""The Zhsunyco Bluetooth integration coordinator."""

from __future__ import annotations

from collections.abc import Callable
from logging import Logger
from typing import TYPE_CHECKING, TypeVar

from bluetooth_sensor_state_data import BluetoothData
from homeassistant.components.bluetooth import (
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
)
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
    PassiveBluetoothProcessorCoordinator,
)
from homeassistant.core import HomeAssistant
from sensor_state_data import SensorUpdate

if TYPE_CHECKING:
    from .types import ZhsunycoConfigEntry

_T = TypeVar("_T")


class ZhsunycoPassiveBluetoothProcessorCoordinator(
    PassiveBluetoothProcessorCoordinator[SensorUpdate]
):
    """Define a Zhsunyco Bluetooth Passive Update Processor Coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: Logger,
        address: str,
        mode: BluetoothScanningMode,
        update_method: Callable[[BluetoothServiceInfoBleak], SensorUpdate],
        device_data: BluetoothData,
        entry: ZhsunycoConfigEntry,
        connectable: bool = False,
    ) -> None:
        """Initialize the Zhsunyco Bluetooth Passive Update Processor Coordinator."""
        super().__init__(
            hass, logger, address, mode, update_method, connectable
        )
        self.device_data = device_data
        self.entry = entry


class ZhsunycoPassiveBluetoothDataProcessor(
    PassiveBluetoothDataProcessor[_T, SensorUpdate]
):
    """Define a Zhsunyco Bluetooth Passive Update Data Processor."""

    coordinator: ZhsunycoPassiveBluetoothProcessorCoordinator
