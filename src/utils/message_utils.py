from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import json
import ast

console = Console()

def format_tool_outputs(tool_outputs_list: list) -> str:
    """Format a list of ToolMessage objects into a readable string"""
    formatted_parts = []
    
    for i, output in enumerate(tool_outputs_list, 1):
        # Handle ToolMessage objects that have been converted to strings
        if isinstance(output, dict):
            formatted_parts.append(f"\n  Tool Output {i}:")
            formatted_parts.append(f"    Name: {output.get('name', 'N/A')}")
            formatted_parts.append(f"    Tool Call ID: {output.get('tool_call_id', 'N/A')}")
            
            # Format the content (which contains the actual output)
            content = output.get('content', 'N/A')
            if isinstance(content, str):
                # Truncate very long outputs
                if len(content) > 500:
                    content_preview = content[:500] + f"... ({len(content)} chars total)"
                else:
                    content_preview = content
                formatted_parts.append(f"    Content:")
                # Indent each line of content
                for line in content_preview.split('\n'):
                    formatted_parts.append(f"      {line}")
            else:
                formatted_parts.append(f"    Content: {content}")
        else:
            formatted_parts.append(f"\n  Tool Output {i}: {output}")
    
    return "\n".join(formatted_parts)


def format_string_with_structures(content: str) -> str:
    """
    Detect and format structured data (lists, dicts) within a string.
    Handles cases like 'Tool calls: [...]' and 'Tool outputs: [...]' by parsing and formatting the structure.
    """
    # Check if the string contains 'Tool outputs:' followed by a list
    if 'Tool outputs:' in content:
        try:
            # Find the position where the tool outputs list starts
            tool_outputs_index = content.index('Tool outputs:')
            prefix = content[:tool_outputs_index + len('Tool outputs:')]
            
            # Extract the part that should be a list
            potential_list = content[tool_outputs_index + len('Tool outputs:'):].strip()
            
            # Try to parse it as a Python literal (list/dict)
            parsed_data = ast.literal_eval(potential_list)
            
            # If it's a list of tool outputs, format them nicely
            if isinstance(parsed_data, list):
                formatted_parts = [prefix + "\n"]
                formatted_parts.append(format_tool_outputs(parsed_data))
                return "\n".join(formatted_parts)
        except (ValueError, SyntaxError):
            # If parsing fails, continue to next check
            pass
    
    # Check if the string contains 'Tool calls:' followed by a list
    if 'Tool calls:' in content:
        try:
            # Find the position where the tool calls list starts
            tool_calls_index = content.index('Tool calls:')
            prefix = content[:tool_calls_index + len('Tool calls:')]
            
            # Extract the part that should be a list
            potential_list = content[tool_calls_index + len('Tool calls:'):].strip()
            
            # Try to parse it as a Python literal (list/dict)
            parsed_data = ast.literal_eval(potential_list)
            
            # If it's a list of tool calls, format them nicely
            if isinstance(parsed_data, list):
                formatted_parts = [prefix + "\n"]
                for i, tool_call in enumerate(parsed_data, 1):
                    if isinstance(tool_call, dict):
                        formatted_parts.append(f"\n  Tool Call {i}:")
                        formatted_parts.append(f"    Name: {tool_call.get('name', 'N/A')}")
                        formatted_parts.append(f"    ID: {tool_call.get('id', 'N/A')}")
                        formatted_parts.append(f"    Type: {tool_call.get('type', 'N/A')}")
                        if 'args' in tool_call:
                            formatted_parts.append(f"    Args:")
                            formatted_parts.append(f"       {json.dumps(tool_call['args'], indent=7, ensure_ascii=False)}")
                return "\n".join(formatted_parts)
        except (ValueError, SyntaxError):
            # If parsing fails, return the original content
            pass
    
    # Try to detect if the entire content is a JSON/dict/list
    try:
        # Try JSON first
        parsed = json.loads(content)
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        try:
            # Try Python literal (ast.literal_eval)
            parsed = ast.literal_eval(content)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except (ValueError, SyntaxError):
            # If all parsing attempts fail, return original content
            return content

def format_message_content(message):
    """Convert message content to displayable string"""
    parts = []
    tool_calls_processed = False

    # Handle ToolCall objects (special case - they don't have 'content')
    if isinstance(message, dict) and 'args' in message and 'name' in message:
        # This is a ToolCall dictionary
        parts.append(f"Tool Call Name: {message.get('name', 'N/A')}")
        parts.append(f"ID: {message.get('id', 'N/A')}")
        
        # Format the args (which should be the tool calls list)
        args = message.get('args', [])
        if isinstance(args, list):
            for i, tool_call in enumerate(args, 1):
                if isinstance(tool_call, dict):
                    parts.append(f"\n  Tool Call {i}:")
                    parts.append(f"    Name: {tool_call.get('name', 'N/A')}")
                    parts.append(f"    ID: {tool_call.get('id', 'N/A')}")
                    parts.append(f"    Type: {tool_call.get('type', 'N/A')}")
                    if 'args' in tool_call:
                        parts.append(f"    Args:")
                        parts.append(f"       {json.dumps(tool_call['args'], indent=7, ensure_ascii=False)}")
        return "\n".join(parts)
    
    # Check if message has 'content' attribute
    if not hasattr(message, 'content'):
        # If it's a dict-like object, try to access it as a dict
        if hasattr(message, '__getitem__'):
            try:
                content = message['content'] if 'content' in message else str(message)
                parts.append(content)
                return "\n".join(parts)
            except (KeyError, TypeError):
                parts.append(str(message))
                return "\n".join(parts)
        else:
            parts.append(str(message))
            return "\n".join(parts)
    
    # Handle main content (normal messages with 'content' attribute)
    if isinstance(message.content, str):
        # Try to detect and format structured data within the string
        formatted_content = format_string_with_structures(message.content)
        parts.append(formatted_content)
    elif isinstance(message.content, list):
        # Handle complex content like tool calls (Anthropic format)
        for item in message.content:
            if item.get('type') == 'text':
                parts.append(item['text'])
            elif item.get('type') == 'tool_use':
                parts.append(f"\n🔧 Tool Call: {item['name']}")
                parts.append(f"   Args: {json.dumps(item['input'], indent=2)}")
                parts.append(f"   ID: {item.get('id', 'N/A')}")
                tool_calls_processed = True
    else:
        parts.append(str(message.content))
    
    # Handle tool calls attached to the message (OpenAI format) - only if not already processed
    if not tool_calls_processed and hasattr(message, 'tool_calls') and message.tool_calls:
        for tool_call in message.tool_calls:
            parts.append(f"\n🔧 Tool Call: {tool_call['name']}")
            parts.append(f"   Args: {json.dumps(tool_call['args'], indent=2)}")
            parts.append(f"   ID: {tool_call['id']}")
    
    return "\n".join(parts)


