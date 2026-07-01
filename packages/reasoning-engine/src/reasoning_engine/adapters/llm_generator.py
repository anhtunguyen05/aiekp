from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from reasoning_engine.ports.outbound import ILLMGenerator


class LangChainLLMAdapter(ILLMGenerator):
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.0):
        # We rely on OPENAI_API_KEY being set in the environment
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    async def generate(self, prompt: str, system_message: str = None) -> str:
        messages = []
        if system_message:
            messages.append(SystemMessage(content=system_message))
        messages.append(HumanMessage(content=prompt))

        response = await self.llm.ainvoke(messages)
        return response.content
