#!/usr/bin/env python

import logging
from functools import partial

from environs import Env
from google.cloud import dialogflow
from telegram import ForceReply, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        rf"Hi {user.mention_markdown_v2()}\!",
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    return response.query_result


def reply_with_dialogflow(update: Update, context: CallbackContext, project_id) -> None:
    session_id = str(update.effective_chat.id)
    intent_answer = detect_intent_texts(
        project_id, session_id, update.message.text, language_code="ru"
    )
    update.message.reply_text(intent_answer.fulfillment_text)
    logger.info(
        "%s | %s", intent_answer.intent.display_name, intent_answer.fulfillment_text
    )


def main():
    """Start the bot."""
    env = Env()
    env.read_env()

    tg_token = env.str("TG_TOKEN")
    project_id = env.str("DIALOGFLOW_PROJECT_ID")
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command,
            partial(reply_with_dialogflow, project_id=project_id),
        )
    )

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
