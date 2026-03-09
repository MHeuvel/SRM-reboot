"""SRM Reboot integration."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, Optional

from aiohttp import ClientError
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry

from .const import (
    DOMAIN,
    CONF_IP,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    SERVICE_REBOOT,
    ATTR_ENTRY_ID,
    INGRESS_MISSED,
    SERVICE_INCREASE_INGRESS_MISSED,
    SERVICE_RESET_INGRESS_MISSED,
)

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
    }
)

PLATFORMS = ["number", "binary_sensor"]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the SRM Reboot integration (legacy entry point)."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    """Set up a config entry for SRM Reboot."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    async def _parse_json_response(resp):
        """Robust JSON-parser: try resp.json, fallback to json.loads(text)."""
        text = await resp.text()
        try:
            # negeer content-type header als die onjuist is
            return await resp.json(content_type=None)
        except Exception:
            try:
                return json.loads(text)
            except Exception as err:
                raise HomeAssistantError(
                    f"Unable to parse as JSON. HTTP {resp.status}. Response: {text}"
                ) from err

    async def handle_reboot(call: ServiceCall) -> None:
        """Handle the reboot service call."""
        entry_id: Optional[str] = call.data.get(ATTR_ENTRY_ID)
        if entry_id:
            cfg = hass.data[DOMAIN].get(entry_id)
            if not cfg:
                raise HomeAssistantError(f"Config entry {entry_id} not found.")
        else:
            if len(hass.data[DOMAIN]) == 1:
                cfg = next(iter(hass.data[DOMAIN].values()))
            elif len(hass.data[DOMAIN]) == 0:
                raise HomeAssistantError("No SRM Reboot config entries configured.")
            else:
                raise HomeAssistantError(
                    "Multiple config entries present. Provide 'entry_id' in service call."
                )

        ip = cfg[CONF_IP]
        port = cfg[CONF_PORT]
        username = cfg[CONF_USERNAME]
        password = cfg[CONF_PASSWORD]

        session = async_get_clientsession(hass)

        auth_url = f"https://{ip}:{port}/webapi/auth.cgi"
        auth_params = {
            "api": "SYNO.API.Auth",
            "version": "2",
            "method": "login",
            "account": username,
            "passwd": password,
            "session": "RouterControl",
            "format": "sid",
        }

        try:
            async with session.get(auth_url, params=auth_params, ssl=False) as resp:
                auth_json = await _parse_json_response(resp)
        except ClientError as err:
            raise HomeAssistantError(f"Auth request failed: {err}") from err

        # Log de volledige auth response voor debugging (niet in productie logs als gevoelige info)
        _LOGGER.debug("Auth response: %s", auth_json)

        success = auth_json.get("success", False)
        if not success:
            # toon JSON output als tekst in de foutmelding
            raise HomeAssistantError(f"Auth failed. Response: {json.dumps(auth_json)}")

        try:
            sid = auth_json["data"]["sid"]
        except Exception:
            raise HomeAssistantError(
                f"Auth response missing sid. Response: {json.dumps(auth_json)}"
            )

        reboot_url = f"https://{ip}:{port}/webapi/entry.cgi"
        reboot_params = {
            "api": "SYNO.Core.System",
            "version": "1",
            "method": "reboot",
            "_sid": sid,
        }

        try:
            async with session.get(reboot_url, params=reboot_params, ssl=False) as resp2:
                reboot_json = await _parse_json_response(resp2)
        except ClientError as err:
            raise HomeAssistantError(f"Reboot request failed: {err}") from err

        _LOGGER.debug("Reboot response: %s", reboot_json)

        if not reboot_json.get("success", False):
            raise HomeAssistantError(f"Reboot failed. Response: {json.dumps(reboot_json)}")

        hass.bus.async_fire(f"{DOMAIN}_reboot_success", {"entry_id": entry.entry_id})

    hass.services.async_register(DOMAIN, SERVICE_REBOOT, handle_reboot, schema=SERVICE_SCHEMA)

    async def handle_increase_ingress_missed(call: ServiceCall) -> None:
        """Increase ingress_missed by 1."""
        entity_id = f"number.{DOMAIN}_{INGRESS_MISSED}"

        state = hass.states.get(entity_id)
        if state is None:
            raise HomeAssistantError("Ingress missed entity not found.")

        try:
            current = int(state.state)
        except (ValueError, TypeError):
            current = 0

        new_value = current + 1

        await hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": entity_id, "value": new_value},
            blocking=True,
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_INCREASE_INGRESS_MISSED,
        handle_increase_ingress_missed,
    )

    async def handle_reset_ingress_missed(call: ServiceCall) -> None:
        """Reset ingress_missed to 0."""
        entity_id = f"number.{DOMAIN}_{INGRESS_MISSED}"

        await hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": entity_id, "value": 0},
            blocking=True,
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_RESET_INGRESS_MISSED,
        handle_reset_ingress_missed,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    """Unload a config entry."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if not hass.data.get(DOMAIN):
        hass.services.async_remove(DOMAIN, SERVICE_REBOOT)
    return True
