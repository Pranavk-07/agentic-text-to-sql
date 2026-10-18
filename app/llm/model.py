import os
from dotenv import load_dotenv
from google import genai

# Load variables from .env
load_dotenv()

# Get Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

# Check API key
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Create Gemini client
client = genai.Client(api_key=api_key)


def ask_llm(prompt):
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text


if __name__ == "__main__":
    answer = ask_llm("What is SQL? Explain in one sentence.")
    print(answer)