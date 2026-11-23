import json
import re
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from . import Tool


class WeatherTool(Tool):
    name = "get_weather"

    description = (
        "Read the weather forecast for one city and date. "
        "Use city codes from the mock data, such as ulm or muenchen. "
        "Convert the requested date to YYYY-MM-DD."
    )

    def __init__(self, log, base_url):
        super().__init__(log)
        self.base_url = base_url

    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City code, such as ulm or muenchen",
                },
                "date": {
                    "type": "string",
                    "description": "Weather date in YYYY-MM-DD format",
                },
            },
            "required": ["city", "date"],
            "additionalProperties": False,
        }

    def run(self, args: dict) -> dict:
        city, day = self.validate_args(args)
        url = f"{self.base_url.rstrip('/')}/weather/{city}/{day}.json"
        request = Request(url, headers={"Accept": "application/json"})

        try:
            with urlopen(request, timeout=30) as response:
                data = json.load(response)
        except HTTPError as exc:
            if exc.code == 404:
                return {
                    "status": "no_data",
                    "city": city,
                    "date": day,
                    "message": "No weather data is available for this city and date.",
                }
            raise RuntimeError(f"Weather endpoint returned HTTP {exc.code}") from None
        except URLError:
            raise RuntimeError("Could not reach the weather endpoint") from None

        return {
            "status": "ok",
            "city": city,
            "date": day,
            "data": data,
        }

    @staticmethod
    def validate_args(args: dict) -> tuple[str, str]:
        if not isinstance(args, dict) or set(args) != {"city", "date"}:
            raise ValueError(
                "Tool arguments must contain exactly two fields: city and date"
            )

        city = args["city"]
        day = args["date"]

        if (
            not isinstance(city, str)
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", city)
        ):
            raise ValueError("city must be a lowercase mock-data city code")
        if not isinstance(day, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            raise ValueError("date must use YYYY-MM-DD")

        date.fromisoformat(day)
        return city, day