def format_messages(messages, title: str = "", border_style: str = "white", msg_subtype: str = ""):
    """Format and display a list of messages with Rich formatting
    
    Args:
        messages: List of messages to format
        title: Title of the panel
        border_style: Border style of the panel
        msg_subtype: Subtype of the message
    """
    # Check if messages is a list
    if isinstance(messages, list):
        for m in messages:
            # Handle different message types
            if isinstance(m, dict):
                # Check if it's a ToolCall dict
                if 'args' in m and 'name' in m:
                    msg_type = 'ToolCall'
                else:
                    msg_type = 'Dict'
            else:
                msg_type = m.__class__.__name__.replace('Message', '')
            
            content = format_message_content(m)

            if msg_type == 'Human':
                if msg_subtype == 'RealHumanMessage':
                    if title == "":
                        title = "🧑 Real Human Message"
                    else:
                        title = f"🧑 {title}"
                    console.print(Panel(content, title=title, border_style="#201ADB"))    # Blue
                else:
                    if title == "":
                        title = "🧑 Simulated Human Message"
                    else:
                        title = f"🧑 {title}"
                    console.print(Panel(content, title=title, border_style="#1A64DB"))    # Blue
            elif msg_type == 'AI':
                if title == "":
                    title = "🤖 Assistant"
                else:
                    title = f"🤖 {title}"
                console.print(Panel(content, title=title, border_style="#24FA00"))    # Green
            elif msg_type == 'ClarifyWithUser':
                if title == "":
                    title = "🤖 Clarify With User"
                else:
                    title = f"🤖 {title}"
                console.print(Panel(content, title=title, border_style="#37DB1A"))    # Green
            elif msg_type == 'ResearchQuestion':
                if title == "":
                    title = "🤖 Research brief generated"
                else:
                    title = f"🤖 {title}"
                console.print(Panel(content, title=title, border_style="#37DB1A"))    # Green
            elif msg_type == 'Tool':
                if title == "":
                    title = "🔧 Tool Output"
                else:
                    title = f"🔧 {title}"
                console.print(Panel(content, title=title, border_style="yellow"))
            elif msg_type == 'ToolCall':
                if title == "":
                    title = "🔧 Tool Calls"
                else:
                    title = f"🔧 {title}"
                console.print(Panel(content, title=title, border_style="magenta"))
            elif msg_type == 'Use tools':
                if title == "":
                    title = "🔧 Tool Output"
                else:
                    title = f"🔧 {title}"
                console.print(Panel(content, title=title, border_style="yellow"))
            elif msg_type == 'System':
                if title == "":
                    title = "🔧 System Message"
                else:
                    title = f"🔧 {title}"
                console.print(Panel(content, title=title, border_style="red"))
            else:
                print(f"msg_type: {msg_type}")
                if title == "":
                    title = f"📝 {msg_type}"
                else:
                    title = f"📝 {title}"
                console.print(Panel(content, title=title, border_style="white"))
    elif isinstance(messages, str):
        console.print(Panel(messages, title=title, border_style=border_style))
    else:
        print(f"messages type: {type(messages)}")


def format_message(messages):
    """Alias for format_messages for backward compatibility"""
    return format_messages(messages)


def show_prompt(prompt_text: str, title: str = "Prompt", border_style: str = "blue"):
    """
    Display a prompt with rich formatting and XML tag highlighting.
    
    Args:
        prompt_text: The prompt string to display
        title: Title for the panel (default: "Prompt")
        border_style: Border color style (default: "blue")
    """
    # Create a formatted display of the prompt
    formatted_text = Text(prompt_text)
    formatted_text.highlight_regex(r'<[^>]+>', style="bold blue")  # Highlight XML tags
    formatted_text.highlight_regex(r'##[^#\n]+', style="bold magenta")  # Highlight headers
    formatted_text.highlight_regex(r'###[^#\n]+', style="bold cyan")  # Highlight sub-headers

    # Display in a panel for better presentation
    console.print(Panel(
        formatted_text, 
        title=f"[bold green]{title}[/bold green]",
        border_style=border_style,
        padding=(1, 2)
    ))