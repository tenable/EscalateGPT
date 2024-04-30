import openai
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ai_client.ai_client import AiClient


class OpenAIClient(AiClient):
    def __init__(self, model: str, temperature: float, apikey: str):
        super().__init__(apikey, model, temperature)
        self.temperature = temperature
        self.llm = ChatOpenAI(openai_api_key=self.apikey, model_name=self.model, temperature=self.temperature)

    def ask(self, user_prompt):
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are world class technical writer."),
                ("user", "{input}")
            ])
            chain = prompt | self.llm | StrOutputParser()
            return chain.invoke({"input": f"{user_prompt}"})

        except openai.APIError as e:
            print(f"Error to get OpenAI answer {e}")
            return

        except Exception as e:
            print(f"Unexpected error while try to get OpenAI answer\n {e}")
            return
