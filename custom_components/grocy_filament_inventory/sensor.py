"""Sensor platform for Grocy Filament Inventory."""

import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors for all filaments."""
    coordinator = hass.data[DOMAIN][entry.entry_id]['coordinator']

    sensors = []
    for filament in coordinator.data:
        sensors.append(
            GrocyFilamentSensor(
                coordinator,
                filament["product_id"],
                filament["product"]["name"],
                filament.get('userfields', {}).get('filament_color', '#FFFFFF') 
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
        filament = next((f for f in self.coordinator.data if f["product_id"] == self._filament_id), None)
        if filament:
            color = filament.get('userfields', {}).get('filament_color', '#FFFFFF')
            if color is None:
                return {"color": "#FFFFFF"}
            else:
                return {"color": color}
        return {"color": "#FFFFFF"}

        # return {
        #     "color": self._color if self._color is not None else '#FFFFFF',
        # }

    @property
    def native_value(self):
        """Return the current aggregated amount of filament in grams."""
        filament = next(
            (f for f in self.coordinator.data if f["product_id"] == self._filament_id),
            None,
        )
        if filament:
            return float(filament.get("amount_aggregated"))
        return None