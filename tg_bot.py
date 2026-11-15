import logging
from functools import partial

from environs import Env
from telegram import ForceReply, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

from dialogflow_utils import detect_intent
from logging_utils import configure_logging


logger = logging.getLogger("tg_bot")


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        rf"Привет {user.mention_markdown_v2()}\!",
        reply_markup=ForceReply(selective=True),
    )


def reply_with_dialogflow(update: Update, context: CallbackContext, project_id) -> None:
    session_id = f"tg-{update.effective_chat.id}"
    intent_answer = detect_intent(project_id, session_id, update.message.text)
    logger.debug(
        "%s | %s", intent_answer.intent.display_name,
        intent_answer.fulfillment_text
    )
    update.message.reply_text(intent_answer.fulfillment_text)


def handle_error(update: object, context: CallbackContext) -> None:
    logger.error("Ошибка при обработке сообщения", exc_info=context.error)


def build_request_kwargs(proxy_url):
    request_kwargs = {"connect_timeout": 20.0, "read_timeout": 20.0}
    if proxy_url:
        request_kwargs["proxy_url"] = proxy_url
    return request_kwargs


def main():
    env = Env()
    env.read_env()
    tg_token = env.str("TG_TOKEN")
    project_id = env.str("DIALOGFLOW_PROJECT_ID")
    proxy_url = env.str("PROXY_SOCKS5", default=None)

    configure_logging(logger, env)
    try:
        updater = Updater(tg_token, request_kwargs=build_request_kwargs(proxy_url))
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(
            MessageHandler(
                Filters.text & ~Filters.command,
                partial(reply_with_dialogflow, project_id=project_id),
            )
        )
        dispatcher.add_error_handler(handle_error)

        updater.start_polling()
        logger.info("Telegram-бот запущен")
        updater.idle()
    except Exception:
        logger.exception("Telegram-бот упал с ошибкой")
        raise


if __name__ == "__main__":
    main()
