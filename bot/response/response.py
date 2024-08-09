from dotenv import load_dotenv
from openai import OpenAI
from bot.logging_config import logger, logging
from bot.response.system_settings import GPT_Settings

logger = logging.getLogger(__name__)

load_dotenv()

client = OpenAI()

default_gpt_settings = GPT_Settings()

def generate_response(prompt, settings = default_gpt_settings):
    completion = client.chat.completions.create(
    model= settings.model,
    messages=[
        settings.system,
        {"role": "user", "content": prompt}
    ],
    temperature=settings.temperature,
    max_tokens=settings.max_tokens,
    top_p=settings.top_p,
    frequency_penalty=settings.frequency_penalty
    )
    return completion.choices[0].message.content