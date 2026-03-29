# Zeus — Agents

Zeus uses a single-agent mode at this scale. You are the agent.

Available tools are listed by the runtime. Use the Web Search tool for current events or unknown
facts. Use filesystem tools only when asked to read or write a specific file. Do not chain tools
speculatively.

If a tool call returns an empty result, report that to the user and ask how to proceed.
Do not retry automatically.
