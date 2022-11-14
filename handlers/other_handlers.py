from datetime import datetime

from loguru import logger
from telebot.types import Message, CallbackQuery, InputMediaPhoto, ReplyKeyboardRemove
from telegram_bot_calendar import DetailedTelegramCalendar

from config_data.config import LSTEP
from database.data_interaction import add_in_commands, add_in_hotels
from hotel_requests.hot_req import hotel_search, photo_search
from keyboards.inline.inline_kb import button_city
from keyboards.reply.reply_kb import choise_amount, answer
from loader import bot
from states.user_data import UserData


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def input_city(message: Message) -> None:
    """
    Выбор команды пользователем
    :param message: одна из команд, перечисленных в списке content_types
    :return: переход к следующему шагу - клавиатура с выбором нужного района введенноо города
    """
    logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | команда {message.text}')
    bot.set_state(message.from_user.id, UserData.command, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = message.text
        if message.text == '/lowprice':
            data['sorting'] = 'PRICE'
        elif message.text == '/highprice':
            data['sorting'] = 'PRICE_HIGHEST_FIRST'
        elif message.text == '/bestdeal':
            data['sorting'] = 'DISTANCE_FROM_LANDMARK'
    logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | ввод города')
    bot.send_message(message.from_user.id, 'Введите город')


@bot.message_handler(content_types=['text'], state=UserData.command)
def choice_city(message: Message) -> None:
    """
    Выбор города из предоставленного списка после запроса к API гостиницы.
    Настройка текущего состояния пользователя на состояние city_id
    :param message: введенный пользователем город в функции input_city
    :return: ID города или района города и его название
    """
    try:
        cities = button_city(message.text)
        logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | '
                    f'функция {button_city.__name__} возвращает список населенных пунктов')
        if cities:
            logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | выбор населенного пункта')
            bot.set_state(message.from_user.id, UserData.city_id, message.chat.id)
            bot.send_message(message.from_user.id, 'Выберите из списка:', reply_markup=cities)
        else:
            logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | вернулся пустой список')
            bot.send_message(message.from_user.id,
                             'К сожалению, вариантов не найдено. Уточните запрос или введите другой город.')
            bot.register_next_step_handler(message, choice_city)
    except Exception as ex:
        logger.warning(f'Пользователь {message.from_user.full_name} | {message.chat.id} | ошибка: {ex}')
        bot.send_message(message.from_user.id,
                         'К сожалению, вариантов не найдено. Повторите запрос позже или введите другой город.')
        bot.register_next_step_handler(message, choice_city)


@bot.callback_query_handler(func=lambda call: call.data.split(':')[0].isdigit())
def get_city_id(call: CallbackQuery) -> None:
    """
    Ответ на выбор города пользователем, добавление ID и названия города в
    текущее состояния пользователя.
    :param call: ответ пользователя из функции get_city (ID города)
    :return: при состоянии команды '/bestdeal': переход к указанию дистанции(get_distance)
            При других состояниях: переход к выбору даты заезда(choise_in)
    """
    if call.message:
        logger.info(f'Пользователь {call.from_user.full_name} | {call.message.chat.id} | населенный пункт выбран')
        with bot.retrieve_data(call.from_user.id) as data:
            data['city_id'] = call.data.split(':')[0]
            data['city'] = call.data.split(':')[1]
        if data['command'] == '/bestdeal':
            bot.send_message(call.message.chat.id, 'Максимальное расстояние от центра в км')
            bot.set_state(call.message.from_user.id, UserData.distance)
            bot.register_next_step_handler(call.message, get_distance)
        else:
            bot.set_state(call.message.from_user.id, UserData.check_in)
            data['price_range'] = [None, None]
            data['distance'] = None
            choice_in(call.message)


