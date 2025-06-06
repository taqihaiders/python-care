from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello!",
        }
    ],
    model="claude-3-5-sonnet-latest",
)
print(response)

response2 = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "foll",
        },
        {
            "role": response.role,
            "content": response.content,
        },
        {
            "role": "user",
            "content": "How are you?",
        },
    ],
    model="claude-3-5-sonnet-latest",
)
print(response2)
