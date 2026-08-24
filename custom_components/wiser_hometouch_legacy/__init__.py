"""Intégration Wiser HomeTouch Legacy."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HomeTouchApi, HomeTouchError
from .const import CONF_HOST, DOMAIN
from .coordinator import HomeTouchCoordinator

PLATFORMS = [Platform.SELECT]

SERVICE_CREATE_USER_MOMENT = "create_user_moment"
SERVICE_DELETE_USER_MOMENT = "delete_user_moment"
ATTR_NAME = "name"

SERVICE_SCHEMA = vol.Schema({vol.Required(ATTR_NAME): vol.All(str, vol.Strip, vol.Length(min=1, max=64))})


def _get_coordinator(hass: HomeAssistant) -> HomeTouchCoordinator:
    """Retourne le coordinateur HomeTouch configuré."""
    coordinators = hass.data.get(DOMAIN, {})
    if not coordinators:
        raise HomeAssistantError("Aucun Wiser HomeTouch Legacy n'est configuré")
    return next(iter(coordinators.values()))


async def _async_create_user_moment(hass: HomeAssistant, call: ServiceCall) -> None:
    """Crée un User Moment."""
    coordinator = _get_coordinator(hass)
    name = call.data[ATTR_NAME]
    existing = coordinator.data.get("user", {}).get("sceneValues", [])

    if name in existing:
        raise ServiceValidationError(f"Le scénario '{name}' existe déjà")

    try:
        await coordinator.api.create_user_moment(name)
    except HomeTouchError as err:
        raise HomeAssistantError(str(err)) from err

    await coordinator.async_request_refresh()


async def _async_delete_user_moment(hass: HomeAssistant, call: ServiceCall) -> None:
    """Supprime un User Moment."""
    coordinator = _get_coordinator(hass)
    name = call.data[ATTR_NAME]
    existing = coordinator.data.get("user", {}).get("sceneValues", [])

    if name not in existing:
        raise ServiceValidationError(f"Le scénario '{name}' n'existe pas")

    try:
        await coordinator.api.delete_user_moment(name)
    except HomeTouchError as err:
        raise HomeAssistantError(str(err)) from err

    await coordinator.async_request_refresh()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configure Wiser HomeTouch Legacy depuis une entrée de configuration."""
    api = HomeTouchApi(async_get_clientsession(hass), entry.data[CONF_HOST])
    coordinator = HomeTouchCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    if not hass.services.has_service(DOMAIN, SERVICE_CREATE_USER_MOMENT):
        hass.services.async_register(
            DOMAIN,
            SERVICE_CREATE_USER_MOMENT,
            lambda call: _async_create_user_moment(hass, call),
            schema=SERVICE_SCHEMA,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_DELETE_USER_MOMENT):
        hass.services.async_register(
            DOMAIN,
            SERVICE_DELETE_USER_MOMENT,
            lambda call: _async_delete_user_moment(hass, call),
            schema=SERVICE_SCHEMA,
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Décharge une entrée de configuration."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_CREATE_USER_MOMENT)
            hass.services.async_remove(DOMAIN, SERVICE_DELETE_USER_MOMENT)
    return unloaded
