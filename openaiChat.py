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


messageList = []


def openai_gpt_chat(msgToSend: str, userId):
    global messageList
    toSendJson = {"role": "user", "content": msgToSend}
    tmp = messageList
    tmp.append(toSendJson)
    try: 
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                messages=tmp,
                                                temperature=0.75,
                                                n=1,
                                                max_tokens=2048,
                                                user=f"{userId}")
        content = response["choices"][0]["message"]["content"][2:]
        messageList = tmp
        messageList.append({"role": "user", "content": f"{content}"})
    except Exception as e:
        print(e)
        return "伺服器涼了 { 6 Д 9 } 請再試一次"    
    return content