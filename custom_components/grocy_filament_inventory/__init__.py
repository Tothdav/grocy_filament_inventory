"""Grocy Filament Inventory integration."""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import CONF_API_KEY, CONF_URL, Platform
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, GROCY_GROUP_ID
from .api import GrocyApi
from .coordinator import GrocyCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the integration from a ConfigEntry (GUI)."""
    grocy_url = entry.data[CONF_URL]
    grocy_api_key = entry.data[CONF_API_KEY]
    grocy_group_id = entry.data[GROCY_GROUP_ID]

    _LOGGER.info("Starting Grocy api with: %s and %s", grocy_url, grocy_api_key)
    client = GrocyApi(grocy_url, grocy_api_key)

    coordinator = GrocyCoordinator(hass, client, grocy_group_id)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": client,
        CONF_URL: grocy_url,
        CONF_API_KEY: grocy_api_key,
        GROCY_GROUP_ID: grocy_group_id
    }

    async def handle_consume_filament(call: ServiceCall):
        _LOGGER.info("Consuming filament service called with: %s", call.data)

        entity = call.data["entity"]

        sensor_state = hass.states.get(entity)
        _LOGGER.debug(sensor_state.attributes)
        product_id = sensor_state.attributes.get("product_id")

        amount = float(call.data.get("amount"))
        await client.async_consume_product(product_id=product_id, amount=amount)
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        "consume_filament",
        handle_consume_filament,
        schema=vol.Schema({
            vol.Required("entity"): cv.entity_id,
            vol.Required("amount", default=1): vol.Coerce(float)
        })
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok