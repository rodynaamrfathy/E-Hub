import asyncio
from typing import Dict, AsyncGenerator, Optional
from dataclasses import dataclass
from langchain.callbacks.base import BaseCallbackHandler


@dataclass
class StreamChunk:
    """Represents a chunk of streamed response."""
    content: str
    is_complete: bool = False
    chunk_type: str = "text"  # "text", "reference", "error", "status", "timeout", "complete"
    metadata: Optional[Dict] = None


class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming LLM responses."""

    def __init__(self):
        self.content = ""
        self.chunks = []
        self._chunk_queue = asyncio.Queue()

    # ---- TOKEN EVENT ----
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called every time a new token is generated."""
        self.content += token
        chunk = StreamChunk(content=token, chunk_type="text")
        self.chunks.append(chunk)
        # schedule safely into async queue
        asyncio.create_task(self._chunk_queue.put(chunk))

    # ---- END EVENT ----
    def on_llm_end(self, response, **kwargs) -> None:
        """Called when generation is complete."""
        final_chunk = StreamChunk(content="", is_complete=True, chunk_type="complete")
        asyncio.create_task(self._chunk_queue.put(final_chunk))

    # ---- ERROR EVENT ----
    def on_llm_error(self, error, **kwargs) -> None:
        """Called when generation fails."""
        error_chunk = StreamChunk(
            content=str(error), is_complete=True, chunk_type="error"
        )
        asyncio.create_task(self._chunk_queue.put(error_chunk))

    # ---- ASYNC CONSUMER ----
    async def get_chunks(self) -> AsyncGenerator[StreamChunk, None]:
        """Async generator yielding streamed chunks."""
        while True:
            try:
                chunk = await asyncio.wait_for(self._chunk_queue.get(), timeout=30.0)
                yield chunk
                if chunk.is_complete:
                    break
            except asyncio.TimeoutError:
                yield StreamChunk(content="", is_complete=True, chunk_type="timeout")
                break
