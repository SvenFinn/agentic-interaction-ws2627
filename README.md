# Agentic Human-AI Interaction

Exercise 01: First Tool Call (28 October 2026).

This project is a small calendar question-answering agent. It sends a
natural-language question to an OpenAI-compatible chat-completions endpoint
and uses a calendar tool to retrieve the relevant daily data.

## Requirements

- Python 3.11 or newer
- An OpenAI-compatible model endpoint that supports tool calls
- Internet access to the model and calendar endpoints

The project has no application dependencies beyond the package listed in
`requirements.txt`.

## Installation

Clone the public repository, create a virtual environment, and activate it:

```bash
git clone https://github.com/SvenFinn/agentic-interaction-ws2627.git
cd agentic-interaction-ws2627
python3 -m venv .venv
source .venv/bin/activate
```

On systems with multiple Python versions, use `python3.11` (or newer) for
both commands. Then install the package:

```bash
python -m pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the repository root. The exercise's default
configuration uses Groq and the provided read-only mock calendar data:

```dotenv
OPENAI_BASE_URL=https://api.groq.com/openai/v1
MODEL=openai/gpt-oss-20b
OPENAI_API_KEY=your-groq-api-key
DATA_BASE_URL=https://jhbelz.github.io/agentic-interaction-data/v1
```

`OPENAI_API_KEY` must contain your own API key.
Environment variables already set in the shell
take precedence over values in `.env`.

## How to run it

From the repository root, activate the virtual environment and pass a
calendar question in quotes:

```bash
source .venv/bin/activate
python -m agent "What is in my calendar on 2026-10-29?"
```

The answer is printed to the terminal and a successful run exits with code
`0`. The agent supports questions about multiple dates and fetches every day
in an inclusive date range before answering. For example:

```bash
python -m agent "What appointments do I have between 2026-10-29 and 2026-10-31?"
```

If no question is supplied, the command exits with a usage message.

## Run logs

Every run creates one JSON Lines file in `logs/`. Each event contains the
following fields where applicable:

- `ts`: ISO 8601 timestamp
- `run_id`: one identifier shared by all events in the run
- `event`: `user_task`, `tool_call`, `tool_result`, `final`, or `error`
- `tool` and `args`: tool name and arguments
- `ok`: whether the step succeeded
- `model`: model name sent to the endpoint
- `duration_ms`: duration of the step in milliseconds

## Required project paths

```text
README.md
requirements.txt
agent/
├── __main__.py
├── logger/
└── tools/
.gitignore
```

The `.gitignore` excludes local configuration and generated files, including
`.env`, `.venv/`, and `logs/`.

## Project structure

```text
agent/
├── __main__.py          # Command-line entry point and agent loop
├── logger/              # JSON Lines run logging
└── tools/
    └── calendar.py      # Calendar API tool
```
