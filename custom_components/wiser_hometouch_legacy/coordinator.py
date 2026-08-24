"""Data coordinator for Wiser HomeTouch Legacy."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HomeTouchApi, HomeTouchError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class HomeTouchCoordinator(DataUpdateCoordinator[dict]):
    """Coordinate HomeTouch polling."""

    def __init__(self, hass: HomeAssistant, api: HomeTouchApi) -> None:
        self.api = api
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict:
        try:
            return await self.api.get_state()
        except HomeTouchError as err:
            raise UpdateFailed(str(err)) from err
