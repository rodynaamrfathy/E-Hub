from services.conversation.orchestration import orchestrate_query
from services.conversation.streaming import stream_llm_response

async def handle_request(query, image=None):
    context = await orchestrate_query(query, image)
    async for token in stream_llm_response(context):
        yield token 