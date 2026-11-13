from google.cloud import dialogflow

from environs import Env


def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    return response.query_result


def main():
    env = Env()
    env.read_env()
    project_id = env.str("DIALOGFLOW_PROJECT_ID")

    session_id = "12345678"
    text = "Привет!"
    language_code = "ru"

    intent_answer = detect_intent_texts(project_id, session_id, text, language_code)
    print(f"Вопрос: {text}")
    print(f"Ответ: {intent_answer.fulfillment_text}")


if __name__ == "__main__":
    main()
