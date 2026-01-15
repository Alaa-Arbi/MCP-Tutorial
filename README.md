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
