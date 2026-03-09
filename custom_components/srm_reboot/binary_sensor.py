from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, INGRESS_MISSED, INGRESS_MISSED_LIMIT, INGRESS_BLOCKED


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor for SRM Reboot."""
    entity = IngressBlockedBinarySensor(hass, entry)
    async_add_entities([entity])


class IngressBlockedBinarySensor(BinarySensorEntity):
    """Binary sensor that reflects ingress blocked state."""

    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self._hass = hass
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{INGRESS_BLOCKED}"
        self._attr_name = "Ingress blocked"
        self._attr_is_on = False
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "SRM Reboot",
        }

        # Verwachte entity_ids van de numbers
        self._ingress_missed_entity_id = f"number.{DOMAIN}_{INGRESS_MISSED}"
        self._ingress_limit_entity_id = f"number.{DOMAIN}_{INGRESS_MISSED_LIMIT}"

    async def async_added_to_hass(self) -> None:
        """Register listeners when entity is added."""

        @callback
        def _handle_state_change(event):
            self._recalculate_state()

        async_track_state_change_event(
            self._hass,
            [self._ingress_missed_entity_id, self._ingress_limit_entity_id],
            _handle_state_change,
        )

        # Initiale berekening
        self._recalculate_state()

    @callback
    def _recalculate_state(self) -> None:
        """Apply your exact logic."""
        missed_state = self._hass.states.get(self._ingress_missed_entity_id)
        limit_state = self._hass.states.get(self._ingress_limit_entity_id)

        try:
            missed = int(missed_state.state) if missed_state else 0
        except (ValueError, TypeError):
            missed = 0

        try:
            limit = int(limit_state.state) if limit_state else 0
        except (ValueError, TypeError):
            limit = 0

        current = bool(self._attr_is_on)

        if missed == 0:
            new_state = False
        elif limit > 0 and missed >= limit:
            new_state = True
        else:
            new_state = current

        if new_state != current:
            self._attr_is_on = new_state
            self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        return self._attr_is_on
