import sqlite3 as sql
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from sql import create_table_person, create_table_mobs, create_table_locations, create_table_items, create_table_inventory
# from .game import
import random as rnd

'''
11 - Покровка
12 - Ровесник
13 - МГУ
'''

db = sql.connect('db.db')
sql = db.cursor()
bot = Bot(token='')
dp = Dispatcher(bot)

create_table_person()
create_table_mobs()
create_table_locations()
create_table_items()
create_table_inventory()



@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    sql.execute(f"DELETE FROM person WHERE UserID = {message.from_user.id}")
    sql.execute(
        f"INSERT INTO person (UserID, Nickname) VALUES ({message.from_user.id}, '{message.from_user.username}')")
    db.commit()
    await message.answer(f"Hello, {message.from_user.username}!")


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer('Бот для ДЗ-4 по курсу Advanced Python')


@dp.message_handler(commands=['stats'])
async def stats(message: types.Message):
    sql.execute(f"SELECT Nickname, Level, HP, CurHP, Money, Attack, MagicAttack, XP, Armour, MagicArmour, LocationID"
                f" FROM person WHERE UserID = {message.from_user.id}")
    data = sql.fetchone()
    sql.execute(f"SELECT LocationName, LocationType FROM locations WHERE LocationID = {data[-1]}")
    location = sql.fetchone()
    await message.answer(f"Nickname: {data[0]}, Level: {data[1]}, HP: {data[2]}, CurHP: {data[3]}, Money: {data[4]},"
                         f" Attack: {data[5]}, MagicAttack: {data[6]}, XP: {data[7]}, Armour: {data[8]},"
                         f" MagicArmour: {data[9]}, Location: {location[0]} ({location[1]})")


async def attack_mob_again(message, db):
    db.execute(f"select MobId, CurHP from person where UserID = {message.chat.id}")
    mob_id, CurHP = db.fetchall()[0]
    db.execute(f"select AttackType, Attack from mobs where MobID = {mob_id}")
    AttackType, Attack = db.fetchall()[0]
    new_hp = CurHP - Attack
    if new_hp < 1:
        db.execute(f"update person set CurHP = 0 where UserID = {message.chat.id}")
        db.commit()
        return "Ценок"
    db.execute(f"update person set CurHP = {new_hp} where UserID = {message.chat.id}")
    return new_hp


@dp.callback_query_handler(text_contains='attack')
async def attack(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=4)
    item = types.InlineKeyboardButton(f"physical", callback_data=f"physical")
    markup.row(item)
    item = types.InlineKeyboardButton(f"magic", callback_data=f"magic")
    markup.row(item)
    await call.message.answer(text="Тип атаки:", reply_markup=markup)


@dp.callback_query_handler(text_contains='physical')
async def physical(call: types.CallbackQuery):
    sql.execute(f"SELECT LocationID, MobId, MobHP, Attack, MagicAttack, Money, XP, HP FROM person WHERE "
                f"UserID = {call.message.chat.id}")
    LocationID, mob_id, MobHP, Attack, MagicAttack, Money, XP, HP = sql.fetchall()[0]
    db.execute(f"select Armour, MagicArmour, XP from mobs where MobID = {mob_id}")
    Armour, MagicArmour, MobXP = db.fetchall()[0]
    MobHP -= Attack - Armour
    db.execute(f"update person set MobHP = {MobHP} where UserID = {call.message.chat.id}")
    db.commit()
    if MobHP > 0:
        await call.message.answer(text="Mob ramain hp:" + " " + str(MobHP))
        await attack_mob_again(call, db)
    else:
        db.execute(f"select Money, XP from person where UserID = {call.message.chat.id}")
        Money, XP = db.fetchall()[0]
        Money += Money
        XP += MobXP
        db.execute(f"update person set Money = {Money}, XP = {XP} where UserID = {call.message.chat.id}")
        db.commit()
        await call.message.answer(text="Mob dead")
        if XP > 100:
            db.execute(f"select Level from person where UserID = {call.message.chat.id}")
            Level = db.fetchall()[0][0]
            Level += 1
            db.execute(
                f"update person set Level = {Level}, XP = 0, HP = {HP + 5}, Attack = {Attack + 5}, Armour = {Armour + 5}"
                f"Money = {Money + 100} where UserID = {call.message.chat.id}")
            db.commit()
            await call.message.answer(text="Level UP")
        db.execute(f"SELECT Money FROM person WHERE UserID = {call.message.chat.id}")
        Money = db.fetchall()[0][0]
        reward = rnd.randint(1, 100)
        Money += reward
        db.execute(f"UPDATE person SET Money = {Money} WHERE UserID = {call.message.chat.id}")
        db.commit()
        await call.message.answer(text=f"Вы получили {reward} монет")
        db.execute(f"UPDATE person SET LocationID = 11 WHERE UserID = {call.message.chat.id}")
        db.commit()
        await call.message.answer(text="Вы отправились на Покровку")


