"""Grocy Filament Inventory integration."""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_API_KEY, CONF_URL

from .const import DOMAIN, GROCY_GROUP_ID
from .api import GrocyApi
from .coordinator import GrocyCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the integration from a ConfigEntry (GUI)."""
    grocy_url = entry.data[CONF_URL]
    grocy_api_key = entry.data[CONF_API_KEY]
    grocy_group_id = entry.data[GROCY_GROUP_ID]

    _LOGGER.info("Starting Grocy api with: %s and %s", grocy_url, grocy_api_key)
    client = GrocyApi(grocy_url, grocy_api_key)

    coordinator = GrocyCoordinator(hass, client, grocy_group_id, _LOGGER)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": client,
        CONF_URL: grocy_url,
        CONF_API_KEY: grocy_api_key,
        GROCY_GROUP_ID: grocy_group_id
    }

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True
