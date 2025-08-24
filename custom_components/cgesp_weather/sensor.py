from __future__ import annotations
import re
from datetime import timedelta
from typing import Any
import aiohttp
from bs4 import BeautifulSoup

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS, PERCENTAGE, UnitOfPressure, UnitOfSpeed
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

DOMAIN = "cgesp"

STATIONS = {
    "Ipiranga": "1000840",
    "Sé": "1000940",
    "Mooca": "1000300",
    "Penha": "1000850",
    "São Miguel Paulista": "1000910",
    "Butantã": "1000950",
    "Santo Amaro": "1000960",
    "M Boi Mirim": "1000970",
    "Cidade Ademar": "1000980",
    "Barragem Parelheiros": "1000990",
    "Marsilac": "1001000",
    "Lapa": "1001010",
    "Campo Limpo": "1001020",
    "Capela do Socorro": "1001030",
    "Vila Formosa": "1001040",
    "Vila Prudente": "1001050",
    "Vila Maria": "1001060",
    "Pinheiros": "1001090",
    "Mauá - Paço Municipal": "1001110",
    "Santana do Parnaíba": "1001120",
    "Riacho Grande": "1001130"
}

DEFAULT_STATION = "Ipiranga"

async def async_setup_platform(hass: HomeAssistant, config: dict, async_add_entities: AddEntitiesCallback, discovery_info=None):
    station_name = config.get("station_name", DEFAULT_STATION)
    station_code = STATIONS.get(station_name, STATIONS[DEFAULT_STATION])
    session = aiohttp.ClientSession()
    coordinator = CGECoordinator(hass, session, station_code)

    await coordinator.async_config_entry_first_refresh()

    dev_info = DeviceInfo(
        identifiers={(DOMAIN, station_code)},
        name=f"CGE {station_name}",
        manufacturer="CGE - Prefeitura de São Paulo",
        model="Estação Meteorológica",
        configuration_url=f"https://www.cgesp.org/v3/estacao.jsp?POSTO={station_code}"
    )

    entities = [
        CGESensor(coordinator, "temperature_current", f"CGE {station_name} Temperatura", "Temperatura atual", TEMP_CELSIUS, dev_info),
        CGESensor(coordinator, "temperature_max", f"CGE {station_name} Temp Máx", "Temperatura máxima", TEMP_CELSIUS, dev_info),
        CGESensor(coordinator, "temperature_min", f"CGE {station_name} Temp Mín", "Temperatura mínima", TEMP_CELSIUS, dev_info),
        CGESensor(coordinator, "humidity_current", f"CGE {station_name} Umidade", "Umidade atual", PERCENTAGE, dev_info),
        CGESensor(coordinator, "humidity_max", f"CGE {station_name} Umidade Máx", "Umidade máxima", PERCENTAGE, dev_info),
        CGESensor(coordinator, "humidity_min", f"CGE {station_name} Umidade Mín", "Umidade mínima", PERCENTAGE, dev_info),
        CGESensor(coordinator, "pressure_current", f"CGE {station_name} Pressão", "Pressão atual", UnitOfPressure.HPA, dev_info),
        CGESensor(coordinator, "pressure_max", f"CGE {station_name} Pressão Máx", "Pressão máxima", UnitOfPressure.HPA, dev_info),
        CGESensor(coordinator, "pressure_min", f"CGE {station_name} Pressão Mín", "Pressão mínima", UnitOfPressure.HPA, dev_info),
        CGESensor(coordinator, "wind_direction", f"CGE {station_name} Vento Direção", "Direção do vento", None, dev_info),
        CGESensor(coordinator, "wind_speed", f"CGE {station_name} Vento Veloc", "Velocidade do vento", UnitOfSpeed.KILOMETERS_PER_HOUR, dev_info),
        CGESensor(coordinator, "wind_gust", f"CGE {station_name} Vento Rajada", "Rajada de vento", UnitOfSpeed.KILOMETERS_PER_HOUR, dev_info),
        CGESensor(coordinator, "rain_current_period", f"CGE {station_name} Chuva Atual", "Chuva período atual", "mm", dev_info),
        CGESensor(coordinator, "rain_previous_period", f"CGE {station_name} Chuva Anterior", "Chuva período anterior", "mm", dev_info),
        CGESensor(coordinator, "rain_reset_time", f"CGE {station_name} Zeramento", "Horário de zeramento", None, dev_info),
    ]

    async_add_entities(entities, True)

class CGECoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession, station_code: str) -> None:
        super().__init__(hass, logger=hass.logger, name=f"CGE {station_code}", update_interval=timedelta(minutes=5))
        self._session = session
        self.station_code = station_code

    async def _async_update_data(self) -> dict[str, Any]:
        url = f"https://www.cgesp.org/v3/estacao.jsp?POSTO={self.station_code}"
        try:
            async with self._session.get(url, timeout=20) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"HTTP {resp.status}")
                text = await resp.text()
        except Exception as err:
            raise UpdateFailed(err) from err
        return self._parse(text)

    def _parse(self, html: str) -> dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n").strip()

        def find_float(label: str) -> float | None:
            m = re.search(label + r"\s*:\s*([0-9]+(?:[.,][0-9]+)?)", text, re.IGNORECASE)
            if not m:
                return None
            val = m.group(1).replace(",", ".")
            try:
                return float(val)
            except:
                return None

        def find_str(label: str) -> str | None:
            m = re.search(label + r"\s*:\s*([A-Za-zÇÃÕÂÊÍÓÚÄËÏÖÜÑ\-]+)", text, re.IGNORECASE)
            return m.group(1) if m else None

        data = {
            "rain_current_period": find_float(r"Per\. Atual"),
            "rain_previous_period": find_float(r"Per\. Anterior"),
            "rain_reset_time": re.search(r"Zeramento\s*:\s*([0-9]{2}:[0-9]{2}:[0-9]{2})", text).group(1) if re.search(r"Zeramento\s*:\s*([0-9]{2}:[0-9]{2}:[0-9]{2})", text) else None,
            "temperature_current": find_float(r"Atual"),
            "temperature_max": find_float(r"Máxima"),
            "temperature_min": find_float(r"Mínima"),
            "humidity_current": find_float(r"Atual"),
            "humidity_max": find_float(r"Máxima"),
            "humidity_min": find_float(r"Mínima"),
            "wind_direction": find_str(r"Direção"),
            "wind_speed": find_float(r"Velocidade"),
            "wind_gust": find_float(r"Rajada"),
            "pressure_current": find_float(r"Atual"),
            "pressure_max": find_float(r"Máxima"),
            "pressure_min": find_float(r"Mínima"),
        }
        return data

class CGESensor(SensorEntity):
    def __init__(self, coordinator: CGECoordinator, key: str, name: str, desc: str, unit: str | None, device_info: DeviceInfo) -> None:
        self._coordinator = coordinator
        self._key = key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = f"cgesp_{key}"
        self._attr_device_info = device_info
        self._attr_extra_state_attributes = {"description": desc}

    @property
    def native_value(self) -> Any:
        return self._coordinator.data.get(self._key)

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success

    async def async_update(self) -> None:
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self._coordinator.async_add_listener(self.async_write_ha_state))
