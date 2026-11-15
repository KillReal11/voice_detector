import logging
from telegram.utils.request import Request
import telegram

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATEFORMAT = "%Y-%m-%d %H:%M:%S"


def create_bot(token, proxy_url=None):
    request_kwargs = {"connect_timeout": 10.0, "read_timeout": 10.0}
    if proxy_url:
        request_kwargs["proxy_url"] = proxy_url
    return telegram.Bot(token=token, request=Request(**request_kwargs))


class TelegramLogsHandler(logging.Handler):
    def __init__(self, bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.bot = bot

    def emit(self, record):
        log_entry = self.format(record)[-4000:]
        try:
            self.bot.send_message(chat_id=self.chat_id, text=log_entry)
        except Exception:
            self.handleError(record)


def configure_logging(logger, env):
    logging.basicConfig(
        format=LOG_FORMAT,
        datefmt=LOG_DATEFORMAT,
        level=logging.INFO
    )
    logger.setLevel(logging.DEBUG)

    token = env.str("TG_LOG_TOKEN", None)
    chat_id = env.str("TG_LOG_CHAT_ID", None)
    proxy_url = env.str("PROXY_SOCKS5", None)
    if not (token and chat_id):
        logger.warning("TG_LOG_TOKEN/TG_LOG_CHAT_ID не заданы, логи в Telegram отключены")
        return

    handler = TelegramLogsHandler(create_bot(token, proxy_url), chat_id)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFORMAT))
    logger.addHandler(handler)
