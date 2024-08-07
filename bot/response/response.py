from dotenv import load_dotenv
from openai import OpenAI
from bot.logging_config import logger, logging
from bot.response.system_settings import GPT_Settings

logger = logging.getLogger(__name__)

load_dotenv()

client = OpenAI()

def generate_response(prompt):
    completion = client.chat.completions.create(
    model= GPT_Settings.model,
    messages=[
        GPT_Settings.system,
        {"role": "user", "content": prompt}
    ],
    temperature=GPT_Settings.temperature,
    max_tokens=GPT_Settings.max_tokens
    )
    return completion.choices[0].message.content