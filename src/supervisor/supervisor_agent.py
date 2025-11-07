"""Multi-agent supervisor for coordinating research across multiple specialized agents.

This module implements a supervisor pattern where:
1. A supervisor agent coordinates research activities and delegates tasks
2. Multiple researcher agents work on specific sub-topics independently
3. Results are aggregated and compressed for final reporting

The supervisor uses parallel research execution to improve efficiency while
maintaining isolated context windows for each research topic.
"""

import asyncio
import traceback
import sys

from typing_extensions import Literal
from alive_progress import alive_bar

from langchain.chat_models import init_chat_model
from langchain_core.messages import (
    HumanMessage, 
    BaseMessage, 
    SystemMessage, 
    ToolMessage,
    filter_messages
)
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from supervisor.supervisor_prompts import lead_researcher_prompt
from supervisor.supervisor_state import (
    SupervisorState, 
    ConductResearch, 
    ResearchComplete
)

from research.research_agent import researcher_agent
from research.research_state import think_tool

from utils.today import get_today_str
from utils.initialize_model import initialize_model

from LLM_models.LLM_models import SUPERVISOR_MODEL_NAME, SUPERVISOR_MODEL_PROVIDER, SUPERVISOR_MODEL_TEMPERATURE, SUPERVISOR_MODEL_BASE_URL, SUPERVISOR_MODEL_PROVIDER_API_KEY, SUPERVISOR_MODEL_MAX_TOKENS

from utils.message_utils import format_messages

