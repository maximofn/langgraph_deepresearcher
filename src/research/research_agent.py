"""
Research Agent Implementation.

This module implements a research agent that can perform iterative web searches
and synthesis to answer complex research questions.
"""

from typing_extensions import Literal
import traceback
import sys

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, ToolCall, filter_messages
from langchain.chat_models import init_chat_model

from research.research_state import ResearcherState, ResearcherOutputState, tavily_search, think_tool
from utils.today import get_today_str
from utils.message_utils import format_messages
from utils.initialize_model import initialize_model
from utils.progress_bar import safe_progress_bar
from research.research_prompts import research_agent_prompt, compress_research_system_prompt, compress_research_human_message

from LLM_models.LLM_models import RESEARCH_MODEL_NAME, RESEARCH_MODEL_PROVIDER, RESEARCH_MODEL_TEMPERATURE, RESEARCH_MODEL_BASE_URL, RESEARCH_MODEL_PROVIDER_API_KEY, RESEARCH_MODEL_MAX_TOKENS
from LLM_models.LLM_models import COMPRESS_MODEL_NAME, COMPRESS_MODEL_PROVIDER, COMPRESS_MODEL_TEMPERATURE, COMPRESS_MODEL_BASE_URL, COMPRESS_MODEL_PROVIDER_API_KEY, COMPRESS_MODEL_MAX_TOKENS

# ===== CONFIGURATION =====

# Set up tools and model binding
tools = [tavily_search, think_tool]
tools_by_name = {tool.name: tool for tool in tools}

# Initialize models
research_model = initialize_model(
    model_name=RESEARCH_MODEL_NAME,
    model_provider=RESEARCH_MODEL_PROVIDER,
    base_url=RESEARCH_MODEL_BASE_URL,
    temperature=RESEARCH_MODEL_TEMPERATURE,
    api_key=RESEARCH_MODEL_PROVIDER_API_KEY,
    max_tokens=RESEARCH_MODEL_MAX_TOKENS
)
research_model_with_tools = research_model.bind_tools(tools)
compress_model = initialize_model(
    model_name=COMPRESS_MODEL_NAME, 
    model_provider=COMPRESS_MODEL_PROVIDER, 
    base_url=COMPRESS_MODEL_BASE_URL, 
    temperature=COMPRESS_MODEL_TEMPERATURE,
    api_key=COMPRESS_MODEL_PROVIDER_API_KEY,
    max_tokens=COMPRESS_MODEL_MAX_TOKENS
)

# ===== AGENT NODES =====

