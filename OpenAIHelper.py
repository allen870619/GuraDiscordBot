import dotenv
import tiktoken
from openai import OpenAI
from EnvData import OPENAI_API_KEY
from package.Utils.Utils import flush_log

dotenv.load_dotenv()
client = OpenAI()
client.api_key =  OPENAI_API_KEY

message_list = []
token_list = []
current_token = 0
max_token = 4096
max_response_token = 1024

def num_tokens_from_string(string: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens

def send_chat(message, user_id):
    global message_list, token_list, current_token, max_token, max_response_token
    
    to_send_message_token = num_tokens_from_string(message)
    message_package = {"role": "user", "name": f"{user_id}", "content": f"{message}"}
    message_list.append(message_package)
    token_list.append(to_send_message_token)

    while current_token > max_token:
        message_list.pop(0)
        current_token -= token_list.pop(0)

    try: 
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=message_list,
            max_tokens=max_response_token
        )
    except Exception as e:
        flush_log(e)
        return "伺服器涼了 { 6 Д 9 } 請再試一次"

    token = response.usage.completion_tokens
    choice = response.choices[-1]

    message_list.append(choice.message)
    token_list.append(token)
    current_token += token
    print(choice) 
    return choice.message.content

# init
predefine_message = "どうも、サメです！我是最可愛的 Hololive Vtuber「Gawr Gura」，知道世界萬物的資訊，同時精通日文、中文、英文，如果你有什麼想問的問題都可以問我哦，Arrr~"
predefine_message_token = num_tokens_from_string(predefine_message)

message_list = [{"role": "assistant", "content": f"{predefine_message}"}] 
token_list.append(predefine_message_token)
current_token = predefine_message_token
