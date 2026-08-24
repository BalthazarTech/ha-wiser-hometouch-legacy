"""Config flow for Wiser HomeTouch Legacy."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HomeTouchApi, HomeTouchError
from .const import CONF_HOST, DOMAIN


class HomeTouchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wiser HomeTouch Legacy."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle initial setup."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            api = HomeTouchApi(async_get_clientsession(self.hass), host)

            try:
                basic = await api.get_basic_moments()
            except HomeTouchError:
                errors["base"] = "cannot_connect"
            else:
                values = basic.get("sceneValues", [])
                if not all(moment in values for moment in ("Home", "Away", "Sleep")):
                    errors["base"] = "not_hometouch"
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
                        default=user_input.get(CONF_HOST, "10.0.0.66")
                        if user_input
                        else "10.0.0.66",
                    ): str,
                }
            ),
            errors=errors,
        )
