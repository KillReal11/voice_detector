import logging
import random
import time

import vk_api as vk
from environs import Env
from vk_api.longpoll import VkEventType, VkLongPoll

from dialogflow_utils import detect_intent
from logging_utils import configure_logging


MIN_RETRY_DELAY = 10
MAX_RETRY_DELAY = 300

logger = logging.getLogger("vk_bot")


def reply_with_dialogflow(event, project_id, vk_api):
    session_id = f"vk-{event.user_id}"
    intent_answer = detect_intent(project_id, session_id, event.text)
    logger.debug(
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
    env = Env()
    env.read_env()
    vk_token = env.str("VK_TOKEN")
    project_id = env.str("DIALOGFLOW_PROJECT_ID")

    configure_logging(logger, env)
    retry_delay = MIN_RETRY_DELAY
    try:
        vk_session = vk.VkApi(token=vk_token)
        vk_api = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)
        logger.info("VK-бот запущен")

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                try:
                    reply_with_dialogflow(event, vk_api, project_id)
                except Exception:
                    logger.exception("Ошибка при обработке сообщения")
    except Exception:
        logger.exception(f"VK-бот упал с ошибкой, перезапуск через {retry_delay} с")
        time.sleep(retry_delay)
        retry_delay = min(retry_delay * 2, MAX_RETRY_DELAY)


if __name__ == "__main__":
    main()
