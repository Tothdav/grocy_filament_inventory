import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_URL

from .const import DOMAIN, GROCY_GROUP_ID
from .api import GrocyApi

_LOGGER = logging.getLogger(__name__)


class GrocyFilamentInventoryFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Grocy Filament Inventory."""

    VERSION = 1

    def __init__(self):
        self.grocy_url = None
        self.grocy_api_key = None
        self.grocy_group_id = None

    async def async_step_user(self, user_input=None):
        """Step when user adds integration via GUI."""
        errors = {}

        if user_input is not None:
            self.grocy_url = user_input[CONF_URL]
            self.grocy_api_key = user_input[CONF_API_KEY]

            # Megpróbáljuk a kapcsolatot (API teszt)
            api = GrocyApi(self.grocy_url, self.grocy_api_key)
            ok = await api.test_connection()

            if not ok:
                errors["base"] = "cannot_connect"
            else:
                return await self.async_step_find_group()

        schema = vol.Schema({
            vol.Required(CONF_URL, default=self.grocy_url or ""): str,
            vol.Required(CONF_API_KEY, default=self.grocy_api_key or ""): str,
        })

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    async def async_step_find_group(self, user_input=None):
        """Second step: Trying to fetch Filament product group."""
        errors = {}

        api = GrocyApi(self.grocy_url, self.grocy_api_key)
        grocy_group_id = await api.find_filament_group()

        if grocy_group_id is None:
            errors["base"] = "no_filament_group"
            return self.async_show_form(
                step_id="find_group",
                data_schema=vol.Schema({}),  # Retry button
                errors=errors
            )

        self.grocy_group_id = grocy_group_id

        # Ha minden megvan → create entry
        return self.async_create_entry(
            title="Grocy Filament Inventory",
            data={
                CONF_URL: self.grocy_url,
                CONF_API_KEY: self.grocy_api_key,
                GROCY_GROUP_ID: self.grocy_group_id,
            },
        )
