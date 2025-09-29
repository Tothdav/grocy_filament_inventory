import logging
import async_timeout
import aiohttp

_LOGGER = logging.getLogger(__name__)


class GrocyApi:
    def __init__(self, url: str, api_key: str):
        self._url = url.rstrip("/")
        self._api_key = api_key
        self._session = aiohttp.ClientSession()

    async def test_connection(self) -> bool:
        """Egyszerű teszt: lekéri a user/me endpointot."""
        try:
            headers = {"GROCY-API-KEY": self._api_key}
            async with self._session.get(f"{self._url}/api/user", headers=headers) as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Grocy API test failed: %s", resp.status)
                return False
        except Exception as e:
            _LOGGER.error("Grocy API exception: %s", e)
            return False

    async def find_filament_group(self) -> int | None:
        """Megkeresi a 'Filament' nevű product group ID-t."""
        headers = {"GROCY-API-KEY": self._api_key}
        async with self._session.get(f"{self._url}/api/objects/product_groups", headers=headers) as resp:
            if resp.status != 200:
                _LOGGER.error("Failed to fetch product groups, status: %s", resp.status)
                return None
            groups = await resp.json()
            for g in groups:
                if g["name"].lower() == "filament":
                    return g["id"]
        return None

    async def async_get_product_userfields(self, product_id):
        headers = {"GROCY-API-KEY": self._api_key}
        url = f"{self._url}/api/userfields/products/{product_id}"
        async with async_timeout.timeout(10):
            async with self._session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def async_get_products(self, product_group_id):
        """Lekéri az összes productot a Grocy-ból."""
        headers = {"GROCY-API-KEY": self._api_key}
        url = f"{self._url}/api/stock"
        async with async_timeout.timeout(10):
            async with self._session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def async_close(self):
        await self._session.close()