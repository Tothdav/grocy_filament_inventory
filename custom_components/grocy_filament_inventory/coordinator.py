from datetime import timedelta
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .api import GrocyApi

from .const import FIELD_PRODUCT_KEY, FIELD_PRODUCT_GROUP_ID, FIELD_PRODUCT_ID, FIELD_PRODUCT_USERFIELDS

_LOGGER = logging.getLogger(__name__)

class GrocyCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, client: GrocyApi, group_id, logger):
        super().__init__(
            hass,
            logger,
            name="grocy_filament_inventory",
            update_interval=timedelta(seconds=60),
        )
        self.client = client
        self.group_id = group_id

    async def _async_update_data(self):
        """Fetch data from Grocy API."""
        try:
            products_in_stock = await self.client.async_get_products(self.group_id)

            filaments = []
            for product_in_stock in products_in_stock:
                if product_in_stock[FIELD_PRODUCT_KEY][FIELD_PRODUCT_GROUP_ID] == self.group_id and product_in_stock[FIELD_PRODUCT_KEY][FIELD_PRODUCT_GROUP_ID] is None:
                    userfields = await self.client.async_get_product_userfields(product_in_stock[FIELD_PRODUCT_ID])
                    product_in_stock[FIELD_PRODUCT_USERFIELDS] = userfields
                    filaments.append(product_in_stock)
            return filaments
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")
