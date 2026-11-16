import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    base_url: str
    model: str
    api_key: str
    data_base_url: str
    max_rounds: int = 30

    @classmethod
    def from_env(cls) -> "Config":
        names = ("OPENAI_BASE_URL", "MODEL", "OPENAI_API_KEY", "DATA_BASE_URL")
        optional_names = ("MAX_ROUNDS",)

        values = {n: os.environ.get(n, "").strip() for n in names}
        optional_values = {n: os.environ.get(n, "").strip() for n in optional_names}

        missing = [n for n, v in values.items() if not v]
        if missing:
            raise ValueError("Missing configuration: " + ", ".join(missing))
        return cls(
            base_url=values["OPENAI_BASE_URL"],
            model=values["MODEL"],
            api_key=values["OPENAI_API_KEY"],
            data_base_url=values["DATA_BASE_URL"],
            max_rounds=(
                int(optional_values["MAX_ROUNDS"])
                if optional_values["MAX_ROUNDS"]
                else 30
            ),
        )