@bot.message_handler(state=UserData.distance)
def get_distance(message: Message) -> None:
    """
    Внесение дистанции в состояние. Ввод пользователем диапазона цен.
    :param message: расстояние от центра, указанное пользователем
    :return: переход к функции get_price_range
    """
    if message.text.isdigit():
        logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | введено расстояние до центра')
        bot.send_message(message.from_user.id,
                         'Введите ценовой диапазон за сутки проживания в руб.(через пробел).')
        bot.set_state(message.from_user.id, UserData.price_range)
        with bot.retrieve_data(message.from_user.id) as data:
            data['distance'] = message.text
            bot.register_next_step_handler(message, get_price_range)
    else:
        logger.warning(f'Пользователь {message.from_user.full_name} | {message.chat.id} | ошибка ввода')
        bot.send_message(message.from_user.id, 'Вы должны ввести число.')
        bot.register_next_step_handler(message, get_distance)


@bot.message_handler(state=UserData.price_range)
def get_price_range(message: Message) -> None:
    """
    Внесение диапазона цен в состояние
    :param message: введенный пользователем диапазон цен
    :return: переход к выбору даты заезда (choice_in)
    """
    range_list = message.text.split(' ')
    if len(range_list) == 2:
        if range_list[0].isdigit() and range_list[1].isdigit():
            logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | введен ценовой диапазон')
            bot.set_state(message.from_user.id, UserData.check_in)
            with bot.retrieve_data(message.from_user.id) as data:
                data['price_range'] = range_list
                choice_in(message)
    else:
        logger.warning(f'Пользователь {message.from_user.full_name} | {message.chat.id} | ошибка ввода')
        bot.send_message(message.from_user.id, 'Вы должны ввести два числа.')


@bot.message_handler(state=UserData.check_in)
def choice_in(message: Message) -> None:
    """
    Выбор даты заезда(год). Настройка состояния пользователя на check_in.
    Переход к выбору месяца и дня заезда.
    """
    logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | выбор даты заезда')
    calendar_in, step = DetailedTelegramCalendar(calendar_id=1,
                                                 locale='ru',
                                                 min_date=datetime.date(datetime.today())).build()
    bot.send_message(message.chat.id,
                     f"Дата заезда: {LSTEP[step]}",
                     reply_markup=calendar_in)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def in_call(call: CallbackQuery) -> None:
    """
    Выбор даты заезда(месяц, день). Внесение даты в текущее состояние пользователя.
    Переход к выбору даты выезда(choice_out)
    """
    if call.message:
        result, key, step = DetailedTelegramCalendar(calendar_id=1,
                                                     locale='ru',
                                                     min_date=datetime.date(datetime.today())).process(call.data)
        if not result and key:
            bot.edit_message_text(f"Дата заезда: {LSTEP[step]}",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=key)
        elif result:
            bot.edit_message_text(f"Дата заезда выбрана: {result.strftime('%d-%m-%Y')}",
                                  call.message.chat.id,
                                  call.message.message_id)
            bot.set_state(call.message.from_user.id, UserData.check_out)
            with bot.retrieve_data(call.from_user.id) as data:
                data['check_in'] = result
                choice_out(call.message)


