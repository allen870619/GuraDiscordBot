import openai
import dotenv
from EnvData import OPENAI_API_KEY
from package.Utils.Utils import flush_log

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


message_list = []
token_list = []
current_token = 0

def openai_gpt_chat(msgToSend: str, user_id):
    global message_list, token_list, current_token
    max_token = 1024
    
    # prepare sending message
    to_send_msg = {"role": "user", "content": msgToSend}
    tmp_list = message_list
    tmp_list.append(to_send_msg)
    
    try: 
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                messages=tmp_list,
                                                max_tokens=max_token,
                                                user=f"{user_id}")
        content = str(response["choices"][0]["message"]["content"])
        while content.startswith("\n"):
            content = content.removeprefix("\n")
        message_list = tmp_list
        message_list.append({"role": "user", "content": f"{content}"})
        
        # token
        msg_token = response["usage"]["prompt_tokens"]
        completion_tokens = response["usage"]["completion_tokens"]
        token_list.append(msg_token)
        token_list.append(completion_tokens)
        current_token += msg_token + completion_tokens
        
        while current_token + max_token > 4096:
            message_list.pop(0)
            current_token -= token_list.pop(0)
    except Exception as e:
        flush_log(e)
        return "伺服器涼了 { 6 Д 9 } 請再試一次"
    return content