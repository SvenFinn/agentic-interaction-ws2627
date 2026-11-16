import json
import time
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Literal, cast

from openai import OpenAI, OpenAIError
from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCallUnion,
    ChatCompletionMessageToolCall,
)

from .config import Config
from ..logger import RunLog
from ..tools import ToolManager

ToolChoice = Literal["auto", "required", "none"]
ToolResult = dict[str, Any]


def _elapsed_ms(start: float) -> int:
    return int((time.perf_counter() - start) * 1000)


class Agent(ABC):
    """Base class: one instance == one chat (it keeps the message history)."""

    config: Config
    log: RunLog
    client: OpenAI
    tools: ToolManager
    history: list[ChatCompletionMessageParam]

    # Subclasses can override this to force a tool call on the first turn.
    force_tool_on_first_turn: ClassVar[bool] = False

    def __init__(self, config: Config, log: RunLog | None = None) -> None:
        self.config: Config = config
        self.log: RunLog = log or RunLog()
        self.client: OpenAI = OpenAI(
            base_url=config.base_url,
            api_key=config.api_key,
            timeout=90,
        )
        self.tools: ToolManager = ToolManager(log=self.log)
        self.register_tools(self.tools)
        self.history: list[ChatCompletionMessageParam] = []

    def reset(self) -> None:
        self.history.clear()

    def run(self, prompt: str) -> str:
        """Run one conversation turn.

        On failure, discard messages added during this turn.

        Note:
            Tool side effects are not rolled back.
        """
        self.log.write("user_task", task=prompt)
        checkpoint = len(self.history)
        self.history.append({"role": "user", "content": prompt})

        try:
            return self._loop(first_turn=checkpoint == 0)
        except Exception:
            # Don't leave half-finished tool calls in the history.
            del self.history[checkpoint:]
            raise

    def _loop(self, first_turn: bool) -> str:
        for round_index in range(self.config.max_rounds):
            start = time.perf_counter()
            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": self.system_prompt()},
                *self.history,
            ]
            force = self.force_tool_on_first_turn and first_turn and round_index == 0
            message = self._complete(messages, "required" if force else "auto")
            model_ms = _elapsed_ms(start)

            if not message.tool_calls:
                text = (message.content or "").strip()
                if not text:
                    raise RuntimeError("The model returned no final answer")
                self.history.append({"role": "assistant", "content": text})
                self.log.write("final", answer=text, duration_ms=model_ms)
                return text

            self.history.append(
                cast(ChatCompletionMessageParam, message.model_dump(exclude_none=True))
            )
            for call in message.tool_calls:
                result = self._execute(call, model_ms)
                self.history.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )

        raise RuntimeError(
            f"Stopped after {self.config.max_rounds} model rounds without a final answer"
        )

    def _complete(
        self, messages: list[ChatCompletionMessageParam], tool_choice: ToolChoice
    ) -> ChatCompletionMessage:
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                tools=self.tools.get_tool_specs(),
                tool_choice=tool_choice,
            )
        except OpenAIError as exc:
            raise RuntimeError(f"Model request failed: {exc}") from None
        return response.choices[0].message

    def _execute(
        self, call: ChatCompletionMessageToolCallUnion, model_ms: int
    ) -> ToolResult:

        if not isinstance(call, ChatCompletionMessageToolCall):
            raise RuntimeError("Model returned an invalid tool call")

        name: str = call.function.name
        args: dict[str, Any] | None

        try:
            parsed = json.loads(call.function.arguments)
            args = parsed if isinstance(parsed, dict) else None
        except (ValueError, TypeError):
            args = None

        self.log.write(
            "tool_call",
            tool=name,
            args=args,
            duration_ms=model_ms,
            tool_call_id=call.id,
        )

        start = time.perf_counter()

        error: str | None = None
        result: ToolResult

        if args is None:
            error = "Invalid tool arguments"
        else:
            try:
                result = self.tools.run_tool(name, args)
            except (ValueError, RuntimeError) as exc:
                error = str(exc)
            except Exception:
                error = "Tool request failed"

        if error is not None:
            result = {"status": "error", "message": error}
            self.log.write("error", ok=False, tool=name, args=args, error=error)

        self.log.write(
            "tool_result",
            ok=error is None,
            tool=name,
            args=args,
            duration_ms=_elapsed_ms(start),
            result=result,
            tool_call_id=call.id,
        )
        return result

    @abstractmethod
    def system_prompt(self) -> str:
        """Called on every request, so dynamic content (e.g. today's date) stays fresh."""

    def register_tools(self, tools: ToolManager) -> None:
        """Override to register the tools this agent can use. Default: none."""