@bot.message_handler(state=UserData.check_out)
def choice_out(message: Message) -> None:
    """
    Выбор даты заезда(год). Настройка состояния пользователя на check_out.
    Переход к выбору месяца и дня выезда.
    """
    logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | выбор даты выезда')
    calendar_out, step = DetailedTelegramCalendar(calendar_id=2,
                                                  locale='ru',
                                                  min_date=datetime.date(datetime.today())).build()
    bot.send_message(message.chat.id,
                     f"Дата выезда: {LSTEP[step]}",
                     reply_markup=calendar_out)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def out_call(call: CallbackQuery) -> None:
    """
    Выбор даты заезда(месяц, день). Внесение даты в текущее состояние пользователя.
    Вычисление срока проживания и его внесение в состояние пользователя.
    Переход к выбору количества отелей для вывода в результате.
    """
    if call.message:
        with bot.retrieve_data(call.from_user.id) as data:
            result, key, step = DetailedTelegramCalendar(calendar_id=2,
                                                         locale='ru',
                                                         min_date=datetime.date(datetime.today())).process(call.data)
            if not result and key:
                bot.edit_message_text(f"Дата выезда: {LSTEP[step]}",
                                      call.message.chat.id,
                                      call.message.message_id,
                                      reply_markup=key)
            elif result > data['check_in']:
                bot.edit_message_text(f"Дата выезда выбрана: {result.strftime('%d-%m-%Y')}",
                                      call.message.chat.id,
                                      call.message.message_id)
                data['check_out'] = result
                data['period'] = int(str(data['check_out'] - data['check_in']).split()[0])
                bot.send_message(call.from_user.id,
                                 'Сколько отелей вывести в результате?',
                                 reply_markup=choise_amount())
                bot.register_next_step_handler(call.message, get_amount)
            elif result <= data['check_in']:
                logger.warning(f'Пользователь {call.from_user.full_name} | {call.message.chat.id} | ошибка ввода')
                bot.send_message(call.from_user.id, 'Дата должна быть позже даты заезда.')
                choice_out(call.message)


@bot.message_handler(content_types=['text'], state=UserData.check_out)
def get_amount(message: Message) -> None:
    """
    Настройка текущего состояния пользователя на hotel_amount(количество отелей).
    Внесение количества в ссстояние польователя.
    Вывод reply-клавиатуры с уточнением необходимости вывода фото.
    :param message: выбранное пользователем количество отелей для вывода в результат
    """
    logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | получено количество отелей')
    bot.set_state(message.from_user.id, UserData.hotel_amount)
    with bot.retrieve_data(message.from_user.id) as data:
        data['hotel_amount'] = message.text
        bot.send_message(message.from_user.id, 'Выводить фото?', reply_markup=answer())
        bot.register_next_step_handler(message, answer_photo)


@bot.message_handler(content_types=['text'], state=UserData.hotel_amount)
def answer_photo(message: Message) -> None:
    """
    Настройка состояния пользователя на photo_amount.
    Уточнение количества фото в случае необходимости вывода.
    :param message: ответ пользователя на вопрос о необходимости вывода фото.
    """
    bot.set_state(message.from_user.id, UserData.photo_amount)
    if message.text == 'Да':
        logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | получение количества фото')
        bot.send_message(message.from_user.id, 'Сколько фото вывести?', reply_markup=choise_amount())
        bot.register_next_step_handler(message, get_photo)
    elif message.text == 'Нет':
        logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | фото не требуется')
        get_photo(message)


@bot.message_handler(content_types=['text'], state=UserData.photo_amount)
def get_photo(message: Message) -> None:
    """
    Внесение ответа пользователя в текущее состояние.
    Проверка пользователем данных для поиска.
    Reply-кнопки для подтверждения/сброса данных для поиска.
    :param message: ответ пользователя (количество фото/"Нет")
    """
    logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | подтверждение введенных данных')
    with bot.retrieve_data(message.from_user.id) as data:
        data['photo_amount'] = message.text
        text = f"Подтвердите ваши данные:\n" \
               f"\nКоманда: {data['command']}" \
               f"\nМесто поиска: {data['city']}" \
               f"\nCheck-in: {data['check_in'].strftime('%d-%m-%Y')}" \
               f"\nCheck-out: {data['check_out'].strftime('%d-%m-%Y')}" \
               f"\nКоличество отелей: {data['hotel_amount']}" \
               f"\nКоличество ночей: {data['period']}" \
               f"\nФото выводить: {data['photo_amount']}"
        if data['command'] == '/bestdeal':
            text += f"\nРасстояние до центра: {data['distance']}" \
                    f"\nЦеновой диапазон: {'-'.join(data['price_range'])}"
        bot.send_message(message.from_user.id, text, reply_markup=answer())
        bot.register_next_step_handler(message, results)


