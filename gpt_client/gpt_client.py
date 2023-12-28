import openai
from openai import OpenAI


class GPTClient:
    def __init__(self, openai_key: str, model: str, temperature: float, max_retries: int = 5):
        self.openai_key = openai_key
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(api_key=self.openai_key, max_retries=max_retries,)

    def ask(self, prompt):
        try:
            chat_completion = self.client.chat.completions.create(
                model=self.model, temperature=self.temperature,
                messages=[{"role": "system", "content": prompt}])
            message = chat_completion.choices[0].message.content
            return message
        except openai.APIError as e:
            print(f"Error to get OpenAI answer {e}")
            return
        except Exception as e:
            print(f"Unexpected error while try to get OpenAI answer\n {e}")
            return
