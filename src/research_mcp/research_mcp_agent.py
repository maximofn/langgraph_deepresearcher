"""Research Agent with MCP Integration.

This module implements a research agent that integrates with Model Context Protocol (MCP)
servers to access tools and resources. The agent demonstrates how to use MCP filesystem
server for local document research and analysis.

Key features:
- MCP server integration for tool access
- Async operations for concurrent tool execution (required by MCP protocol)
- Filesystem operations for local document research
- Secure directory access with permission checking
- Research compression for efficient processing
- Lazy MCP client initialization for LangGraph Platform compatibility
"""

import os

from typing_extensions import Literal

from alive_progress import alive_bar

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, ToolCall, filter_messages
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END

from research_mcp.research_mcp_promtps import research_agent_prompt_with_mcp
from research.research_state import ResearcherState, ResearcherOutputState, think_tool
from research_mcp.research_mcp_utils import get_current_dir

from research.research_prompts import compress_research_system_prompt, compress_research_human_message

from utils.today import get_today_str
from utils.message_utils import format_messages

from LLM_models.LLM_models import RESEARCH_MODEL_NAME, RESEARCH_MODEL_PROVIDER, RESEARCH_MODEL_TEMPERATURE, RESEARCH_MODEL_BASE_URL, RESEARCH_MODEL_PROVIDER_API_KEY
from LLM_models.LLM_models import COMPRESS_MODEL_NAME, COMPRESS_MODEL_PROVIDER, COMPRESS_MODEL_TEMPERATURE, COMPRESS_MODEL_BASE_URL, COMPRESS_MODEL_PROVIDER_API_KEY

# ===== CONFIGURATION =====

# MCP server configuration for filesystem access
mcp_config = {
    "filesystem": {
        "command": "npx",
        "args": [
            "-y",  # Auto-install if needed
            "@modelcontextprotocol/server-filesystem",
            str(get_current_dir() / "files")  # Path to research documents
        ],
        "transport": "stdio"  # Communication via stdin/stdout
    }
}

# Global client variable - will be initialized lazily
_client = None

def get_mcp_client():
    """Get or initialize MCP client lazily to avoid issues with LangGraph Platform."""
    global _client
    if _client is None:
        _client = MultiServerMCPClient(mcp_config)
    return _client

# Initialize models
compress_model = init_chat_model(
    model=COMPRESS_MODEL_NAME, 
    model_provider=COMPRESS_MODEL_PROVIDER, 
    api_key=COMPRESS_MODEL_PROVIDER_API_KEY,
    base_url=COMPRESS_MODEL_BASE_URL, 
    temperature=COMPRESS_MODEL_TEMPERATURE,
    max_tokens=32000
)
model = init_chat_model(
    model=RESEARCH_MODEL_NAME
)

# ===== AGENT NODES =====

async def llm_call(state: ResearcherState):
    """Analyze current state and decide on tool usage with MCP integration.

    This node:
    1. Retrieves available tools from MCP server
    2. Binds tools to the language model
    3. Processes user input and decides on tool usage

    Returns updated state with model response.
    """
    
    # Get available tools from MCP server
    client = get_mcp_client()
    mcp_tools = await client.get_tools()

    # Use MCP tools for local document access
    tools = mcp_tools + [think_tool]

    # Initialize model with tool binding
    model_with_tools = model.bind_tools(tools)
    
    # Show progress bar while waiting for LLM response
    print("⏳ MCP Researcher agent:")
    format_messages([state.get("researcher_messages", [])[-1]])
    with alive_bar(monitor=False, stats=False, title="", spinner='dots_waves', bar='blocks') as bar:
        research_messages = model_with_tools.invoke(
            [SystemMessage(content=research_agent_prompt_with_mcp.format(date=get_today_str()))] + state["researcher_messages"]
        )
        bar()  # Complete the progress bar
    
    # Format and display the research messages
    format_messages([research_messages])

    # Process user input with system prompt
    return {
        "researcher_messages": [
            research_messages
        ]
    }

