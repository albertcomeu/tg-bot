import telebot
import requests
import fake_useragent
from bs4 import BeautifulSoup
from telebot import types

token = '########################'
bot = telebot.TeleBot(token)

#кнопка старт
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Одежда')
    item2 = types.KeyboardButton('Обувь')
    markup.add(item1, item2)
    bot.send_message(message.chat.id,'Выберите нужную категорию',reply_markup=markup)

#обработка ввода
@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text=='Одежда':
        bot.send_message(message.chat.id,"Введите название модели: ")
        bot.register_next_step_handler(message, find_model)
    elif message.text == 'Обувь':
        bot.send_message(message.chat.id, "Введите название модели: ")
        bot.register_next_step_handler(message, find_model)

#парсинг
def find_model(message):
    model = message.text

    adidas = 'https://www.adidas.at/' + model

    model = model.replace(' ','+')

    martins = 'https://www.martensosterreich.com/advanced_search_result.html?keyword=' + model

    responsemartins = requests.get(martins)

    soupm = BeautifulSoup(responsemartins.content, 'html5lib')

    mitems = soupm.find_all('div', class_='productNewList')

    if not mitems: bot.send_message(message.chat.id, 'Ничего не найдено((')

    for n, i in enumerate(mitems, start=1):
        itemName = i.find('p', class_ = 'productname').text.strip()
        itemPrice = i.find('span', class_ = 'normalprice').text
        itemSpecialPrice = i.find('span', class_='productSpecialPrice').text
        itemImg = i.find('div', class_='productShowImage')

        itemImg = beautyimg(itemImg)

        print(f'{n}: {itemPrice} ({itemSpecialPrice}) - {itemName} \n{itemImg}')

        itemImg = itemImg.replace(' ','%20')

        if(itemSpecialPrice):
            itemPrice = itemSpecialPrice

        fitemPrice = float(itemPrice[1:])
        extraPrice = int((fitemPrice + (fitemPrice * 20 / 100)) * get_euro() + 1500)

        bot.send_message(message.chat.id,f'{n}. {itemName} \nЦена: {extraPrice}р.')
        bot.send_photo(message.chat.id, 'https://www.martensosterreich.com/' + itemImg)

    bot.register_next_step_handler(message, connect_name)

#обрезка картинки
def beautyimg(itemImg):
    itemImg = str(itemImg)
    itemImg = itemImg[itemImg.find('img src') + 9:itemImg.find('.jpg') + 4]
    return itemImg


def connect_name(message):
    bot.send_message(message.chat.id, 'По поводу оформления пишите @name с пересланым сообщением')



#парсинг курса евро
def get_euro():
    data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    return data['Valute']['EUR']['Value']


bot.infinity_polling()
