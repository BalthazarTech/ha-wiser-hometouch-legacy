"""Local API client for legacy Schneider Electric Wiser HomeTouch."""

from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout

from .const import USER_AGENT


class HomeTouchError(Exception):
    """Base HomeTouch exception."""


class HomeTouchConnectionError(HomeTouchError):
    """HomeTouch connection failed."""


class HomeTouchApi:
    """Client for the local HomeTouch OCF API."""

    def __init__(self, session: ClientSession, host: str) -> None:
        self._session = session
        self._host = host
        self._base_url = f"http://{host}/ocf"

    @property
    def host(self) -> str:
        """Return HomeTouch host."""
        return self._host

    async def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Connection": "close",
        }
        if payload is not None:
            headers["Content-Type"] = "application/json"

        try:
            async with self._session.request(
                method,
                f"{self._base_url}{path}",
                headers=headers,
                json=payload,
                timeout=ClientTimeout(total=8),
            ) as response:
                response.raise_for_status()
                return await response.json(content_type=None)
        except (asyncio.TimeoutError, ClientError, ValueError) as err:
            raise HomeTouchConnectionError(
                f"Unable to communicate with HomeTouch {self._host}: {err}"
            ) from err

    async def get_basic_moments(self) -> dict[str, Any]:
        """Return Basic Moments."""
        return await self._request("GET", "/sceneCollection/0")

    async def get_user_moments(self) -> dict[str, Any]:
        """Return User Moments."""
        return await self._request("GET", "/sceneCollection/1")

    async def get_state(self) -> dict[str, Any]:
        """Return Basic and User Moments using one bulk request."""
        data = await self._request("GET", "/oic/resx?if=oic.if.b")

        basic = None
        user = None

        def walk(value: Any) -> None:
            nonlocal basic, user
            if isinstance(value, dict):
                href = value.get("href")
                rep = value.get("rep")
                if href == "/sceneCollection/0" and isinstance(rep, dict):
                    basic = rep
                elif href == "/sceneCollection/1" and isinstance(rep, dict):
                    user = rep
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(data)

        if basic is None or user is None:
            raise HomeTouchError("Scene collections not found in HomeTouch response")

        return {"basic": basic, "user": user}

    async def set_basic_moment(self, moment: str) -> dict[str, Any]:
        """Activate a Basic Moment."""
        return await self._request(
            "POST",
            "/sceneCollection/0",
            {"isIrrelevant": False, "lastScene": moment},
        )

    async def set_user_moment(self, moment: str) -> dict[str, Any]:
        """Activate a User Moment."""
        return await self._request(
            "POST",
            "/sceneCollection/1",
            {"isIrrelevant": False, "lastScene": moment},
        )
