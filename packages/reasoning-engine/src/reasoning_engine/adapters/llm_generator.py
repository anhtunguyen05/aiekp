from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from reasoning_engine.ports.outbound import ILLMGenerator


class LangChainLLMAdapter(ILLMGenerator):
    def __init__(self, model_name: str = "gemini-3.5-flash", temperature: float = 0.0):
        import os

        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            model=model_name, temperature=temperature, google_api_key=api_key
        )

    async def generate(self, prompt: str, system_message: str = None) -> str:
        messages = []
        if system_message:
            messages.append(SystemMessage(content=system_message))
        messages.append(HumanMessage(content=prompt))

        response = await self.llm.ainvoke(messages)
        content = response.content
        if isinstance(content, list):
            # Combine text parts if it's a list
            return " ".join(
                [c.get("text", "") if isinstance(c, dict) else str(c) for c in content]
            )
        return str(content)

    async def astream(self, prompt: str, system_message: str = None):
        messages = []
        if system_message:
            messages.append(SystemMessage(content=system_message))
        messages.append(HumanMessage(content=prompt))

        async for chunk in self.llm.astream(messages):
            if isinstance(chunk.content, list):
                yield " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in chunk.content])
            else:
                yield str(chunk.content)
