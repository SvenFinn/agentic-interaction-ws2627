import json
import re
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from . import Tool


class TransitTool(Tool):
    name = "get_train_connections"

    description = (
        "Read train connections for one mock-data route and date. "
        "Use city codes such as ulm and muenchen. "
        "Convert the requested date to YYYY-MM-DD."
    )

    def __init__(self, log, base_url):
        super().__init__(log)
        self.base_url = base_url

    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "from": {
                    "type": "string",
                    "description": "Departure city code, such as ulm",
                },
                "to": {
                    "type": "string",
                    "description": "Destination city code, such as muenchen",
                },
                "date": {
                    "type": "string",
                    "description": "Travel date in YYYY-MM-DD format",
                },
            },
            "required": ["from", "to", "date"],
            "additionalProperties": False,
        }

    def run(self, args: dict) -> dict:
        origin, destination, day = self.validate_args(args)
        url = (
            f"{self.base_url.rstrip('/')}/transit/"
            f"{origin}/{destination}/{day}.json"
        )
        request = Request(url, headers={"Accept": "application/json"})

        try:
            with urlopen(request, timeout=30) as response:
                data = json.load(response)
        except HTTPError as exc:
            if exc.code == 404:
                return {
                    "status": "no_data",
                    "from": origin,
                    "to": destination,
                    "date": day,
                    "message": (
                        "No train connection data is available "
                        "for this route and date."
                    ),
                }
            raise RuntimeError(f"Transit endpoint returned HTTP {exc.code}") from None
        except URLError:
            raise RuntimeError("Could not reach the transit endpoint") from None

        return {
            "status": "ok",
            "from": origin,
            "to": destination,
            "date": day,
            "data": data,
        }

    @staticmethod
    def validate_args(args: dict) -> tuple[str, str, str]:
        if not isinstance(args, dict) or set(args) != {"from", "to", "date"}:
            raise ValueError(
                "Tool arguments must contain exactly three fields: from, to, and date"
            )

        origin = args["from"]
        destination = args["to"]
        day = args["date"]

        for value_name, value in (
            ("from", origin),
            ("to", destination),
        ):
            if (
                not isinstance(value, str)
                or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value)
            ):
                raise ValueError(
                    f"{value_name} must be a lowercase mock-data city code"
                )

        if not isinstance(day, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            raise ValueError("date must use YYYY-MM-DD")

        date.fromisoformat(day)
        return origin, destination, day
