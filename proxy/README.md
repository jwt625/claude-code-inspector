# Claude Code Logging Proxy

A lightweight HTTP proxy server that logs all communication between Claude Code and the inference endpoint.

## Features

- **Real-time SSE Streaming**: Supports Server-Sent Events (SSE) streaming for both Anthropic and OpenAI-compatible endpoints
- **Format Detection**: Automatically detects and handles both Anthropic and OpenAI SSE formats
- **Comprehensive Logging**: Logs all requests and responses while preserving streaming performance
- **Header Preservation**: Maintains streaming headers (`Content-Type: text/event-stream`) for client compatibility
- **Zero Buffering**: Streams responses in real-time without waiting for complete response

## Setup

1. Create `.env` file from template:
```bash
cp .env.example .env
```

2. Edit `.env` and set your upstream URL:
```
UPSTREAM_URL=https://your-inference-endpoint.com
```

3. Install dependencies:
```bash
uv sync
```


or
```bash
uv pip install flask requests python-dotenv flask_cors
```

## Running

Start the proxy server:
```bash
uv run python proxy_server.py
```

The server will start on `http://127.0.0.1:58734` by default.

## Claude Code Configuration

Update your Claude Code settings to use the proxy:

**Option 1: Environment variable**
```bash
export ANTHROPIC_BASE_URL=http://127.0.0.1:58734
```

**Option 2: Settings file** (`.claude/settings.json`)
```json
{
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:58734",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "zai-org/GLM-4.6-FP8"
}
```

## Streaming Support

The proxy now supports real-time SSE streaming for both Anthropic and OpenAI-compatible endpoints:

### Anthropic Format
```
event: message_start
data: {"type":"message_start","message":{...}}

event: content_block_delta
data: {"type":"content_block_delta","delta":{...}}

event: message_stop
data: {"type":"message_stop"}
```

### OpenAI Format
```
data: {"id":"chatcmpl-123","choices":[{"delta":{"content":"Hello"}}]}

data: {"id":"chatcmpl-123","choices":[{"delta":{"content":" world"}}]}

data: [DONE]
```

The proxy:
1. Detects streaming responses via `Content-Type: text/event-stream` header
2. Streams chunks to the client in real-time (no buffering)
3. Accumulates chunks in memory for logging
4. Parses and logs the complete response after streaming completes
5. Automatically detects and handles both SSE formats

### Testing Streaming

Run the test script to verify streaming functionality:
```bash
uv run python test_streaming.py
```

## Logs

Logs are written to `./logs/requests_YYYYMMDD.jsonl` in JSON Lines format.

Each log entry contains:
- Timestamp (UTC)
- Request method, path, headers, body
- Response status, headers, body
- For streaming responses: parsed and aggregated message content
- Sensitive headers (authorization, api-key) are redacted

## Health Check

Visit `http://127.0.0.1:58734/` to verify the proxy is running.

## Analysis Tools

### Entity Extraction with Agent Tracking

Extract all entities from logs with agent instance tracking and deduplication:

```bash
python3 -m analysis.extract_all_entities \
    proxy/logs/requests_20260110.jsonl \
    -o proxy/logs/entities_with_tracking.json
```

**Features**:
- **Agent Instance Tracking**: Identifies individual agent instances across requests
- **Entity Deduplication**: Removes duplicate tool definitions, system prompts, etc.
- **Conversation Evolution**: Tracks how conversations evolve
- **Parent-Child Relationships**: Links spawned subagents to parent agents

**Output includes**:
- Agent instances with conversation fingerprints
- Deduplicated entities (tools, prompts, tasks)
- Agent hierarchy and relationships
- Workflow DAG with spawn and tool result edges
- Comprehensive statistics

See [docs/AGENT_WORKFLOW_TRACKING.md](../docs/AGENT_WORKFLOW_TRACKING.md) for detailed documentation.

### React-Based Viewer

Start the viewer to explore logs interactively:

```bash
# Terminal 1: Start log API server
uv run python log_api.py

# Terminal 2: Start React viewer
cd viewer
pnpm dev
```

Open `http://localhost:58735` to access:
- **Timeline Panel**: Chronological request visualization
- **Stats Panel**: Workflow metrics overview
- **Workflow Panel**: D3.js force-directed graph with spawn/tool edges
- **Agent Gantt Panel**: Timeline view with spawn arrows

### Standalone HTML Viewer

For offline viewing, open `viewer/workflow_tree_viz.html` and load an entities JSON file.

### Other Analysis Scripts

- `../scripts/analyze_system_prompts.py`: Analyze system prompt patterns
- `../scripts/extract_all_tools.py`: Extract tool definitions