@bot.message_handler(func=lambda message: message.text in ['Нет', 'Да'])
def results(message: Message) -> None:
    """
    Настройка текущего состояния на None.
    Вывод результатов поиска и внесение данных в БД
    (в случае подтверждения пользователем данных для поиска).
    Так же вывод фото в результате, если не был выбран ответ "Нет".
    В случае неподтверждения пользователем данных бот предлагает начать новый поиск.
    Так же после завершения поиска предлагается начать новый поиск.
    """
    if message.text == 'Нет':
        logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | данные не подтверждены')
    elif message.text == 'Да':
        logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | данные подтверждены')
        bot.send_message(message.from_user.id, 'Выполняется поиск...', reply_markup=ReplyKeyboardRemove())
        with bot.retrieve_data(message.from_user.id) as data:
            hotels_results = hotel_search(city_id=data['city_id'],
                                          check_in=data['check_in'],
                                          check_out=data['check_out'],
                                          sort=data['sorting'],
                                          min_price=data['price_range'][0],
                                          max_price=data['price_range'][1],
                                          distance=data['distance'])
        if hotels_results is not None:
            logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | '
                        f'функция {hotel_search.__name__} возвращает список отелей')
            logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | '
                        f'добавление данных в БД (функция {add_in_commands.__name__})')
            save_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            add_in_commands(chat_id=message.chat.id,
                            time=save_date,
                            command=data['command'],
                            location=data['city'])
            logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | '
                        f'вывод отелей с добавлением в БД (функция {add_in_hotels.__name__})')
            count = 0
            for hotel in hotels_results:
                if count == int(data['hotel_amount']):
                    break
                try:
                    bot.send_message(
                        message.from_user.id,
                        f"Отель: {hotel['name']}\n"
                        f"Звезд: {hotel['starRating']}\n"
                        f"Адрес: {hotel['address']['streetAddress']}\n"
                        f"Расстояние до центра: {hotel['landmarks'][0]['distance']}\n"
                        f"Цена за одну ночь: {hotel['ratePlan']['price']['exactCurrent']}\n"
                        f"Сумма за весь период проживания: {round((hotel['ratePlan']['price']['exactCurrent'] * data['period']), 2)}\n"
                        f"Ссылка на отель: {'https://hotels.com/ho' + str(hotel['id'])}\n",
                        disable_web_page_preview=True
                    )
                    count += 1
                    add_in_hotels(chat_id=message.chat.id,
                                  time=save_date,
                                  name_hotel=hotel['name'],
                                  address=hotel['address']['streetAddress'],
                                  price=hotel['ratePlan']['price']['exactCurrent'],
                                  url_hotel='https://hotels.com/ho' + str(hotel['id']))

                    if data['photo_amount'] != 'Нет':
                        photos_list = photo_search(hotel['id'], int(data['photo_amount']))
                        if photos_list is not None:
                            bot.send_media_group(message.chat.id, [InputMediaPhoto(photo) for photo in photos_list])
                        else:
                            logger.warning(f'Пользователь {message.from_user.full_name} | {message.chat.id} | '
                                           f'ошибка вывода фото гостиницы')
                            bot.send_message(message.from_user.id, 'Фото данной гостиницы не найдены.')
                    else:
                        continue
                except KeyError as ex:
                    logger.warning(f'Пользователь {message.from_user.full_name} | {message.chat.id} | '
                                   f'ошибка вывода гостиницы {ex}')
                    continue
            bot.send_message(message.from_user.id, 'Поиск завершен.')
            logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | вывод отелей завершен')
        else:
            logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | вернулся пустой список')
            bot.send_message(message.from_user.id,
                             'По вашему запросу подходящих вариантов не найдено.')

    logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | сброс состояния')
    bot.set_state(message.from_user.id, None)
    bot.send_message(message.from_user.id,
                     'Для начала нового поиска выберите нужную команду или нажмите /help.',
                     reply_markup=ReplyKeyboardRemove())