@dp.callback_query_handler(text_contains='magic')
async def magic(call: types.CallbackQuery):
    db.execute(f"select LocationID, MobId, MobHP, Attack, MagicAttack, Money, XP, HP from person where "
               f"UserID = {call.message.chat.id}")
    LocationID, mob_id, MobHP, Attack, MagicAttack, Money, XP, HP = db.fetchall()[0]
    db.execute(f"select Armour, MagicArmour, XP from mobs where MobID = {mob_id}")
    Armour, MagicArmour, MobXP = db.fetchall()[0]
    MobHP -= MagicAttack - MagicArmour
    db.execute(f"update person set MobHP = {MobHP} where UserID = {call.message.chat.id}")
    db.commit()
    if MobHP > 0:
        await call.message.answer(text="Mob ramain hp:" + " " + str(MobHP))
        await attack_mob_again(call, db)
    else:
        db.execute(f"select Money, XP from person where UserID = {call.message.chat.id}")
        Money, XP = db.fetchall()[0]
        Money += Money
        XP += MobXP
        db.execute(f"update person set Money = {Money}, XP = {XP} where UserID = {call.message.chat.id}")
        db.commit()
        await call.message.answer(text="Mob dead")
        if XP > 100:
            db.execute(f"select Level from person where UserID = {call.message.chat.id}")
            Level = db.fetchall()[0][0]
            Level += 1
            db.execute(
                f"update person set Level = {Level}, XP = 0, HP = {HP + 5}, Attack = {Attack + 5}, Armour = {Armour + 5}"
                f"Money = {Money + 100} where UserID = {call.message.chat.id}")
            db.commit()
            await call.message.answer(text="Level UP")
        db.execute(f"SELECT Money FROM person WHERE UserID = {call.message.chat.id}")
        Money = db.fetchall()[0][0]
        reward = rnd.randint(1, 100)
        Money += reward
        db.execute(f"UPDATE person SET Money = {Money} WHERE UserID = {call.message.chat.id}")
        db.commit()
        await call.message.answer(text=f"Вы получили {reward} монет")
        db.execute(f"UPDATE person SET LocationID = 11 WHERE UserID = {call.message.chat.id}")
        db.commit()


@dp.message_handler(commands=['location_list'])
async def location_list(message: types.Message):
    db.execute(f"SELECT LocationID, LocationName, XCoord, YCoord FROM locations")
    LocationID, LocationName, XCoord, YCoord = db.fetchall()[0]
    s = ""
    for i in range(len(LocationID)):
        s += f"ID: {LocationID[i]} Name:{LocationName[i]} XCoord:{XCoord[i]} YCoord:{YCoord[i]}"
    await message.answer(text=s)


@dp.message_handler(commands=['travel'])
async def travel(message: types.Message):
    sql.execute(f"SELECT LocationID, LocationName FROM locations")
    # location_id, location_name = sql.fetchall()[0]
    tmp = sql.fetchall()
    location_id = []
    location_name = []
    for i in tmp:
        location_id.append(i[0])
        location_name.append(i[1])
    markup = types.InlineKeyboardMarkup(row_width=3)
    for i in range(len(location_id)):
        item = types.InlineKeyboardButton(location_name[i], callback_data=f"travel_{location_id[i]}")
        markup.row(item)
    await message.answer(text="Выберите локацию", reply_markup=markup)


@dp.callback_query_handler(text_contains=['travel_11'])
async def travel_11(call: types.CallbackQuery):
    sql.execute(f"SELECT LocationID FROM person WHERE UserID = {call.message.chat.id}")
    LocationID = sql.fetchall()[0][0]
    sql.execute(f"SELECT XCoord, YCoord FROM locations WHERE LocationID = {LocationID}")
    XCoord, YCoord = sql.fetchall()[0]
    sql.execute(f"UPDATE person SET LocationID = 11 WHERE UserID = {call.message.chat.id}")
    db.commit()
    length = (abs(XCoord - 100) * abs(XCoord - 100) + abs(YCoord - 50) * abs(YCoord - 50)) ** 0.5
    for i in range(int(length), 0, -40):
        await asyncio.sleep(1)
        await call.message.answer(text="Осталось пройти:" + " " + str(i) + " " + "метров")
    await call.message.answer(text="Вы на Покровке")


