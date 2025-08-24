from __future__ import annotations
from homeassistant.core import HomeAssistant

DOMAIN = "cgesp"

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True