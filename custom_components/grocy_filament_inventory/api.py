import logging
import async_timeout
import aiohttp

_LOGGER = logging.getLogger(__name__)

class GrocyApi:

    GROCY_API_KEY_STRING = "GROCY-API-KEY"
    GROCY_API_URL_SUFFIX = "api"

    def __init__(self, url: str, api_key: str):
        self._url = url.rstrip("/")
        self._api_key = api_key
        self._session = aiohttp.ClientSession()

    async def test_connection(self) -> bool:
        """It is a basic connection check by fetching user/me endpoint."""
        try:
            headers = {self.GROCY_API_KEY_STRING: self._api_key}
            async with self._session.get(f"{self._url}/api/user", headers=headers) as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Grocy API test failed: %s", resp.status)
                return False
        except Exception as e:
            _LOGGER.error("Grocy API exception: %s", e)
            return False

    async def find_filament_group(self) -> int | None:
        """It finds the product group id of the 'Filament' product type"""
        headers = {self.GROCY_API_KEY_STRING: self._api_key}
        async with self._session.get(f"{self._url}/{self.GROCY_API_URL_SUFFIX}/objects/product_groups", headers=headers) as resp:
            if resp.status != 200:
                _LOGGER.error("Failed to fetch product groups, status: %s", resp.status)
                return None
            groups = await resp.json()
            for group in groups:
                if group["name"].lower() == "filament":
                    return group["id"]
        return None

    async def async_get_product_userfields(self, product_id):
        headers = {self.GROCY_API_KEY_STRING: self._api_key}
        url = f"{self._url}/{self.GROCY_API_URL_SUFFIX}/userfields/products/{product_id}"
        async with async_timeout.timeout(10):
            async with self._session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def async_get_products(self, product_group_id):
        """Fetches all the products with the given product group id"""
        headers = {self.GROCY_API_KEY_STRING: self._api_key}
        url = f"{self._url}/api/stock"
        async with async_timeout.timeout(10):
            async with self._session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def async_close(self):
        await self._session.close()