@dp.callback_query_handler(text_contains=['travel_12'])
async def travel_12(call: types.CallbackQuery):
    sql.execute(f"SELECT LocationID FROM person WHERE UserID = {call.message.chat.id}")
    LocationID = sql.fetchall()[0][0]
    sql.execute(f"SELECT XCoord, YCoord FROM locations WHERE LocationID = {LocationID}")
    XCoord, YCoord = sql.fetchall()[0]
    sql.execute(f"UPDATE person SET LocationID = 12 WHERE UserID = {call.message.chat.id}")
    db.commit()
    length = (abs(XCoord - 200) * abs(XCoord - 200) + abs(YCoord - 200) * abs(YCoord - 200)) ** 0.5
    for i in range(int(length), 0, -40):
        await asyncio.sleep(1)
        await call.message.answer(text="Осталось пройти:" + " " + str(i) + " " + "метров")
    await call.message.answer(text="Вы в Ровеснике")


@dp.callback_query_handler(text_contains=['travel_13'])
async def travel_13(call: types.CallbackQuery):
    sql.execute(f"SELECT LocationID FROM person WHERE UserID = {call.message.chat.id}")
    LocationID = sql.fetchall()[0][0]
    sql.execute(f"SELECT XCoord, YCoord FROM locations WHERE LocationID = {LocationID}")
    XCoord, YCoord = sql.fetchall()[0]
    sql.execute(f"UPDATE person SET LocationID = 13 WHERE UserID = {call.message.chat.id}")
    db.commit()
    length = (abs(XCoord - 0) * abs(XCoord - 0) + abs(YCoord - 10) * abs(YCoord - 10)) ** 0.5
    for i in range(int(length), 0, -40):
        await asyncio.sleep(1)
        await call.message.answer(text="Осталось пройти:" + " " + str(i) + " " + "метров")
    await call.message.answer(text="Вы в подземельях МГУ")


@dp.message_handler(commands=['inventory'])
async def inventory(message: types.Message):
    sql.execute(f"SELECT ItemID, Used FROM inventory WHERE UserID = {message.chat.id}")
    cur_inventory = sql.fetchall()
    if cur_inventory == []:
        await message.answer(text="Ваш инвентарь пуст")
    else:
        s = ""
        for i in cur_inventory:
            sql.execute(f"SELECT ItemName, ItemType FROM items WHERE ItemID = {i[0]}")
            ItemName, ItemType = sql.fetchall()[0]
            s += f"ID: {i[0]} Name: {ItemName} Description: {ItemType} Used: {i[1]}\n"
        await message.answer(text=s)


@dp.message_handler(commands=['use_item'])
async def use_item(message: types.Message):
    sql.execute(f"SELECT ItemID, Used FROM inventory WHERE UserID = {message.chat.id}")
    cur_inventory = sql.fetchall()
    if cur_inventory == []:
        await message.answer(text="Ваш инвентарь пуст")
    else:
        sql.execute(f"SELECT ItemID FROM Inventory WHERE UserID = {message.chat.id} AND Used = 0")
        tmp = sql.fetchall()
        item_id = []
        for i in tmp:
            item_id.append(i[0])
        markup = types.InlineKeyboardMarkup(row_width=3)
        for i in range(len(item_id)):
            item = types.InlineKeyboardButton(str(item_id[i]), callback_data=f"use_item_{item_id[i]}")
            markup.row(item)
        await message.answer(text="Выберите предмет", reply_markup=markup)


@dp.callback_query_handler(text_contains=['use_item_'])
async def use_item_(call: types.CallbackQuery):
    item_id = int(call.data[9:])
    sql.execute(f"SELECT ItemName, ItemDescription FROM items WHERE ItemID = {item_id}")
    ItemName, ItemDescription = sql.fetchall()[0]
    await call.message.answer(text=f"Вы надели {ItemName}")
    sql.execute(f"UPDATE inventory SET Used = 1 WHERE ItemID = {item_id}")
    db.commit()


@dp.message_handler(commands=['drop_item'])
async def drop_item(message: types.Message):
    sql.execute(f"SELECT ItemID, Used FROM inventory WHERE UserID = {message.chat.id}")
    cur_inventory = sql.fetchall()
    if cur_inventory == []:
        await message.answer(text="Ваш инвентарь пуст")
    else:
        sql.execute(f"SELECT ItemID FROM Inventory WHERE UserID = {message.chat.id} AND Used = 0")
        tmp = sql.fetchall()
        item_id = []
        for i in tmp:
            item_id.append(i[0])
        markup = types.InlineKeyboardMarkup(row_width=3)
        for i in range(len(item_id)):
            item = types.InlineKeyboardButton(str(item_id[i]), callback_data=f"drop_item_{item_id[i]}")
            markup.row(item)
        await message.answer(text="Выберите предмет", reply_markup=markup)


