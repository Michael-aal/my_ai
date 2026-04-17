from command_area import parse_command
from action_engine import perform_action
from ai_engine import get_ai_response
from voice import speak


def run_assistant():

    while True:

        try:

            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("Jarvis: Goodbye")
                speak("Goodbye")
                break

            action = parse_command(user_input)

            if action:

                speakRes(action)

            else:

                response = get_ai_response(user_input)

                print("Jarvis:", response)

                speak(response)

        except Exception as error:

            error_message = f"An error occurred: {str(error)}"

            print("Jarvis:", error_message)

            speak(error_message)


def speakRes(action):

    result = perform_action(action)

    print("DEBUG ACTION:", action)

    print("Jarvis:", result)

    if result:

        speak(result)

    else:

        speak("Command executed")
        