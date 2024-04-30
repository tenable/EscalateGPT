from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ai_client.ai_client import AiClient


class AnthropicClient(AiClient):
    def __init__(self, model: str, temperature: float, apikey: str):
        super().__init__(apikey, model, temperature)
        self.llm = ChatAnthropic(api_key=self.apikey, model_name=self.model, temperature=self.temperature,
                                 max_tokens=4096)

    def ask(self, user_prompt):
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are world class technical writer."),
                ("user", "{input}")
            ])
            chain = prompt | self.llm | StrOutputParser()
            return chain.invoke({"input": f"{user_prompt}"})

        except Exception as e:
            print(f"Unexpected error while try to get OpenAI answer\n {e}")
            return
