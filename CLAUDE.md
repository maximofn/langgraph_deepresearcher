# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LangGraph Deep Researcher is a multi-agent research system that uses LangGraph to coordinate specialized AI agents for conducting deep research on complex topics. The system employs a supervisor pattern where a lead researcher coordinates multiple sub-agents that work on specific research topics in parallel.

## Common Commands

### Running the Application
```bash
# Run the main research workflow
python src/langgraph_deepresearch.py

# Run tests
python test/test_agent_research.py
python test/test_agent_scope.py
```

### Environment Setup
```bash
# Install dependencies using uv
uv sync

# Activate virtual environment
source .venv/bin/activate
```

### Required Environment Variables
The following API keys must be set in a `.env` file:
- `OPENAI_API_KEY` - For OpenAI models
- `ANTHROPIC_API_KEY` - For Claude models
- `GITHUB_API_KEY` - For GitHub Models API
- `CEREBRAS_API_KEY` - For Cerebras models
- `TAVILY_API_KEY` - For web search functionality
- `LANGSMITH_API_KEY` - For LangSmith tracing and evaluation

## Architecture

### Multi-Agent Workflow Pipeline

The system follows a sequential pipeline with four main phases:

1. **Scope Agent** ([scope_agent.py](src/scope/scope_agent.py))
   - Entry point for user requests
   - Determines if clarification is needed from the user
   - Generates a comprehensive research brief from the conversation
   - Uses structured output (`ClarifyWithUser`, `ResearchQuestion`) for deterministic decisions

2. **Supervisor Agent** ([supervisor_agent.py](src/supervisor/supervisor_agent.py))
   - Coordinates research activities across multiple sub-agents
   - Breaks down the research brief into parallel research topics
   - Launches up to `max_concurrent_researchers` (default: 3) research agents in parallel
   - Aggregates compressed research findings from all sub-agents
   - Maximum iterations: `max_researcher_iterations` (default: 6)

3. **Research Agents** ([research_agent.py](src/research/research_agent.py) or [research_mcp_agent.py](src/research_mcp/research_mcp_agent.py))
   - Execute iterative research on assigned topics
   - Two implementations:
     - Standard: Uses Tavily search for web research
     - MCP-enabled: Uses Model Context Protocol for local filesystem research
   - Compresses findings before returning to supervisor
   - Each agent has isolated context and works independently

4. **Writer Agent** ([write_agent.py](src/write/write_agent.py))
   - Integrates the entire workflow: scope → research → report generation
   - Synthesizes all research findings into a comprehensive final report
   - Uses `final_report_generation_prompt` to format findings into a cohesive document
   - Compiles all phases (clarify_with_user, write_research_brief, supervisor_subgraph, final_report_generation) into a single graph

### State Management

Each agent maintains its own state schema:

- **AgentState** (Scope): `messages`, `research_brief`, `supervisor_messages`
- **SupervisorState**: `supervisor_messages`, `research_iterations`, `raw_notes`, `notes`
- **ResearcherState**: `researcher_messages`, `research_topic`, `compressed_research`, `raw_notes`

State is passed between agents through specific fields (e.g., `research_brief` → `supervisor_messages`).

### Model Configuration

Model assignments are centralized in [LLM_models.py](src/LLM_models/LLM_models.py):

- **Scope Agent**: OpenAI GPT-4.1 (clarification and brief generation)
- **Research Agent**: Claude Sonnet 4.5 (tool calling and research, 4096 max tokens)
- **Supervisor Agent**: Claude Sonnet 4.5 (coordination and delegation, 4096 max tokens)
- **Compression**: OpenAI GPT-4.1 (summarization with 32K max tokens)
- **Writer Agent**: OpenAI GPT-4.1 (final report generation, 32K max tokens)

Models can be easily swapped by changing the constants in this file.

### MCP Integration

The system supports Model Context Protocol (MCP) for local filesystem research:

- Configuration in [research_mcp_agent.py](src/research_mcp/research_mcp_agent.py)
- Uses `@modelcontextprotocol/server-filesystem` via npx
- Requires async operations due to inter-process communication
- Lazy client initialization for LangGraph Platform compatibility
- Accessed via `get_mcp_client()` function

To enable MCP mode, set `MCP = True` in [langgraph_deepresearch.py](src/langgraph_deepresearch.py) and use `agent_builder_mcp` instead of `agent_builder`.

### Key Tools

- **tavily_search**: Web search for gathering research information
- **think_tool**: Internal reasoning tool for strategic planning
- **ConductResearch**: Supervisor tool to delegate research to sub-agents
- **ResearchComplete**: Supervisor tool to signal research completion

## Development Workflow

### Adding a New Agent

1. Create state schema in `src/{agent_name}/{agent_name}_state.py`
2. Define prompts in `src/{agent_name}/{agent_name}_prompts.py`
3. Implement agent logic in `src/{agent_name}/{agent_name}_agent.py`:
   - Define node functions
   - Create routing logic
   - Build StateGraph
   - Compile with optional checkpointer
4. Integrate into main workflow in [langgraph_deepresearch.py](src/langgraph_deepresearch.py)

### Debugging Graphs

Use flags in [debug.py](src/debug.py) to visualize agent graphs:
```python
PRINT_SCOPE_GRAPH = True      # Print ASCII graph to console
SAVE_SCOPE_GRAPH = True       # Save Mermaid PNG diagram
PRINT_RESEARCH_GRAPH = True
SAVE_RESEARCH_GRAPH = True
PRINT_SUPERVISOR_GRAPH = True
SAVE_SUPERVISOR_GRAPH = True
PRINT_WRITER_GRAPH = True
SAVE_WRITER_GRAPH = True
```

### Testing with LangSmith

The project uses LangSmith for evaluation:
- Test datasets defined in `test/dataset/`
- Evaluation scripts in `test/test_agent_*.py`
- Creates datasets for testing agent decision-making (e.g., when to continue vs. stop research)

## Important Patterns

### Error Handling
All agent functions include comprehensive try-catch blocks that:
- Capture line numbers and error types
- Print full tracebacks
- Re-raise exceptions for caller handling

### Progress Indicators
The system uses `alive_bar` for visual feedback during LLM calls and tool executions.

### Message Formatting
Use `format_messages()` from [message_utils.py](src/utils/message_utils.py) for consistent console output with titles and message type indicators.

### Async Operations
- Supervisor uses `asyncio.gather()` for parallel research agent execution
- MCP agents require async throughout due to protocol requirements
- Main entry point uses `asyncio.run(main())` when async agents are involved

## Notes

- The main workflow in [langgraph_deepresearch.py](src/langgraph_deepresearch.py) currently tests individual agents with hardcoded research briefs. The full integrated workflow is in [write_agent.py](src/write/write_agent.py)
- Each agent can be compiled with an `InMemorySaver` checkpointer for state persistence
- Thread configuration uses `{"configurable": {"thread_id": "1"}}` for conversation continuity
- The supervisor enforces limits on concurrent researchers and total iterations to prevent runaway research
- The system is fully async-compatible for MCP integration, using `asyncio.run(main())` as the entry point
