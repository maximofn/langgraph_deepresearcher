import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import asyncio

async def main():

    console = Console()

    # Get the absolute path to our sample research docs
    sample_docs_path = os.path.abspath("./files/")
    console.print(f"[bold blue]Sample docs path:[/bold blue] {sample_docs_path}")

    # Check if the directory exists
    if os.path.exists(sample_docs_path):
        console.print(f"[green]✓ Directory exists with files:[/green] {os.listdir(sample_docs_path)}")
    else:
        console.print("[red]✗ Directory does not exist![/red]")
        console.print(f"[yellow]Please create the directory: {sample_docs_path}[/yellow]")
        return  # Exit early if directory doesn't exist

    # MCP Client configuration - filesystem server for local document access
    mcp_config = {
        "filesystem": {
            "command": "npx",
            "args": [
                "-y",  # Auto-install if needed
                "@modelcontextprotocol/server-filesystem",
                sample_docs_path
            ],
            "transport": "stdio"
        }
    }

    console.print(Panel("[bold yellow]Creating MCP client...[/bold yellow]", expand=False))
    client = MultiServerMCPClient(mcp_config)
    console.print("[green]✓ MCP client created successfully![/green]")

    # Test getting tools
    console.print(Panel("[bold yellow]Getting tools...[/bold yellow]", expand=False))
    tools = await client.get_tools()

    # Create a rich table for tool display
    table = Table(title="Available MCP Tools", show_header=True, header_style="bold magenta")
    table.add_column("Tool Name", style="cyan", width=25)
    table.add_column("Description", style="white", width=80)

    for tool in tools:
        # Truncate long descriptions for better display
        description = tool.description[:77] + "..." if len(tool.description) > 80 else tool.description
        table.add_row(tool.name, description)

    console.print(table)
    console.print(f"[bold green]✓ Successfully retrieved {len(tools)} tools from MCP server[/bold green]")

if __name__ == "__main__":
    asyncio.run(main())