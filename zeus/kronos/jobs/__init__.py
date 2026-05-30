# zeus/kronos/jobs/ — Built-in job implementations.
# Each job exposes `async def <entry>(params: dict) -> dict | str` and is
# referenced from JobDefinition.executor as a dotted import path.
