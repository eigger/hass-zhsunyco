"""The Zhsunyco Bluetooth integration."""

from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry

if TYPE_CHECKING:
    from .coordinator import ZhsunycoPassiveBluetoothProcessorCoordinator

type ZhsunycoConfigEntry = ConfigEntry[ZhsunycoPassiveBluetoothProcessorCoordinator]
