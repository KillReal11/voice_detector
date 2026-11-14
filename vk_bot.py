import logging
import random

import vk_api as vk
from environs import Env
from vk_api.longpoll import VkEventType, VkLongPoll

from dialogflow_utils import detect_intent

logger = logging.getLogger(__name__)


def reply_with_dialogflow(event, project_id, vk_api):
    session_id = f"vk-{event.user_id}"
    intent_answer = detect_intent(project_id, session_id, event.text)
    logger.info(
        "%s | %s", intent_answer.intent.display_name,
        intent_answer.fulfillment_text
    )
    if not intent_answer.intent.is_fallback:
        vk_api.messages.send(
            user_id=event.user_id,
            message=intent_answer.fulfillment_text,
            random_id=random.randint(1, 1000),
        )


def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    env = Env()
    env.read_env()
    vk_token = env.str("VK_TOKEN")
    project_id = env.str("DIALOGFLOW_PROJECT_ID")

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            try:
                reply_with_dialogflow(event, vk_api, project_id)
            except Exception:
                logger.exception("Ошибка при обработке сообщения")


if __name__ == "__main__":
    main()
