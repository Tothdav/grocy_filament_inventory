"""Sensor platform for Grocy Filament Inventory."""

import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, DEFAULT_COLOR, FIELD_PRODUCT_ID, FIELD_PRODUCT_KEY, FIELD_PRODUCT_NAME, FIELD_PRODUCT_USERFIELDS, FIELD_FILAMENT_COLOR, FIELD_PRODUCT_AMOUNT_AGGREGATED, FIELD_COLOR

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors for all filaments."""
    coordinator = hass.data[DOMAIN][entry.entry_id]['coordinator']
    _LOGGER.debug("Starting to create sensors")

    sensors = []
    for filament in coordinator.data:
        sensors.append(
            GrocyFilamentSensor(
                coordinator,
                filament[FIELD_PRODUCT_ID],
                filament[FIELD_PRODUCT_KEY][FIELD_PRODUCT_NAME],
                filament.get(FIELD_PRODUCT_USERFIELDS, {}).get(FIELD_FILAMENT_COLOR, DEFAULT_COLOR) 
            )
        )

    async_add_entities(sensors)


class GrocyFilamentSensor(CoordinatorEntity, SensorEntity):
    """Representation of a filament as a sensor."""

    def __init__(self, coordinator, filament_id, filament_name, color):
        super().__init__(coordinator)
        self._filament_id = filament_id
        self._attr_name = f"Filament {filament_name}"
        self._attr_unique_id = f"grocy_filament_{filament_id}"
        self._attr_native_unit_of_measurement = "g"
        self._attr_icon = "mdi:chart-donut"
        self._color = color

    @property
    def extra_state_attributes(self):
        filament = next((f for f in self.coordinator.data if f[FIELD_PRODUCT_ID] == self._filament_id), None)
        if filament:
            product_id = filament.get(FIELD_PRODUCT_ID, -1)
            color = filament.get(FIELD_PRODUCT_USERFIELDS, {}).get(FIELD_FILAMENT_COLOR, DEFAULT_COLOR)
            if color is None:
                return {FIELD_COLOR: DEFAULT_COLOR, "product_id": product_id}
            else:
                return {FIELD_COLOR: color, "product_id": product_id}
        return {FIELD_COLOR: DEFAULT_COLOR, "product_id": "-1"}

    @property
    def native_value(self):
        """Return the current aggregated amount of filament in grams."""
        filament = next(
            (f for f in self.coordinator.data if f[FIELD_PRODUCT_ID] == self._filament_id),
            None,
        )
        if filament:
            return float(filament.get(FIELD_PRODUCT_AMOUNT_AGGREGATED))
        return None