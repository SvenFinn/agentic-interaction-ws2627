import time
from abc import ABC, abstractmethod


class ToolManager:
    def __init__(self):
        self.tools = {}

    def register_tool(self, tool):
        if tool.name in self.tools:
            raise ValueError(f"Tool with name '{tool.name}' is already registered.")
        self.tools[tool.name] = tool

    def get_tool(self, name: str):
        return self.tools.get(name)

    def get_tool_specs(self):
        return [tool.spec() for tool in self.tools.values()]

    def run_tool(self, name: str, args: dict) -> dict:

        tool = self.get_tool(name)
        if not tool:
            result = {
                "status": "error",
                "message": f"Tool with name '{name}' is not registered.",
            }

        else:
            try:
                result = tool.run(args)
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

        return result


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
