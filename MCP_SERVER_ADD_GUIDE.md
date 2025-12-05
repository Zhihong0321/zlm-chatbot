# MCP server addition rules & format

## Scope & source of truth
- Backend source of truth lives in the `mcp_servers` table managed by `backend/app/core/mcp_manager.py` and exposed through the FastAPI routes in `backend/app/api/mcp.py`.
- Legacy/local scripts (`mcp_manager.py`, `mcp_management_api.py`) read/write `mcp_servers.json`; use this only for standalone CLI runs. Prefer the HTTP API so the backend and frontend stay in sync.

## Required fields (per `MCPServerCreate`)
- `name` (string), `description` (string), `command` (string) are mandatory.
- Optional with defaults: `arguments` (list, default `[]`), `environment` (dict, default `{}`), `working_directory` (string or `null`, defaults to project root when not set), `enabled` (bool, default `true`), `auto_start` (bool, default `true`), `health_check_interval` (int seconds, default `30`).
- `id` is auto-generated (UUID) when omitted; if you provide one, it must be unique. Use a short slug (e.g., `search-index-1`) to simplify downstream references.
- Auto-start behavior: when `enabled` and `auto_start` are true, the POST handler will immediately attempt to start the server.

## Command, folder layout, and environment rules
- Place every MCP server in its own sub-folder (e.g., `mcp_servers/<server-id>/`) and keep the entrypoint inside that folder.
- Set `working_directory` to that sub-folder; commands should not rely on project root CWD. Example: `"working_directory": "E:/oneapi/mcp_servers/my-server-1"` and `"command": "python"`, `"arguments": ["main.py"]`.
- `command` + `arguments` must be directly runnable (no shells, no interactive prompts). Examples: `"python"` with script args, or `"npx"` with `-y` and the MCP package name.
- Keep `environment` minimal and non-secret where possible; never bake secrets into the repo—use real env vars in deployment and pass only the variable names here.
- Ensure dependencies for the command (e.g., `npx`, Python modules) are present in the target runtime.

## Add a server via HTTP API (preferred)
POST `http://localhost:8000/api/v1/mcp/servers`
```bash
curl -X POST http://localhost:8000/api/v1/mcp/servers \
  -H "Content-Type: application/json" \
  -d '{
    "id": "my-server-1",              # optional; auto-generated if omitted
    "name": "My Server",
    "description": "Does X for Y",
    "command": "npx",
    "arguments": ["-y", "@modelcontextprotocol/server-template"],
    "environment": {"API_KEY_VAR": "${API_KEY_VAR}"},
    "working_directory": "E:/oneapi/mcp_servers/my-server-1",
    "files": [                        # optional: server-side files (max 20 files, 5MB each)
      {"path": "main.py", "content": "print('hello')"},
      {"path": "config/bill.json", "content": "{...}"}
    ],
    "enabled": true,
    "auto_start": true,
    "health_check_interval": 30
  }'
```
- Success response contains `server_id`; when auto-start succeeds you also get a `process_id`. If auto-start fails, the message includes the error—resolve it, then `POST /api/v1/mcp/servers/{id}/start`.

### File upload rules (via `files`)
- Max 20 files per request; each file max 5MB (UTF-8 text only).
- Paths must be **relative** to `working_directory`; absolute paths or path escape (`..`) are rejected.
- Files are written before the server is registered/started, ensuring required assets (e.g., `bill.json`, entrypoints) exist at runtime.

## Start/stop/control endpoints
- Start: `POST /api/v1/mcp/servers/{id}/start`
- Stop: `POST /api/v1/mcp/servers/{id}/stop`
- Restart: `POST /api/v1/mcp/servers/{id}/restart`
- Bulk: `POST /api/v1/mcp/start-all` (enabled + auto_start), `POST /api/v1/mcp/stop-all`
- Status: `GET /api/v1/mcp/status`; Health: `GET /api/v1/mcp/health`

## Legacy JSON format (for standalone CLI use)
- File: `mcp_servers.json` with a top-level `servers` array. Each entry mirrors the fields above (including `working_directory`, `enabled`, `auto_start`, `health_check_interval`, `status`, `process_id`, timestamps).
- After editing the file manually, start via `python mcp_management_api.py` (or directly through `mcp_manager.py`) and use the same start/stop logic.

## Readiness checklist before adding a server
- Command runs successfully in the target environment with the provided `working_directory` and `environment`.
- `id` is unique; `name` and `description` clearly describe capabilities.
- `environment` contains only the variables the server truly needs; secrets are supplied at runtime, not committed.
- `health_check_interval` is reasonable for the server’s startup/idle characteristics.
- For `npx` servers, include `-y` to avoid interactive prompts; for Python servers, ensure the module is importable from the working directory.
- If the server needs data files (e.g., `bill.json`), include them via the `files` array so they are present on deploy.
