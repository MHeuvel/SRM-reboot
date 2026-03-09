from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, INGRESS_MISSED, INGRESS_MISSED_LIMIT


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities for SRM Reboot."""
    async_add_entities(
        [
            IngressMissedNumber(hass, entry),
            IngressMissedLimitNumber(hass, entry),
        ]
    )


class BaseSrmNumber(NumberEntity):
    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self._hass = hass
        self._entry = entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "SRM Reboot",
        }


class IngressMissedNumber(BaseSrmNumber):
    """User-controlled counter: ingress_missed."""

    _attr_native_min_value = 0
    _attr_native_step = 1
    _attr_mode = "box"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, entry)
        self._attr_unique_id = f"{entry.entry_id}_{INGRESS_MISSED}"
        self._attr_name = "Ingress missed"
        self._value = 0  # integratie verandert dit nooit

    @property
    def native_value(self) -> float | None:
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        # Alleen de gebruiker (of onze service via number.set_value) wijzigt dit.
        self._value = int(value)
        self.async_write_ha_state()


class IngressMissedLimitNumber(BaseSrmNumber):
    """User-configurable limit: ingress_missed_limit."""

    _attr_native_min_value = 1
    _attr_native_step = 1
    _attr_mode = "box"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, entry)
        self._attr_unique_id = f"{entry.entry_id}_{INGRESS_MISSED_LIMIT}"
        self._attr_name = "Ingress missed limit"
        self._value = entry.options.get(INGRESS_MISSED_LIMIT, 5)

    @property
    def native_value(self) -> float | None:
        return self._value


    async def async_set_native_value(self, value: float) -> None:
        self._value = int(value)
        self.async_write_ha_state()

        # Persist the value in config entry options
        new_options = {**self._entry.options, INGRESS_MISSED_LIMIT: self._value}
        self._hass.config_entries.async_update_entry(self._entry, options=new_options)
