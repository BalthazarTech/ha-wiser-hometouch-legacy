"""Entités select pour Wiser HomeTouch Legacy."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HomeTouchCoordinator

BASIC_API_TO_FR = {
    "Home": "Maison",
    "Away": "Absent",
    "Sleep": "Nuit",
}
BASIC_FR_TO_API = {label: value for value, label in BASIC_API_TO_FR.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configurer les entités select du HomeTouch."""
    coordinator: HomeTouchCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            HomeTouchBasicSelect(coordinator, entry),
            HomeTouchUserSelect(coordinator, entry),
        ]
    )


class HomeTouchSelectBase(CoordinatorEntity[HomeTouchCoordinator], SelectEntity):
    """Classe de base des sélecteurs HomeTouch."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HomeTouchCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Wiser HomeTouch",
            manufacturer="Schneider Electric",
            model="CCT501510",
        )


class HomeTouchBasicSelect(HomeTouchSelectBase):
    """Sélecteur des Basic Moments."""

    _attr_name = "Mode chauffage"
    _attr_icon = "mdi:home-thermometer"

    def __init__(self, coordinator: HomeTouchCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_basic_moment"

    @property
    def options(self) -> list[str]:
        raw_options = self.coordinator.data.get("basic", {}).get("sceneValues", [])
        return [BASIC_API_TO_FR.get(value, value) for value in raw_options]

    @property
    def current_option(self) -> str | None:
        raw_value = self.coordinator.data.get("basic", {}).get("lastScene")
        if not raw_value:
            return None
        return BASIC_API_TO_FR.get(raw_value, raw_value)

    async def async_select_option(self, option: str) -> None:
        if option not in self.options:
            raise ValueError(f"Mode de base non pris en charge : {option}")

        api_value = BASIC_FR_TO_API.get(option, option)
        await self.coordinator.api.set_basic_moment(api_value)
        await self.coordinator.async_request_refresh()


class HomeTouchUserSelect(HomeTouchSelectBase):
    """Sélecteur des User Moments."""

    _attr_name = "Scénario"
    _attr_icon = "mdi:gesture-tap-button"

    def __init__(self, coordinator: HomeTouchCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_user_moment"

    @property
    def options(self) -> list[str]:
        return list(self.coordinator.data.get("user", {}).get("sceneValues", []))

    @property
    def current_option(self) -> str | None:
        return self.coordinator.data.get("user", {}).get("lastScene") or None

    async def async_select_option(self, option: str) -> None:
        if option not in self.options:
            raise ValueError(f"Scénario utilisateur inconnu : {option}")
        await self.coordinator.api.set_user_moment(option)
        await self.coordinator.async_request_refresh()
