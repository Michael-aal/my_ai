import os
import re
import time
import logging
from typing import Callable, Optional
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from collections import deque

load_dotenv()

# ================================
# LOGGING
# ================================
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("ai_engine")

# ================================
# IMPORTS
# ================================
try:
    import google.generativeai as genai
except:
    genai = None

try:
    from openai import OpenAI
except:
    OpenAI = None

try:
    from groq import Groq
except:
    Groq = None

try:
    from mistralai import Mistral
except:
    Mistral = None

try:
    import cohere
except:
    cohere = None

# ================================
# KEYS
# ================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

SYSTEM_PROMPT = "You are a fast, concise AI assistant. Keep replies short."

# ================================
# CLEANER
# ================================
def clean(text: str):
    if not text:
        return None
    text = re.sub(r"\*+|#+", "", text)
    return text.strip()

# ================================
# TIMEOUT
# ================================
executor = ThreadPoolExecutor(max_workers=5)

def run_with_timeout(fn: Callable, timeout=6):
    future = executor.submit(fn)
    try:
        return future.result(timeout=timeout)
    except:
        return None

# ================================
# CONVERSATION MEMORY
# ================================
MAX_HISTORY = 10

class ConversationBuffer:
    def __init__(self):
        self.buf = deque(maxlen=MAX_HISTORY)

    def add(self, role, content):
        self.buf.append({"role": role, "content": content})

    def get(self):
        return list(self.buf)

conversation = ConversationBuffer()

# ================================
# PROVIDERS (UNIFIED SIGNATURE)
# ================================

def gemini_response(prompt, history=None):
    if not genai or not GEMINI_API_KEY:
        return None

    def call():
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        r = model.generate_content(
            f"{SYSTEM_PROMPT}\nUser: {prompt}"
        )
        return clean(r.text)

    return run_with_timeout(call)


def openai_response(prompt, history=None):
    if not OpenAI or not OPENAI_API_KEY:
        return None

    def call():
        client = OpenAI(api_key=OPENAI_API_KEY)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        else:
            messages.append({"role": "user", "content": prompt})

        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        return clean(r.choices[0].message.content)

    return run_with_timeout(call)


def groq_response(prompt, history=None):
    if not Groq or not GROQ_API_KEY:
        return None

    def call():
        client = Groq(api_key=GROQ_API_KEY)

        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        return clean(r.choices[0].message.content)

    return run_with_timeout(call)


def mistral_response(prompt, history=None):
    if not Mistral or not MISTRAL_API_KEY:
        return None

    def call():
        client = Mistral(api_key=MISTRAL_API_KEY)

        r = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        return clean(r.choices[0].message.content)

    return run_with_timeout(call)


def cohere_response(prompt, history=None):
    if not cohere or not COHERE_API_KEY:
        return None

    def call():
        client = cohere.ClientV2(api_key=COHERE_API_KEY)

        r = client.chat(
            model="command-r-plus",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        return clean(r.message.content[0].text)

    return run_with_timeout(call)

# ================================
# PROVIDER CHAIN
# ================================
PROVIDERS = [
    ("Groq", groq_response),
    ("OpenAI", openai_response),
    ("Gemini", gemini_response),
    ("Mistral", mistral_response),
    ("Cohere", cohere_response),
]

# ================================
# MAIN ENGINE
# ================================
def get_ai_response(prompt: str):

    conversation.add("user", prompt)
    history = conversation.get()

    for name, fn in PROVIDERS:
        logger.info("Trying %s", name)

        try:
            response = fn(prompt, history)

            if response:
                conversation.add("assistant", response)
                logger.info("Success: %s", name)
                return response

        except Exception as e:
            logger.warning("%s crashed: %s", name, e)

    return "All AI providers failed."