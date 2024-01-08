import openai
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class GPTClient:
    def __init__(self, openai_key: str, model: str, temperature: float, max_retries: int = 5):
        self.openai_key = openai_key
        self.model = model
        self.temperature = temperature
        # self.client = OpenAI(api_key=self.openai_key, max_retries=max_retries, )
        self.llm = ChatOpenAI(openai_api_key=self.openai_key, model_name=self.model, temperature=self.temperature)

    def ask(self, user_prompt):
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are world class technical security researcher."),
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
