import config
import keyboards
import file_creator
import telebot
import time
import json
from commercial_offer import CommercialOffer
from random import choice

bot = telebot.TeleBot(config.TOKEN)

co_dict = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        'Привет!\nЭтот бот написан для создания коммерческих предложений с сайта ТОВ "КОМПАНІЯ УКРБЕЗПЕКА": https://ukrbezpeka.com/, нажми "Начать создание КП" для старта.',
        reply_markup=keyboards.keyboard1
    )
    bot.send_message(
        message.chat.id,
        'Пробный период - 5 коммерческих предложений',
        reply_markup=keyboards.keyboard1
    )
    print('Пользователь {0} подписался на бота'.format(str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)))
    users = load_db()
    if message.from_user.id not in [user['id'] for user in users]:
        users.append(
            {
                'first_name': str(message.from_user.first_name),
                'last_name': str(message.from_user.last_name),
                'id': message.from_user.id,
                'trial': 'yes',
                'co_amount': 0
            }
        )
        write_db(users)

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(
        message.chat.id,
        'Привет!\nЭтот бот написан для создания коммерческих предложений с сайта ТОВ "КОМПАНІЯ УКРБЕЗПЕКА": https://ukrbezpeka.com/, нажми "Начать создание КП" для старта.',
        reply_markup=keyboards.keyboard1
    )
    print('Пользователь {0} запросил команду "/help"'.format(str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)))

@bot.message_handler(content_types=['text'])
def message_reader(message):
    global co_dict
    if message.text == 'Начать создание КП':
        co_dict[message.from_user.id] = CommercialOffer()
        bot.send_message(
            message.chat.id,
            'Итак, мы начали создание коммерческого предложения, для добавления вставляй ссылку на товар и через " - " указывай количество.',
            reply_markup=keyboards.keyboard2
        )
        print('Пользователь {0} начал создание КП'.format(str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)))
        bot.register_next_step_handler(message, add_card)
    else:
        bot.send_message(
            message.chat.id,
            'Ошибка! Для начала нужно нажать "Начать создание КП"',
            reply_markup=keyboards.keyboard1
        )
        print('Ошибка! Пользователь {0} допустил ошибку'.format(str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)))

def add_card(message):
    global co_dict
    if message.text == 'Добавлены все позиции' and co_dict[message.from_user.id].card_number > 0:
        bot.send_message(
            message.chat.id,
            'Отлично! Теперь напиши стоимость работ.',
            reply_markup=keyboards.keyboard3
        )
        print('Пользователь {0} добавил все позиции'.format(str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)))
        bot.register_next_step_handler(message, add_work_cost)
    elif message.text == 'Добавлены все позиции' and co_dict[message.from_user.id].card_number == 0:
        bot.send_message(
            message.chat.id,
            'Ошибка! Не было добавлено ниодной позиции',
            reply_markup=keyboards.keyboard2            
        )
        print('Ошибка! Пользователь {0} допустил ошибку'.format(str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)))
        bot.register_next_step_handler(message, add_card)
    elif message.text == 'Отмена':
        del co_dict[message.from_user.id]
        bot.send_message(
            message.chat.id,
            'Ок, создание файла прервано, для начала нажми "Начать создание КП".',
            reply_markup=keyboards.keyboard1
        )
        print('Пользователь {0} отменил создание КП'.format(str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)))
    else:
        try:
            co_dict[message.from_user.id].add_card(message.text)
            bot.send_message(
                message.chat.id,
                choice(['Принято, дальше...', 'Есть, добавил...', 'Отлично, далее...']),
                reply_markup=keyboards.keyboard2
            )
            print('Пользователь {0} добавил очередную позицию'.format(str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)))
        except:
            bot.send_message(
                message.chat.id,
                'Ошибка! Ты ввел что-то не то или как-то не так',
                reply_markup=keyboards.keyboard2
            )
            print('Ошибка! Пользователь {0} допустил ошибку'.format(str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)))
        bot.register_next_step_handler(message, add_card)

def add_work_cost(message):
    global co_dict
    if message.text == 'Отмена':
        del co_dict[message.from_user.id]
        bot.send_message(
            message.chat.id,
            'Ок, создание файла прервано, для начала нажми "Начать создание КП".',
            reply_markup=keyboards.keyboard1
        )
        print('Пользователь {0} отменил создание КП'.format(str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)))
    else:
        try:
            co_dict[message.from_user.id].work_cost = int(message.text)
            print('Пользователь {0} добавил стоимость работ'.format(str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)))
            users = load_db()            
            for user in users:
                if user['id'] == message.from_user.id:
                    if user['trial'] == 'no':
                        user['co_amount'] += 1
                        write_db(users)
                        create_file(message)
                    elif user['trial'] == 'yes' and user['co_amount'] < config.TRIAL:
                        user['co_amount'] += 1
                        write_db(users)
                        create_file(message)
                    else:
                        bot.send_message(
                            message.chat.id,
                            'Пробный режим закончен, для продолжения свяжись с администратором бота.',
                            reply_markup=keyboards.keyboard1
                        )
            del co_dict[message.from_user.id]
        except:
            bot.send_message(
                message.chat.id,
                'Ошибка! Это должно быть просто число',
                reply_markup=keyboards.keyboard3
            )
            print('Ошибка! Пользователь {0} допустил ошибку'.format(str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)))
            bot.register_next_step_handler(message, add_work_cost)

def create_file(message):
    global co_dict
    cards = co_dict[message.from_user.id].cards
    work_cost = co_dict[message.from_user.id].work_cost
    try:
        co_file = file_creator.create_file(
            cards,
            work_cost
        )
        bot.send_document(
            message.chat.id,
            co_file
        )
        bot.send_message(
                message.chat.id,
                'Отлично! Файл создан!',
                reply_markup=keyboards.keyboard1
            )
        print('Пользователь {0} создал КП'.format(str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)))
    except:
        bot.send_message(
            message.chat.id,
            'Ошибка! При записи файла произошла ошибка',
            reply_markup=keyboards.keyboard1
        )
        print('Ошибка! При записи КП пользователя {0} произошла ошибка'.format(str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)))

def load_db():
    try:
        users = json.load(open('db/db.json', 'r'))
        print('БД загружена успешно')
        return users
    except:
        print('Ошибка! При загрузке БД произошла ошибка')

def write_db(users):
    try:
        with open('db/db.json', 'w') as db_file:
            json.dump(users, db_file, indent=2, ensure_ascii=False)
        print('БД записана успешно')
    except:
        print('Ошибка! При записи БД произошла ошибка')

while True:
    try:
        bot.polling(none_stop=True, interval=2)
        break
    except telebot.apihelper.ApiException as e:
        bot.stop_polling()
        time.sleep(15)
