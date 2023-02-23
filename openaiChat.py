import openai
import dotenv
from EnvData import OPENAI_API_KEY

dotenv.load_dotenv()
openai.api_key = OPENAI_API_KEY

def openai_txt_chat(prompt):
    # Load your API key from an environment variable or secret management service
    response = openai.Completion.create(model="text-davinci-003",
                                        prompt=prompt,
                                        temperature=0.9,
                                        n=3,
                                        max_tokens=2000)
    responseText = response["choices"][0]["text"]
    return responseText[2:]