import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, STATIONS, DEFAULT_STATION

class CGESPWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):


    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input["station"], data=user_input)

        schema = vol.Schema({
            vol.Required("station", default=DEFAULT_STATION): vol.In(list(STATIONS.keys()))
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
