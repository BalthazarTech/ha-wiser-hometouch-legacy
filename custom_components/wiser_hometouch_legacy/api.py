"""Client API local du Schneider Electric Wiser HomeTouch historique."""

from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout

from .const import USER_AGENT


class HomeTouchError(Exception):
    """Erreur de base du HomeTouch."""


class HomeTouchConnectionError(HomeTouchError):
    """Échec de communication avec le HomeTouch."""


class HomeTouchApi:
    """Client de l'API OCF locale du HomeTouch."""

    def __init__(self, session: ClientSession, host: str) -> None:
        self._session = session
        self._host = host
        self._base_url = f"http://{host}/ocf"

    @property
    def host(self) -> str:
        """Retourne l'adresse du HomeTouch."""
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
                f"Impossible de communiquer avec le HomeTouch {self._host}: {err}"
            ) from err

    async def get_basic_moments(self) -> dict[str, Any]:
        """Retourne les Basic Moments."""
        return await self._request("GET", "/sceneCollection/0")

    async def get_user_moments(self) -> dict[str, Any]:
        """Retourne les User Moments."""
        return await self._request("GET", "/sceneCollection/1")

    async def get_state(self) -> dict[str, Any]:
        """Retourne les Basic et User Moments en une seule requête."""
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
            raise HomeTouchError("Collections de scènes introuvables dans la réponse du HomeTouch")

        return {"basic": basic, "user": user}

    async def set_basic_moment(self, moment: str) -> dict[str, Any]:
        """Active un Basic Moment."""
        return await self._request(
            "POST",
            "/sceneCollection/0",
            {"isIrrelevant": False, "lastScene": moment},
        )

    async def set_user_moment(self, moment: str) -> dict[str, Any]:
        """Active un User Moment."""
        return await self._request(
            "POST",
            "/sceneCollection/1",
            {"isIrrelevant": False, "lastScene": moment},
        )

    async def create_user_moment(self, moment: str) -> dict[str, Any]:
        """Crée un User Moment."""
        return await self._request(
            "POST",
            "/sceneCollection/1",
            {"sceneValues": [moment]},
        )

    async def delete_user_moment(self, moment: str) -> dict[str, Any]:
        """Supprime un User Moment."""
        return await self._request(
            "DELETE",
            "/sceneCollection/1",
            {"sceneValues": [moment]},
        )