def get_notes_from_tool_calls(messages: list[BaseMessage]) -> list[str]:
    """Extract research notes from ToolMessage objects in supervisor message history.
    
    This function retrieves the compressed research findings that sub-agents
    return as ToolMessage content. When the supervisor delegates research to
    sub-agents via ConductResearch tool calls, each sub-agent returns its
    compressed findings as the content of a ToolMessage. This function
    extracts all such ToolMessage content to compile the final research notes.
    
    Args:
        messages: List of messages from supervisor's conversation history
        
    Returns:
        List of research note strings extracted from ToolMessage objects
    """
    
    try:
        return [tool_msg.content for tool_msg in filter_messages(messages, include_types="tool")]
    
    except Exception as e:
        # Get the traceback information
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno
        
        # Print detailed error information
        print(f"\n❌ Error in get_notes_from_tool_calls function:")
        print(f"   Line number: {line_number}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"\n   Full traceback:")
        traceback.print_exc()
        
        # Re-raise the exception to let the caller handle it
        raise

# ===== CONFIGURATION =====

supervisor_tools = [ConductResearch, ResearchComplete, think_tool]
supervisor_model = initialize_model(
    model_name=SUPERVISOR_MODEL_NAME,
    model_provider=SUPERVISOR_MODEL_PROVIDER,
    base_url=SUPERVISOR_MODEL_BASE_URL,
    temperature=SUPERVISOR_MODEL_TEMPERATURE,
    api_key=SUPERVISOR_MODEL_PROVIDER_API_KEY,
    max_tokens=SUPERVISOR_MODEL_MAX_TOKENS
)
supervisor_model_with_tools = supervisor_model.bind_tools(supervisor_tools)

# System constants
# Maximum number of tool call iterations for individual researcher agents
# This prevents infinite loops and controls research depth per topic
max_researcher_iterations = 6 # Calls to think_tool + ConductResearch

# Maximum number of concurrent research agents the supervisor can launch
# This is passed to the lead_researcher_prompt to limit parallel research tasks
max_concurrent_researchers = 3

# ===== SUPERVISOR NODES =====

async def supervisor(state: SupervisorState) -> Command[Literal["supervisor_tools"]]:
    """Coordinate research activities.
    
    Analyzes the research brief and current progress to decide:
    - What research topics need investigation
    - Whether to conduct parallel research
    - When research is complete
    
    Args:
        state: Current supervisor state with messages and research progress
        
    Returns:
        Command to proceed to supervisor_tools node with updated state
    """
    
    try:
        supervisor_messages = state.get("supervisor_messages", [])
        
        # Prepare system message with current date and constraints
        system_message = lead_researcher_prompt.format(
            date=get_today_str(), 
            max_concurrent_research_units=max_concurrent_researchers,
            max_researcher_iterations=max_researcher_iterations
        )
        messages = [SystemMessage(content=system_message)] + supervisor_messages
        
        # Make decision about next research steps
        print("⏳ Supervisor agent:")
        with alive_bar(monitor=False, stats=False, title="", spinner='dots_waves', bar='blocks') as bar:
            response = await supervisor_model_with_tools.ainvoke(messages)
            bar()
        
        # Format and display the supervisor messages
        if response.tool_calls is not None:
            response_tool_calls_name = response.tool_calls[0].get('name')
            if response_tool_calls_name == "think_tool":
                title = "Supervisor Agent tools - Call to think tool"
            elif response_tool_calls_name == "ConductResearch":
                title = "Supervisor Agent tools - Call to Conduct Research"
            else:
                title = "Supervisor Agent tools - Tool Calls"
            format_messages([response], title=title)
        else:
            format_messages([response], title="Supervisor Agent")
        
        # Increment research iterations if conduct research tool call is present
        research_iterations = state.get("research_iterations", 0)
        if response.tool_calls is not None:
            response_tool_calls_name = response.tool_calls[0].get('name')
            if response_tool_calls_name == "ConductResearch":
                research_iterations += 1
        
        return Command(
            goto="supervisor_tools",
            update={
                "supervisor_messages": [response],
                "research_iterations": research_iterations
            }
        )
    
    except Exception as e:
        # Get the traceback information
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno
        
        # Print detailed error information
        print(f"\n❌ Error in supervisor function:")
        print(f"   Line number: {line_number}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"\n   Full traceback:")
        traceback.print_exc()
        
        # Re-raise the exception to let the caller handle it
        raise

async def supervisor_tools(state: SupervisorState) -> Command[Literal["supervisor", "__end__"]]:
    """Execute supervisor decisions - either conduct research or end the process.
    
    Handles:
    - Executing think_tool calls for strategic reflection
    - Launching parallel research agents for different topics
    - Aggregating research results
    - Determining when research is complete
    
    Args:
        state: Current supervisor state with messages and iteration count
        
    Returns:
        Command to continue supervision, end process, or handle errors
    """
    
    try:
        supervisor_messages = state.get("supervisor_messages", [])
        research_iterations = state.get("research_iterations", 0)
        most_recent_message = supervisor_messages[-1]
        # Create a System message to show supervisor messages and research iterations
        system_message = SystemMessage(
            content=f"Research iterations: {research_iterations}"
        )
        format_messages([system_message], title="Supervisor Agent tools - Research iterations")
        
        # Initialize variables for single return pattern
        tool_messages = []
        all_raw_notes = []
        next_step = "supervisor"  # Default next step
        should_end = False
        
        # Check exit criteria first
        exceeded_iterations = research_iterations >= max_researcher_iterations
        no_tool_calls = not most_recent_message.tool_calls
        research_complete = any(
            tool_call["name"] == "ResearchComplete" 
            for tool_call in most_recent_message.tool_calls
        )
        
        if exceeded_iterations or no_tool_calls or research_complete:
            # Create a System message to show the decision
            system_message = SystemMessage(
                content=f"Exceeded iterations or no tool calls or research complete. Ending supervisor... Research iterations: {research_iterations} and supervisor messages: {supervisor_messages}"
            )
            termination_message_info = ""
            if exceeded_iterations:
                termination_message_info += f" Exceeded iterations"
            if no_tool_calls:
                termination_message_info += f" No tool calls"
            if research_complete:
                termination_message_info += f" Research complete"
            format_messages([system_message], title=termination_message_info)
            should_end = True
            next_step = END
        
        else:
            # Execute ALL tool calls before deciding next step
            try:
                # Separate think_tool calls from ConductResearch calls
                think_tool_calls = [
                    tool_call for tool_call in most_recent_message.tool_calls if tool_call["name"] == "think_tool"
                ]
                
                conduct_research_calls = [
                    tool_call for tool_call in most_recent_message.tool_calls if tool_call["name"] == "ConductResearch"
                ]

                # Handle think_tool calls (synchronous)
                for tool_call in think_tool_calls:
                    observation = think_tool.invoke(tool_call["args"])
                    tool_message = ToolMessage(
                        content=observation,
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"]
                    )
                    format_messages([tool_message], title="Supervisor Agent - think tool result")
                    tool_messages.append(tool_message)

                # Handle ConductResearch calls (asynchronous)
                if conduct_research_calls:
                    # Launch parallel research agents
                    coros = [
                        researcher_agent.ainvoke({
                            "researcher_messages": [
                                HumanMessage(content=tool_call["args"]["research_topic"])
                            ],
                            "research_topic": tool_call["args"]["research_topic"]
                        }) 
                        for tool_call in conduct_research_calls
                    ]

                    # Wait for all research to complete
                    tool_results = await asyncio.gather(*coros)

                    # Format research results as tool messages
                    # Each sub-agent returns compressed research findings in result["compressed_research"]
                    # We write this compressed research as the content of a ToolMessage, which allows
                    # the supervisor to later retrieve these findings via get_notes_from_tool_calls()
                    research_tool_messages = [
                        ToolMessage(
                            content=result.get("compressed_research", "Error synthesizing research report"),
                            name=tool_call["name"],
                            tool_call_id=tool_call["id"]
                        ) for result, tool_call in zip(tool_results, conduct_research_calls)
                    ]
                    
                    tool_messages.extend(research_tool_messages)

                    # Aggregate raw notes from all research
                    all_raw_notes = [
                        "\n".join(result.get("raw_notes", [])) for result in tool_results
                    ]
                    
            except Exception as e:
                # Get the traceback information for inner exception
                exc_type, exc_obj, exc_tb = sys.exc_info()
                line_number = exc_tb.tb_lineno
                
                # Print detailed error information
                print(f"\n❌ Error executing tool calls in supervisor_tools function:")
                print(f"   Line number: {line_number}")
                print(f"   Error type: {type(e).__name__}")
                print(f"   Error message: {str(e)}")
                print(f"\n   Full traceback:")
                traceback.print_exc()
                
                should_end = True
                next_step = END
        
        # Single return point with appropriate state updates
        if should_end:
            return Command(
                goto=next_step,
                update={
                    "notes": get_notes_from_tool_calls(supervisor_messages),
                    "research_brief": state.get("research_brief", "")
                }
            )
        else:
            return Command(
                goto=next_step,
                update={
                    "supervisor_messages": tool_messages,
                    "raw_notes": all_raw_notes
                }
            )
    
    except Exception as e:
        # Get the traceback information for outer exception
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno
        
        # Print detailed error information
        print(f"\n❌ Error in supervisor_tools function:")
        print(f"   Line number: {line_number}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"\n   Full traceback:")
        traceback.print_exc()
        
        # Re-raise the exception to let the caller handle it
        raise

# ===== GRAPH CONSTRUCTION =====

# Build supervisor graph
supervisor_builder = StateGraph(SupervisorState)
supervisor_builder.add_node("supervisor", supervisor)
supervisor_builder.add_node("supervisor_tools", supervisor_tools)
supervisor_builder.add_edge(START, "supervisor")
supervisor_agent = supervisor_builder.compile()