@dp.callback_query_handler(text_contains=['drop_item_'])
async def drop_item_(call: types.CallbackQuery):
    item_id = int(call.data[10:])
    sql.execute(f"SELECT ItemName, ItemDescription FROM items WHERE ItemID = {item_id}")
    ItemName, ItemDescription = sql.fetchall()[0]
    await call.message.answer(text=f"Вы выбросили {ItemName}")
    sql.execute(f"DELETE FROM inventory WHERE ItemID = {item_id}")
    db.commit()

@dp.message_handler(commands=['buy_complex'])
async def buy_complex(message: types.Message):
    sql.execute(f"SELECT LocationID FROM person WHERE UserID = {message.chat.id}")
    LocationID = sql.fetchall()[0][0]
    sql.execute(f"SELECT LocationName FROM locations WHERE LocationID = {LocationID}")
    LocationName = sql.fetchall()[0][0]
    if LocationName == "Покровка":
        sql.execute(f"SELECT Money FROM person WHERE UserID = {message.chat.id}")
        Money = sql.fetchall()[0][0]
        if Money >= 10:
            await message.answer(text="Вы купили комплекс")
            sql.execute(f"UPDATE person SET Money = Money - 10, HP = HP + 10, Armour = Armour + 100, MagicArmour = MagicArmour + 100"
                        f" WHERE UserID = {message.chat.id}")
            db.commit()
            sql.execute(f"INSERT INTO inventory (UserID, ItemID, Used) VALUES ({message.chat.id}, 222, 1)")
            db.commit()
        else:
            await message.answer(text="У вас недостаточно денег")
    else:
        await message.answer(text="Вы не можете купить комплекс не на Покровке")


@dp.message_handler(commands=['buy_beluga'])
async def buy_beluga(message: types.Message):
    sql.execute(f"SELECT LocationID FROM person WHERE UserID = {message.chat.id}")
    LocationID = sql.fetchall()[0][0]
    sql.execute(f"SELECT LocationName FROM locations WHERE LocationID = {LocationID}")
    LocationName = sql.fetchall()[0][0]
    if LocationName == "Ровесник":
        sql.execute(f"SELECT Money FROM person WHERE UserID = {message.chat.id}")
        Money = sql.fetchall()[0][0]
        if Money >= 10:
            await message.answer(text="Вы купили белугу")
            sql.execute(f"UPDATE person SET Money = Money - 10, HP = HP + 50, Armour = Armour + 10, MagicArmour = MagicArmour + 10"
                        f" WHERE UserID = {message.chat.id}")
            db.commit()
            sql.execute(f"INSERT INTO inventory (UserID, ItemID, Used) VALUES ({message.chat.id}, 223, 1)")
            db.commit()
        else:
            await message.answer(text="У вас недостаточно денег")
    else:
        await message.answer(text="Вы не можете купить белугу не в Ровеснике")

@dp.message_handler(commands=['get_marker'])
async def get_marker(message: types.Message):
    sql.execute(f"SELECT LocationID FROM person WHERE UserID = {message.chat.id}")
    LocationID = sql.fetchall()[0][0]
    sql.execute(f"SELECT LocationName FROM locations WHERE LocationID = {LocationID}")
    LocationName = sql.fetchall()[0][0]
    if LocationName == "Покровка":
        sql.execute(f"SELECT Money FROM person WHERE UserID = {message.chat.id}")
        Money = sql.fetchall()[0][0]
        if Money >= 0:
            await message.answer(text="Вы забрали маркер")
            sql.execute(f"UPDATE person SET Attack = Attack + 15, MagicAttack = MagicAttack + 15"
                        f" WHERE UserID = {message.chat.id}")
            db.commit()
            sql.execute(f"INSERT INTO inventory (UserID, ItemID, Used) VALUES ({message.chat.id}, 224, 1)")
            db.commit()
    else:
        await message.answer(text="Вы не можете купить маркер не на Покровке")


@dp.message_handler(commands=['get_eraser'])
async def get_eraser(message: types.Message):
    sql.execute(f"SELECT LocationID FROM person WHERE UserID = {message.chat.id}")
    LocationID = sql.fetchall()[0][0]
    sql.execute(f"SELECT LocationName FROM locations WHERE LocationID = {LocationID}")
    LocationName = sql.fetchall()[0][0]
    if LocationName == "Покровка":
        sql.execute(f"SELECT Money FROM person WHERE UserID = {message.chat.id}")
        Money = sql.fetchall()[0][0]
        if Money >= 0:
            await message.answer(text="Вы забрали стёрку")
            sql.execute(f"UPDATE person SET Defence = Defence + 15, MagicDefence = MagicDefence + 15"
                        f" WHERE UserID = {message.chat.id}")
            db.commit()
            sql.execute(f"INSERT INTO inventory (UserID, ItemID, Used) VALUES ({message.chat.id}, 225, 1)")
            db.commit()
    else:
        await message.answer(text="Вы не можете забрать стёрку не на Покровке")

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
