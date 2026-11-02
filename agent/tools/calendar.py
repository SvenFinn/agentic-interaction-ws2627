
import json
import re
import time
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from . import Tool

class CalendarTool(Tool):
    name = "get_calendar_day"

    description = (
        "Read all calendar appointments for one day. "
        "Use this to answer calendar questions. "
        "Convert the requested date to YYYY-MM-DD."
    )

    def __init__(self, log, base_url):
        super().__init__(log)
        self.base_url = base_url

    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Calendar date in YYYY-MM-DD format",
                }
            },
            "required": ["date"],
            "additionalProperties": False,
        }

    def run(self, args: dict) -> dict:
        day = self.validate_date(args)

        url = f"{self.base_url.rstrip('/')}/calendar/{day}.json"

        request = Request(
            url,
            headers={"Accept": "application/json"},
        )

        try:
            with urlopen(request, timeout=30) as response:
                data = json.load(response)

        except HTTPError as exc:
            if exc.code == 404:
                return {
                    "status": "no_data",
                    "date": day,
                    "message": (
                        "No calendar data is available for this day. "
                        "This does not mean there are no appointments."
                    ),
                }

            raise RuntimeError(
                f"Calendar endpoint returned HTTP {exc.code}"
            ) from None

        except URLError:
            raise RuntimeError(
                "Could not reach the calendar endpoint"
            ) from None

        return {
            "status": "ok",
            "date": day,
            "data": data,
        }

    @staticmethod
    def validate_date(args: dict) -> str:
        if not isinstance(args, dict) or set(args) != {"date"}:
            raise ValueError(
                "Tool arguments must contain exactly one field: date"
            )

        day = args["date"]

        if not isinstance(day, str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}", day
        ):
            raise ValueError("date must use YYYY-MM-DD")

        date.fromisoformat(day)

        return day