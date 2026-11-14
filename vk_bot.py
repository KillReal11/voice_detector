from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api as vk
from environs import Env
import random
from google.cloud import dialogflow
import logging


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def echo(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1, 1000)
    )


def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    return response.query_result


def reply_with_dialogflow(event, project_id, vk_api):
    session_id = str(event.user_id)
    intent_answer = detect_intent_texts(
        project_id,
        session_id,
        event.text,
        language_code="ru"
    )
    if not intent_answer.intent.is_fallback:
        vk_api.messages.send(
            user_id=event.user_id,
            message=intent_answer.fulfillment_text,
            random_id=random.randint(1, 1000)
        )
    logger.info("%s | %s", intent_answer.intent.display_name, intent_answer.fulfillment_text)


if __name__ == "__main__":
    env = Env()
    env.read_env()
    vk_token = env.str("VK_TOKEN")
    project_id = env.str("DIALOGFLOW_PROJECT_ID")
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            reply_with_dialogflow(event, project_id, vk_api)
