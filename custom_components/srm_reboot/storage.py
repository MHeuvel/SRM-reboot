import json
from homeassistant.helpers import storage

from .const import DOMAIN

STORE_VERSION = 1
STORE_KEY = f"{DOMAIN}_config"

async def async_save_config(hass, config):
    """Save the config dict to Home Assistant storage."""
    store = storage.Store(hass, STORE_VERSION, STORE_KEY)
    await store.async_save(config)

async def async_load_config(hass):
    """Load the config dict from storage (or return None)."""
    store = storage.Store(hass, STORE_VERSION, STORE_KEY)
    data = await store.async_load()
    return data
