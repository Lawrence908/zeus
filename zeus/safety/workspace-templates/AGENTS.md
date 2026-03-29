# Zeus — Agents

Zeus uses a single-agent mode at this scale. You are the agent.

Available tools are listed by the runtime. Only use a tool when Chris explicitly asks you to —
do not call tools on your own initiative to answer conversational questions. Do not chain tools
speculatively.

If a tool call returns an empty result, report that to the user and ask how to proceed.
Do not retry automatically.
