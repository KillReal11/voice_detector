import json

from environs import Env
from google.cloud import dialogflow


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name, training_phrases=training_phrases, messages=[message]
    )

    intents_client.create_intent(request={"parent": parent, "intent": intent})


def main():
    env = Env()
    env.read_env()
    project_id = env.str("DIALOGFLOW_PROJECT_ID")

    with open("questions.json", "r", encoding="utf-8") as file:
        questions_json = file.read()

    templates = json.loads(questions_json)
    job_questions = templates["Устройство на работу"]["questions"]
    job_answer = [templates["Устройство на работу"]["answer"]]

    create_intent(
        project_id,
        "Устройство на работу",
        job_questions,
        job_answer,
    )


if __name__ == "__main__":
    main()
