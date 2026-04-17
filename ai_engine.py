from google import genai

client = genai.Client(
    api_key="AIzaSyDf2ikyEvaFvJfhfMYrvyHnwlQIVI95qZ0"
)

data = """
You are a software engineer.
User name: Michael
User role: student, full-stack developer
User goal: building a local voice assistant project
Ai role: programmer assistant for coding and problem solving
"""


def get_ai_response(prompt):

    try:

        full_prompt = data + "\nUser: " + prompt

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[full_prompt]
        )

        if response.text:
            return response.text.strip()

        return "I could not generate a response."

    except Exception as e:

        print("AI Engine Error:", e)

        return "There was an error contacting the AI service."