def llm_call(state: ResearcherState):
    """Analyze current state and decide on next actions.
    
    The model analyzes the current conversation state and decides whether to:
    1. Call search tools to gather more information
    2. Provide a final answer based on gathered information
    
    Returns updated state with the model's response.
    """
    
    try:
        # Show progress bar while waiting for LLM response
        print("⏳ Researcher agent:")
        if isinstance(state.get('researcher_messages', [])[-1], HumanMessage):
            format_messages([state.get("researcher_messages", [])[-1]], title="Researcher Agent - Simulated Human Message")
        with safe_progress_bar(monitor=False, stats=False, title="", spinner='dots_waves', bar='blocks') as bar:
            research_messages = research_model_with_tools.invoke(
                [SystemMessage(content=research_agent_prompt)] + state["researcher_messages"]
            )
            bar()  # Complete the progress bar
        
        # Format and display the research messages
        format_messages([research_messages], title="Researcher Agent response")

        # Return the research messages
        return {
            "researcher_messages": [
                research_messages
            ]
        }
    except Exception as e:
        # Get the traceback information
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno
        
        # Print detailed error information
        print(f"\n❌ Error in llm_call function:")
        print(f"   Line number: {line_number}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"\n   Full traceback:")
        traceback.print_exc()
        
        # Re-raise the exception to let the caller handle it
        raise

def tool_node(state: ResearcherState):
    """Execute all tool calls from the previous LLM response.
    
    Executes all tool calls from the previous LLM responses.
    Returns updated state with tool execution results.
    """

    try:
        # Get the tool calls
        tool_calls = state["researcher_messages"][-1].tool_calls

        # Format the tool calls
        format_messages([ToolCall(
            name="Tool Calls",
            args=tool_calls,
            id="tool_call_id"
        )], title="Researcher Agent - Tool calls")
     
        # Execute all tool calls
        observations = []
        for tool_call in tool_calls:
            with safe_progress_bar(monitor=False, stats=False, title=f"", spinner='dots_waves', bar='blocks') as bar:
                tool = tools_by_name[tool_call["name"]]
                observation = tool.invoke(tool_call["args"])
                observations.append(observation)
                bar()
            
            # Format and display the result immediately
            format_messages([ToolMessage(
                content=observation,
                name=tool_call["name"],
                tool_call_id=tool_call["id"]
            )], title="Researcher Agent - Tool calls result")

        # Create tool message outputs
        tool_outputs = [
            ToolMessage(
                content=observation,
                name=tool_call["name"],
                tool_call_id=tool_call["id"]
            ) for observation, tool_call in zip(observations, tool_calls)
        ]

        # Return the tool outputs
        return {"researcher_messages": tool_outputs}
    
    except Exception as e:
        # Get the traceback information
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno
        
        # Print detailed error information
        print(f"\n❌ Error in tool_node function:")
        print(f"   Line number: {line_number}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"\n   Full traceback:")
        traceback.print_exc()
        
        # Re-raise the exception to let the caller handle it
        raise

def compress_research(state: ResearcherState) -> dict:
    """Compress research findings into a concise summary.
    
    Takes all the research messages and tool outputs and creates
    a compressed summary suitable for the supervisor's decision-making.
    """
    
    try:
        system_message = compress_research_system_prompt.format(date=get_today_str())
        messages = [SystemMessage(content=system_message)] + state.get("researcher_messages", []) + [HumanMessage(content=compress_research_human_message)]

        print("⏳ Compressing Research:")
        with safe_progress_bar(monitor=False, stats=False, title="", spinner='dots_waves', bar='blocks') as bar:
            response = compress_model.invoke(messages)
            bar()
        
        # Format and display the compressed research
        format_messages([response], title="Researcher Agent - Compressed Research")

        # Extract raw notes from tool and AI messages
        raw_notes = [
            str(m.content) for m in filter_messages(
                state["researcher_messages"], 
                include_types=["tool", "ai"]
            )
        ]

        # Return the compressed research and raw notes
        return {
            "compressed_research": str(response.content),
            "raw_notes": ["\n".join(raw_notes)]
        }
    
    except Exception as e:
        # Get the traceback information
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno
        
        # Print detailed error information
        print(f"\n❌ Error in compress_research function:")
        print(f"   Line number: {line_number}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"\n   Full traceback:")
        traceback.print_exc()
        
        # Re-raise the exception to let the caller handle it
        raise

# ===== ROUTING LOGIC =====

def should_continue(state: ResearcherState) -> Literal["tool_node", "compress_research"]:
    """Determine whether to continue research or provide final answer.
    
    Determines whether the agent should continue the research loop or provide
    a final answer based on whether the LLM made tool calls.
    
    Returns:
        "tool_node": Continue to tool execution
        "compress_research": Stop and compress research
    """
    
    try:
        messages = state["researcher_messages"]
        last_message = messages[-1]
        
        # If the LLM makes a tool call, continue to tool execution
        if last_message.tool_calls:
            # Create a System message to show the decision
            decision_message = SystemMessage(
                content="Last message contains tool calls. Continuing to tool execution..."
            )
            format_messages([decision_message], title="Researcher Agent - Should continue")
            return "tool_node"
        # Otherwise, we have a final answer
        else:
            # Create a System message to show the decision
            decision_message = SystemMessage(
                content="No tool calls found. Stopping research and compressing findings..."
            )
            format_messages([decision_message], title="Researcher Agent - Should compress research")
            return "compress_research"
    
    except Exception as e:
        # Get the traceback information
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno
        
        # Print detailed error information
        print(f"\n❌ Error in should_continue function:")
        print(f"   Line number: {line_number}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"\n   Full traceback:")
        traceback.print_exc()
        
        # Re-raise the exception to let the caller handle it
        raise

# ===== GRAPH CONSTRUCTION =====

# Build the agent workflow
agent_builder = StateGraph(ResearcherState, output_schema=ResearcherOutputState)

# Add nodes to the graph
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)
agent_builder.add_node("compress_research", compress_research)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        "tool_node": "tool_node", # Continue research loop
        "compress_research": "compress_research", # Provide final answer
    },
)
agent_builder.add_edge("tool_node", "llm_call") # Loop back for more research
agent_builder.add_edge("compress_research", END)

# Compile the agent
researcher_agent = agent_builder.compile()