Телеграм-бот @hotel_world_bot для поиска отелей сайта Hotels.com
Данный бот позволяет:

- подбирать отели по самой низкой или высокой цене;
- подбирать отели по лучшему соотношению цена/расстояние от центра города;
- задавать количество выводимых отелей;
- задавать диапазон цен.

Бот написан на Python 3.9. Для работы бота необходимо дополнительно установить библиотеки «Requests» и «pyTelegramBotAPI» Бот использует API "rapidapi.com". Для логирования работы бота используется библиотека loguru. Для работы с БД используется библиотека sqlite3.

Бот состоит из следующих пакетов и модулей:

- "main.py" - основной модуль для запуска скрипта;
- пакет "config_data" содержит следующий модуль:
    - "config.py" – содержит конфигурационные настройки, такие как API key, token для telegram бота и остальные настройки;

- пакет "database" содержит модуль для работы с БД:
    - "data_interaction.py" содержит функцию создания БД и ее таблиц. А так же функции добавления информации в БД и запрос информации для команды "history"
- пакет "handlers" содержит следующие модули:
    - "start.py" - обработчик команды "start";
    - "help.py" - обработчик команды "help";
    - "other_handlers.py" - содержит обработчики команд "lowprice", "highprice", "bestdeal" и другие обработчики;
    - "history.py" - обработчик команды "history": взаимодействует с БД, возвращает результат запроса истории поиска гостиниц
    - "echo.py" - обработчик сообщений без состояния/некорректных;

- пакет "hotel_requests" содержит следующий модуль:
    - "hot_req.py" - содержит функции запросов к API;

- пакет "keyboards" содержит следующие пакеты:
    - пакет "inline" содержит модуль "inline_kb.py" - содержит функцию вывода инлайн-клавиатуры;
    - пакет "reply" содержит модуль "reply_kb.py" - содержит функции вывода реплай-клавиатур;

- пакет "states" содержит следующий модуль:
    - "user_data.py" - содержит класс текущего состояния пользователя;

Начало работы: для запуска бота необходим установленный интерпретатор Python версии 3.9 все остальные пакеты в requirements.txt. Запуск бота в модуле main.py. Нужен файл .env, куда нужно сохранить RAPIDAPI_KEY и токен от вашего бота.
