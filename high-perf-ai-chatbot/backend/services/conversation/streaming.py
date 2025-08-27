from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

PROMPT_TEMPLATE  = "you are dawar eco assistant"

async def stream_llm_response(context):
    llm = ChatOpenAI(streaming=True, callbacks=[], temperature=0)
    chain = LLMChain(llm=llm, prompt=PROMPT_TEMPLATE)

    # Async token streaming
    async for token in chain.arun(context):
        yield token