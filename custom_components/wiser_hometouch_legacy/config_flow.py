"""Config flow for Wiser HomeTouch Legacy."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HomeTouchApi, HomeTouchError
from .const import CONF_HOST, DOMAIN

DEFAULT_HOST = "10.0.0.66"


async def _async_validate_host(hass, host: str) -> str | None:
    """Valide qu'une adresse correspond à un HomeTouch compatible."""
    api = HomeTouchApi(async_get_clientsession(hass), host)

    try:
        basic = await api.get_basic_moments()
    except HomeTouchError:
        return "cannot_connect"

    values = basic.get("sceneValues", [])
    if not all(moment in values for moment in ("Home", "Away", "Sleep")):
        return "not_hometouch"

    return None


class HomeTouchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wiser HomeTouch Legacy."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle initial setup."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            error = await _async_validate_host(self.hass, host)
            if error:
                errors["base"] = error
            else:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Wiser HomeTouch ({host})",
                    data={CONF_HOST: host},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=user_input.get(CONF_HOST, DEFAULT_HOST)
                        if user_input
                        else DEFAULT_HOST,
                    ): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input=None):
        """Permet de modifier l'adresse IP d'un HomeTouch existant."""
        errors = {}
        entry = self._get_reconfigure_entry()
        current_host = entry.data[CONF_HOST]

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            error = await _async_validate_host(self.hass, host)
            if error:
                errors["base"] = error
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={CONF_HOST: host},
                    title=f"Wiser HomeTouch ({host})",
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=user_input.get(CONF_HOST, current_host)
                        if user_input
                        else current_host,
                    ): str,
                }
            ),
            errors=errors,
        )