async def tool_node(state: ResearcherState):
    """Execute tool calls using MCP tools.

    This node:
    1. Retrieves current tool calls from the last message
    2. Executes all tool calls using async operations (required for MCP)
    3. Returns formatted tool results

    Note: MCP requires async operations due to inter-process communication
    with the MCP server subprocess. This is unavoidable.
    """

    # Get the tool calls
    tool_calls = state["researcher_messages"][-1].tool_calls

    # Format the tool calls
    format_messages([ToolCall(
        name="Tool Calls",
        args=tool_calls,
        id="tool_call_id"
    )])

    async def execute_tools():
        """Execute all tool calls. MCP tools require async execution."""
        # Get fresh tool references from MCP server
        client = get_mcp_client()
        mcp_tools = await client.get_tools()
        tools = mcp_tools + [think_tool]
        tools_by_name = {tool.name: tool for tool in tools}

        # Execute tool calls (sequentially for reliability)
        observations = []
        for tool_call in tool_calls:
            print(f"⏳ Executing Tool Call: {tool_call['name']} - {tool_call['args']}")
            with alive_bar(monitor=False, stats=False, title=f"", spinner='dots_waves', bar='blocks') as bar:
                tool = tools_by_name[tool_call["name"]]
                if tool_call["name"] == "think_tool":
                    # think_tool is sync, use regular invoke
                    observation = tool.invoke(tool_call["args"])
                else:
                    # MCP tools are async, use ainvoke
                    observation = await tool.ainvoke(tool_call["args"])
                observations.append(observation)
            bar()
        
            # Format and display the result immediately
            format_messages([ToolMessage(
                content=observation,
                name=tool_call["name"],
                tool_call_id=tool_call["id"]
            )])

        # Format results as tool messages
        tool_outputs = [
            ToolMessage(
                content=observation,
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
            for observation, tool_call in zip(observations, tool_calls)
        ]

        return tool_outputs

    messages = await execute_tools()

    return {"researcher_messages": messages}

def compress_research(state: ResearcherState) -> dict:
    """Compress research findings into a concise summary.

    Takes all the research messages and tool outputs and creates
    a compressed summary suitable for further processing or reporting.

    This function filters out think_tool calls and focuses on substantive
    file-based research content from MCP tools.
    """
    
    system_message = compress_research_system_prompt.format(date=get_today_str())
    messages = [SystemMessage(content=system_message)] + state.get("researcher_messages", []) + [HumanMessage(content=compress_research_human_message)]

    print("⏳ Compressing Research:")
    with alive_bar(monitor=False, stats=False, title="", spinner='dots_waves', bar='blocks') as bar:
        response = compress_model.invoke(messages)
        bar()
    
    # Format and display the compressed research
    format_messages([response])

    # Extract raw notes from tool and AI messages
    raw_notes = [
        str(m.content) for m in filter_messages(
            state["researcher_messages"], 
            include_types=["tool", "ai"]
        )
    ]

    return {
        "compressed_research": str(response.content),
        "raw_notes": ["\n".join(raw_notes)]
    }

# ===== ROUTING LOGIC =====

def should_continue(state: ResearcherState) -> Literal["tool_node", "compress_research"]:
    """Determine whether to continue with tool execution or compress research.

    Determines whether to continue with tool execution or compress research
    based on whether the LLM made tool calls.
    """
    messages = state["researcher_messages"]
    last_message = messages[-1]

    # Continue to tool execution if tools were called
    if last_message.tool_calls:
        # Create a System message to show the decision
        decision_message = SystemMessage(
            content="Last message contains tool calls. Continuing to tool execution..."
        )
        format_messages([decision_message])
        return "tool_node"
    # Otherwise, compress research findings
    else:
        # Create a System message to show the decision
        decision_message = SystemMessage(
            content="No tool calls found. Stopping research and compressing findings..."
        )
        format_messages([decision_message])
        return "compress_research"

# ===== GRAPH CONSTRUCTION =====

# Build the agent workflow
agent_builder_mcp = StateGraph(ResearcherState, output_schema=ResearcherOutputState)

# Add nodes to the graph
agent_builder_mcp.add_node("llm_call", llm_call)
agent_builder_mcp.add_node("tool_node", tool_node)
agent_builder_mcp.add_node("compress_research", compress_research)

# Add edges to connect nodes
agent_builder_mcp.add_edge(START, "llm_call")
agent_builder_mcp.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        "tool_node": "tool_node",        # Continue to tool execution
        "compress_research": "compress_research",  # Compress research findings
    },
)
agent_builder_mcp.add_edge("tool_node", "llm_call")  # Loop back for more processing
agent_builder_mcp.add_edge("compress_research", END)

# Compile the agent
agent_mcp = agent_builder_mcp.compile()