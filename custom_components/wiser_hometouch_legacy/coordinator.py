"""Coordinateur de données pour Wiser HomeTouch Legacy."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HomeTouchApi, HomeTouchError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

MAX_UPDATE_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 1


class HomeTouchCoordinator(DataUpdateCoordinator[dict]):
    """Coordonne l'interrogation périodique du HomeTouch."""

    def __init__(self, hass: HomeAssistant, api: HomeTouchApi) -> None:
        self.api = api
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict:
        """Met à jour les données avec plusieurs tentatives avant indisponibilité."""
        last_error: HomeTouchError | None = None

        for attempt in range(1, MAX_UPDATE_ATTEMPTS + 1):
            try:
                return await self.api.get_state()
            except HomeTouchError as err:
                last_error = err
                if attempt < MAX_UPDATE_ATTEMPTS:
                    _LOGGER.debug(
                        "Échec de lecture HomeTouch (%s/%s), nouvelle tentative dans %ss: %s",
                        attempt,
                        MAX_UPDATE_ATTEMPTS,
                        RETRY_DELAY_SECONDS,
                        err,
                    )
                    await asyncio.sleep(RETRY_DELAY_SECONDS)

        raise UpdateFailed(str(last_error)) from last_error
