# Боты службы поддержки на Dialogflow

Два бота, которые отвечают на типовые вопросы пользователей: для Telegram и для VK. Распознаванием вопросов занимается Dialogflow, в боте остаётся только передать ему текст и отправить ответ.

## Демо

| Бот | Ссылка |
|-----|--------|
| Telegram |https://t.me/voice_detector_1_bot|
| VK |https://vk.ru/club243276281|

<img width="517" height="305" alt="tg_demo" src="https://github.com/user-attachments/assets/a2cba6ec-6088-4f81-a7a3-39120bdbcc39" />


## Что делают боты

- **Telegram-бот** (`tg_bot.py`) отвечает на любое текстовое сообщение. Если Dialogflow не понял вопрос, отвечает стандартной фразой агента.
- **VK-бот** (`vk_bot.py`) отвечает в личных сообщениях сообщества. На непонятные вопросы молчит, чтобы на них мог ответить оператор.

Оба бота используют общий модуль `dialogflow_utils.py` и ведут отдельную сессию Dialogflow для каждого пользователя.

## Что такое Dialogflow

[Dialogflow](https://cloud.google.com/dialogflow) это сервис Google для распознавания смысла фраз. В агенте описываются интенты: набор тренировочных фраз («Как устроиться к вам на работу?») и ответ на них. Когда приходит фраза, Dialogflow находит подходящий интент даже при другой формулировке и возвращает ответ. Если подходящего интента нет, срабатывает Default Fallback Intent.

## Установка

Нужен Python 3.11.

```bash
git clone https://github.com/KillReal11/voice_detector
cd voice_detector
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
```

## Настройка

1. Создайте проект в [Google Cloud](https://console.cloud.google.com/) и агента в [Dialogflow ES](https://dialogflow.cloud.google.com/) с языком по умолчанию `ru`.
2. Включите в проекте Dialogflow API.
3. Получите файл с ключами для доступа к API: `gcloud auth application-default login`.
4. Создайте бота в Telegram через [@BotFather](https://t.me/BotFather) и токен сообщества в VK (с правом на отправку сообщений).
5. Создайте файл `.env` рядом с кодом:

```
TG_TOKEN=токен_телеграм_бота
VK_TOKEN=токен_сообщества_vk
DIALOGFLOW_PROJECT_ID=id_проекта_в_google_cloud
GOOGLE_APPLICATION_CREDENTIALS=путь/к/файлу/с/ключами.json
TG_LOG_CHAT_ID=ваш_телеграмм_id
TG_LOG_TOKEN=токен_телеграм_бота_для_отправки_логов
```

## Загрузка интентов

Вопросы и ответы лежат в `questions.json`. Формат:

```json
{
  "Название интента": {
    "questions": ["Фраза 1", "Фраза 2"],
    "answer": "Текст ответа"
  }
}
```

Скрипт настроен только на создание интента "Устройство на работу". Чтобы создать из него интент в агенте:

```bash
python create_intent.py
```



## Запуск

```bash
python tg_bot.py
python vk_bot.py
```

Боты запускаются отдельными процессами.
