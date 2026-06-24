# MCP Excel Manager

**Chat with your Excel spreadsheets in plain English — a Gemini agent that reads, slices, and edits `.xlsx` files through a Model Context Protocol tool server.**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white) ![Google Gemini](https://img.shields.io/badge/Gemini-8E75B2?style=flat&logo=googlegemini&logoColor=white) ![MCP](https://img.shields.io/badge/Model_Context_Protocol-000000?style=flat&logo=modelcontextprotocol&logoColor=white) ![pandas](https://img.shields.io/badge/pandas-150458?style=flat&logo=pandas&logoColor=white) ![React](https://img.shields.io/badge/React_18-20232A?style=flat&logo=react&logoColor=61DAFB) ![Vite](https://img.shields.io/badge/Vite_5-646CFF?style=flat&logo=vite&logoColor=white)

## Overview

MCP Excel Manager lets you talk to a folder of Excel files the way you'd talk to an analyst: "list my files", "read Accounts.xlsx", "append a row to Leads", "show me the first ten rows of Opportunities". Behind the chat box, a Google Gemini model decides which spreadsheet operation to run and the actual file work happens inside a separate process that speaks the Model Context Protocol (MCP).

The point of the project is to keep the LLM and the file access cleanly separated. Gemini never touches your disk — it only ever emits structured tool calls. A dedicated MCP server owns the spreadsheet logic (pandas + openpyxl) and exposes exactly five tools. The FastAPI backend sits in the middle as the MCP client and agent loop, and a React + Vite single-page app gives you a chat panel with a results area.

I built this as a hands-on way to learn the MCP client/server split and Gemini's function-calling loop end to end. The bundled sample data is CRM-shaped (Accounts, Leads, Opportunities, Features, Workflows), so the assistant reads as a lightweight "chat with your CRM export" tool, but everything it actually does is generic Excel manipulation — point it at any `.xlsx` files you drop into `excel_data/`.

## Key Features

- **Natural-language spreadsheet ops** — ask in English and Gemini picks the right tool: list files, read a whole sheet, read a row range, write a single cell, or append a row.
- **MCP tool server** — a standalone `FastMCP` process (`excel_mcp_server.py`) exposes the Excel operations as MCP tools over stdio, fully decoupled from the LLM.
- **`@mention` file context** — type `@Accounts.xlsx` in your message and the backend auto-loads that sheet and injects it into the prompt as an `<excel file="…">` context block, so Gemini can reason over the data without a tool round-trip.
- **Agent loop with tool execution** — the backend calls Gemini with the available tool schemas, detects function calls in the response, runs them against the MCP server, feeds results back, and repeats until Gemini returns a final text answer.
- **MCP → Gemini schema translation** — a `ToolManager` rewrites MCP JSON Schema into the shape Gemini's `function_declarations` expects (stripping `title`, `$schema`, `anyOf`, etc.) and converts Gemini's protobuf tool-call args back into native Python dicts.
- **Path-traversal guard** — every file operation resolves the name strictly inside `excel_data/` and refuses anything that isn't there, so a model (or user) can't reach outside the data directory.
- **React chat UI** — a two-panel single-page app: a chat box on the left, an assistant-response area on the right, plus `DataTable` and `DataChart` (Recharts) components ready to render tabular and bar/line results.
- **Clean FastAPI structure** — config via `pydantic-settings`, a cached settings object, CORS for the Vite dev server, structured logging, custom error handlers, and a `/health` endpoint.
- **Sample CRM dataset included** — six ready-to-query `.xlsx` files (Accounts, Leads, Opportunities, Features, Workflows, Sample) so the app does something useful the moment you start it.

## How It Works

The system is three processes: the React frontend, the FastAPI backend (MCP client + agent), and the MCP Excel server. A user message flows through all three and back.

### 1. Frontend → backend

The React app (`Chat.jsx`) posts your message to `POST /api/chat` through an axios client. In dev, Vite proxies `/api` to the FastAPI server on port 8000. The chat request body is just `{ "message": "..." }`; the response is `{ "reply": "..." }`.

### 2. Prompt building and `@mention` injection

The backend's chat layer (`UIChat`, extending a base `Chat` orchestrator) preprocesses the query. It scans for `@`-prefixed words, matches them against the real files returned by the MCP `list_excel_files` tool, reads any that match via `read_sheet`, and wraps the contents in `<excel file="...">...</excel>` blocks. That context is folded into a system-style prompt that frames Gemini as an Excel/CRM assistant and tells it to use tools only when needed and not to invent sheet names.

### 3. The Gemini agent loop

`Chat.run()` drives the loop:

1. Collect tool schemas from every registered MCP client via `ToolManager.get_all_tools_schema()`.
2. Send the message history plus those schemas to Gemini (`gemini-2.5-flash`) using `google.generativeai`, passing the tools as `function_declarations`.
3. Inspect the response. `ToolManager.extract_tool_calls()` walks the candidates/parts and pulls out any `function_call` parts, converting their protobuf args into plain dicts.
4. If there are no tool calls, extract the text and return it as the final reply.
5. If there are tool calls, `execute_tool_calls()` finds the MCP client that owns each tool and invokes it, collecting the text content of the results.
6. `resume_with_tool_results()` appends the tool outputs as `function`-role parts and calls Gemini again. The loop repeats until Gemini stops asking for tools.

### 4. The MCP Excel server

`MCPExcelClient` spawns `excel_mcp_server.py` as a subprocess over stdio (`StdioServerParameters` + `stdio_client`), initializes an MCP `ClientSession`, and exposes typed helper methods (`list_excel_files`, `read_sheet`, `read_range`, `write_cell`, `append_row`). The server itself is a `FastMCP` app that registers five tools backed by pandas:

| Tool | What it does |
|------|--------------|
| `list_excel_files` | Globs `excel_data/*.xlsx` and returns the file names |
| `read_sheet` | Reads a sheet into a DataFrame and returns it as a list of row dicts |
| `read_range` | Returns an inclusive slice of rows from a sheet (`start_row`..`end_row`) |
| `write_cell` | Sets a single cell by row/column index and writes the file back |
| `append_row` | Concatenates a new row dict onto the sheet and saves |

Reads and writes go through pandas with `openpyxl` as the Excel engine, and every call passes through the `_resolve_file()` guard that keeps access inside `excel_data/`.

### 5. Lifecycle

On FastAPI startup the app connects the MCP client (spawning the server subprocess) and stashes the chat agent on `app.state`. On shutdown it closes the MCP session through an `AsyncExitStack` for a clean teardown. On Windows the client test harness switches to the Proactor event loop policy so stdio subprocess transport works.

## Tech Stack

- **Languages:** Python (~79% of the repo), JavaScript, CSS, HTML.
- **Backend:** FastAPI, Uvicorn, Pydantic / `pydantic-settings`, httpx, asyncio.
- **AI / agent:** Google Gemini (`gemini-2.5-flash`) via `google-generativeai`; Model Context Protocol (`mcp`, `mcp[cli]`) with `FastMCP` for the tool server. (`anthropic` is also listed as a dependency for an alternate LLM path.)
- **Data:** pandas + openpyxl for reading/writing `.xlsx`.
- **Frontend:** React 18, Vite 5, axios, Recharts.

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ (for the frontend)
- A Google Gemini API key

### Installation

```bash
git clone https://github.com/DCode-v05/MCP-Excel-Manager.git
cd MCP-Excel-Manager

# backend deps
pip install -r requirements.txt

# frontend deps
cd frontend
npm install
cd ..
```

Create a `.env` file in the project root with your Gemini key:

```bash
GEMINI_API_KEY=your_key_here
```

### Running

Start the backend (it spawns the MCP Excel server automatically on startup):

```bash
# from the repo root
python -m backend.main
# or
uvicorn backend.main:app --reload
```

The API comes up on `http://localhost:8000` (docs at `/docs`, health at `/api/health`).

Start the frontend in a second terminal:

```bash
cd frontend
npm run dev
```

The app opens at `http://localhost:5173` and proxies API calls to the backend.

## Usage

Drop any `.xlsx` files you want to query into `excel_data/` (six CRM-style samples ship with the repo). Then open the web app and type into the chat box. Some things that work:

- `List all Excel files.`
- `Read the contents of Accounts.xlsx.`
- `Show me rows 0 to 9 of the Leads sheet.`
- `Compare @Accounts.xlsx with @Opportunities.xlsx.` — the `@mentions` pull both sheets into context.
- `Append a row to Leads.xlsx with name "Alice".`

Gemini decides which tool to call, the MCP server runs it against the file, and the assistant replies in text. You can also hit the API directly:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List all Excel files"}'
```

## Project Structure

```
MCP-Excel-Manager/
├── backend/
│   ├── api/
│   │   ├── models.py            # Pydantic request/response schemas (ChatRequest/Response)
│   │   └── routes.py            # /health and /chat endpoints
│   ├── core/
│   │   ├── chat.py              # Base agent loop: Gemini ↔ tool execution
│   │   └── ui_chat.py           # Adds @mention context injection + prompt framing
│   ├── mcp/
│   │   ├── excel_mcp_server.py  # FastMCP server: the 5 Excel tools (pandas)
│   │   ├── mcp_client.py        # stdio MCP client + typed Excel helpers
│   │   └── tool_manager.py      # MCP→Gemini schema translation, call extraction/exec
│   ├── services/
│   │   └── gemini_service.py    # Gemini wrapper: chat, tool calls, result resumption
│   ├── utils/
│   │   ├── error_handlers.py    # Custom exception handling
│   │   └── logger.py            # Logging config
│   ├── config.py                # pydantic-settings config (Gemini key, dirs, CORS)
│   └── main.py                  # FastAPI app + MCP startup/shutdown wiring
├── excel_data/                  # Sample .xlsx files (Accounts, Leads, Opportunities, …)
├── frontend/
│   ├── src/
│   │   ├── components/          # Chat, DataTable, DataChart (Recharts), Loader
│   │   ├── services/api.js      # axios client for /api/chat
│   │   ├── styles/              # App.css, Loader.css
│   │   ├── App.jsx              # Two-panel layout (chat + results)
│   │   └── index.jsx            # React entry point
│   ├── vite.config.js           # Vite dev server + /api proxy to FastAPI
│   └── package.json
├── requirements.txt
└── README.md
```

---

## Contact

<table>
  <tr><td><b>Portfolio:</b> <a href="https://www.denistan.me">Denistan</a></td><td><b>LinkedIn:</b> <a href="https://www.linkedin.com/in/denistanb">denistanb</a></td></tr>
  <tr><td><b>GitHub:</b> <a href="https://github.com/DCode-v05">DCode-v05</a></td><td><b>LeetCode:</b> <a href="https://leetcode.com/u/Denistan_B">Denistan_B</a></td></tr>
  <tr><td colspan="2" align="center"><b>Email:</b> <a href="mailto:denistanb05@gmail.com">denistanb05@gmail.com</a></td></tr>
</table>

Made with ❤️ by **Denistan B**
