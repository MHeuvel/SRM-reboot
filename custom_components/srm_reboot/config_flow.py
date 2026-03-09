"""Config flow for SRM Reboot integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_IP, CONF_PORT, CONF_USERNAME, CONF_PASSWORD, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)


class SRMRebootConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SRM Reboot."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            ip = user_input[CONF_IP]
            port = user_input[CONF_PORT]
            unique_id = f"{ip}:{port}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            # Save the data as the config entry (password stored in config entry data)
            return self.async_create_entry(
                title=unique_id,
                data={
                    CONF_IP: ip,
                    CONF_PORT: port,
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                },
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_IP): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
