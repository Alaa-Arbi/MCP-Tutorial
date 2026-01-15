# MCP-Tutorial
This is a repo, in which I track code I used to learn about the Model Context Protocol


The key participants in the MCP architecture are:
- MCP Host: The AI application that coordinates and manages one or multiple MCP clients
- MCP Client: A component that maintains a connection to an MCP server and obtains context from an MCP server for the MCP host to use
- MCP Server: A program that provides context to MCP clients

MCP consists of two layers:
- Data layer: Defines the JSON-RPC based protocol
- Transport layer: Defines the communication mechanisms (Stdio transport for local servers and Streamable HTTP transport for remote servers)

MCP primitives are the most important concept within MCP. They define what clients and servers can offer each other. These primitives specify the types of contextual information that can be shared with AI applications and the range of actions that can be performed.

MCP Server Primitives:
- Tools: Executable functions that AI applications can invoke to perform actions (e.g., file operations, API calls, database queries)
- Resources: Data sources that provide contextual information to AI applications (e.g., file contents, database records, API responses)
- Prompts: Reusable templates that help structure interactions with language models (e.g., system prompts, few-shot examples)

As a concrete example, consider an MCP server that provides context about a database. It can expose tools for querying the database, a resource that contains the schema of the database, and a prompt that includes few-shot examples for interacting with the tools.

MCP Client Primitives: These primitives allow MCP server authors to build richer interactions.
- Sampling: Allows servers to request language model completions from the client’s AI application. This is useful when servers’ authors want access to a language model, but want to stay model independent and not include a language model SDK in their MCP server. They can use the sampling/complete method to request a language model completion from the client’s AI application.
- Elicitation: Allows servers to request additional information from users. This is useful when servers’ authors want to get more information from the user, or ask for confirmation of an action. They can use the elicitation/request method to request additional information from the user.
- Logging: Enables servers to send log messages to clients for debugging and monitoring purposes.

## Hands-on Learning with MCP

### MCP Client
The `mcp_client.py` script demonstrates how to implement an MCP client. Key features include:
- **Connecting to an MCP Server**: The client connects to a server script (e.g., `mcp_server.py`) using the Stdio transport layer.
- **Tool Discovery**: The client lists available tools provided by the server and uses them dynamically.
- **OpenAI Integration**: The client uses OpenAI's GPT-4o model to process queries and interact with tools exposed by the server.
- **Elicitation Handling**: The client handles elicitation requests from the server, allowing user confirmation or cancellation of actions.
- **Interactive Chat Loop**: The client provides an interactive loop for users to input queries and receive responses.

### MCP Server
The `mcp_server.py` script demonstrates how to implement an MCP server. Key features include:
- **Tool Implementation**: The server provides tools such as `get_alerts` (fetches weather alerts) and `get_forecast` (fetches weather forecasts for a location).
- **Resource Exposure**: The server exposes resources like weather station information and IDs.
- **Prompt Definition**: The server defines prompts, such as `weather_summary_prompt`, to structure interactions with the client.
- **Elicitation Requests**: The server uses elicitation to confirm user actions before executing tools.
- **Integration with External APIs**: The server fetches data from the National Weather Service (NWS) API to provide real-time weather information.

### Key Takeaways
- **MCP Architecture**: The hands-on implementation highlights the interaction between MCP clients and servers, showcasing the use of tools, resources, and prompts.
- **Dynamic Tool Usage**: The client dynamically discovers and invokes tools provided by the server, demonstrating the flexibility of MCP.
- **User Interaction**: Elicitation enables rich user interactions, allowing servers to request additional information or confirmations.
- **AI Integration**: The integration of OpenAI's GPT-4o model in the client demonstrates how AI can enhance MCP-based applications.

This hands-on experience provided a deeper understanding of how MCP facilitates communication and context sharing between AI applications and external systems.
