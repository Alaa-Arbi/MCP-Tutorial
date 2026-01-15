import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.openai = OpenAI()
    # methods will go here

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "/Users/a.arbi/MCP-Tutorial/.venv/bin/python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in response.tools]

        # Initial OpenAI API call
        response = self.openai.chat.completions.create(
            model="gpt-4o",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        final_text = []
        
        while response.choices[0].finish_reason == "tool_calls":
            message = response.choices[0].message
            messages.append(message)
            
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = eval(tool_call.function.arguments)
                
                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": str(result.content)
                })
            
            # Get next response from OpenAI
            response = self.openai.chat.completions.create(
                model="gpt-4o",
                max_tokens=1000,
                messages=messages,
                tools=available_tools
            )
        
        if response.choices[0].message.content:
            final_text.append(response.choices[0].message.content)

        return "\n".join(final_text)
    
    async def get_and_run_prompt(self, name, args):
        prompt_def = await self.session.get_prompt(name=name, arguments=args)
        query = prompt_def.messages[0].content.text
        try:
            response = await self.process_query(query)
            print("\n" + response)
        except Exception as e:
            print(f"\nError: {str(e)}")
    
    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")

        print("Reading and listing all resources from the server...")
        await self.list_and_read_resources(self.session)

        print("Listing available prompts from the server...")
        await self.list_prompts()

        print("Type your queries or 'quit' to exit.")
        while True:
            try:

                query = input("\nQuery: ").strip()

                if query.startswith("/weather_summary_prompt"):
                    _, city = query.split(" ", 1)
                    await self.get_and_run_prompt("weather_summary_prompt", {"city": city})
                    continue

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

    async def list_prompts(self):
        result = await self.session.list_prompts()
        for p in result.prompts:
            print(p.name, "-", p.description, p.arguments)

    async def list_resource_templates(self, session: ClientSession):
        # Ask the server for all resources
        response = await session.list_resource_templates()
        resources = response.resourceTemplates # list of Resource objects

        print("\n=== Available Resource Templates ===")
        for r in resources:
            print(f"URI: {r.uriTemplate}, name: {r.name}, description: {r.description}")
        return resources

    async def list_resources(self, session: ClientSession):
        # Ask the server for all resources
        response = await session.list_resources()
        resources = response.resources  # list of Resource objects

        print("\n=== Available Resources ===")
        for r in resources:
            print(f"URI: {r.uri}, name: {r.name}, description: {r.description}")
        return resources
    
    async def read_resource(self, session: ClientSession, uri: str):
        try:
            # This makes a `resources/read` request for that specific URI
            content, mime_type = await session.read_resource(uri)

            print(f"\n--- Resource Content: {uri} ---")
            print(f"MIME type: {mime_type}")
            print(content)   # text for text resources

        except Exception as e:
            print(f"Failed to read resource {uri}: {e}")

    async def list_and_read_resources(self, session: ClientSession):
        resource_templates = await self.list_resource_templates(session)
        resources = await self.list_resources(session)

        for r in resources:
            # Read and print each resource
            await self.read_resource(session, r.uri)


async def main(): 
    path_to_server_script = "mcp_server.py"  
    client = MCPClient()
    try:
        await client.connect_to_server(path_to_server_script)
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())