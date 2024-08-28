from ollama import Client
import asyncio
from ollama import AsyncClient


# client = Client(host='http://192.168.1.111:11434')
client = AsyncClient(host='http://127.0.0.1:11434')

# response = client.chat(model='qwen', messages=[
#     {
#         'role': 'user',
#         'content': 'Why is the sky blue?',
#     },
# ])


async def chat():
    message = {'role': 'user', 'content': 'Why is the sky blue?'}
    response = await AsyncClient().chat(model='qwen', messages=[message])
    print(response['message']['content'])

asyncio.run(chat())
