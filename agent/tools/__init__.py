import time
from abc import ABC, abstractmethod


class Tool(ABC):
    name: str
    description: str

    def __init__(self, log):
        self.log = log

    def spec(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters(),
            },
        }

    @abstractmethod
    def parameters(self) -> dict:
        pass

    @abstractmethod
    def run(self, args: dict) -> dict:
        pass

    def run_tool(self, args: dict) -> dict:
        start = time.perf_counter()

        try:
            result = self.run(args)
            ok = True

        except Exception as exc:
            result = {
                "status": "error",
                "message": (
                    str(exc)
                    if isinstance(exc, (ValueError, RuntimeError))
                    else "Tool execution failed"
                ),
            }
            ok = False

        duration_ms = int(
            (time.perf_counter() - start) * 1000
        )

        self.log.write(
            "tool_run",
            ok=ok,
            tool=self.name,
            args=args,
            duration_ms=duration_ms,
            result=result,
        )

        return result