#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from dbworker import DBWorker
import random

db = DBWorker("db_file.db")


class States(StatesGroup):
    waiting_for_players_list = State()
    waiting_for_teams_number = State()
    waiting_for_user_confirm = State()


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    if not db.user_exist(message.from_user.id):
        db.add_user(message.from_user.id)
        await message.answer(f'Привет, {message.from_user.first_name}! \
        \nЯ смотрю ты тут впервые, добро пожаловать! \
        \nДавай разделим твою компанию на команды. \
        \nЧтобы начать используй команду /begin')

    else:
        await message.answer(f'Привет, {message.from_user.first_name}, с возвращением! \
        \nДавай разделим твою компанию на команды. \
        \nЧтобы начать используй команду /begin')


async def cmd_begin(message: types.Message, state: FSMContext):
    if not db.user_exist(message.from_user.id):
        db.add_user(message.from_user.id)
    await state.finish()
    await message.answer(f"Перечисли, пожалуйста, через запятую, имена людей, которые будут играть.")
    await States.waiting_for_players_list.set()


async def get_players_names(message: types.Message, state: FSMContext):
    s = message.text.replace(', ', ',').title().split(',')
    if len(s) == 1:
        await message.answer(f"Один в поле не воин, зови друзей.")
        return
    elif len(s) == 2:
        await message.answer(f"Вас двое, боюсь мои услуги бесполезны, зовите друзей и возвращайтесь.")
        return
    elif len(s) > 2:
        await state.update_data(players_list=s)
        await message.answer(f"Отлично, скажи, пожалуйста, на сколько команд вас разделить?")
        await States.next()
        print(s)
        return s


async def get_teams_number(message: types.Message, state: FSMContext):
    a = [str(i) for i in range(1, 100)]
    if message.text not in a:
        await message.answer(f"Введи число, пожалуйста)")
        return
    else:
        k = int(message.text)
        await state.update_data(teams_number=k)
        await magic(message, state)


async def magic(message, state):
    k = await state.get_data()
    k = k["teams_number"]
    s = await state.get_data()
    s = s["players_list"]
    n = len(s)
    if k > n:
        await message.answer(f"Ничего не выйдет, количество команд больше чем количество игроков, попробуй еще раз.")
        await States.waiting_for_teams_number.set()
        return
    # Формирование списка для распределения по командам
    f = []
    # Формирование проверочного списка
    p = []
    # Перемешиваем список \ выясняем количество игроков в командах
    random.shuffle(s)
    nk = round(n / k)
    t = 1
    # Очистка проверочного списка
    p.clear()
    # Формируем списки команд
    for i in s:
        f.append(i)
        p.append(i)
        if len(f) == nk:
            await message.answer(f"Игроки команды " + str(t) + ":\n" + "\n".join(f))
            f.clear()
            # Условия неравномерного распеределения игроков по командам (7 игроков 3 команды и тд)
            if n % k != 0:
                if k * nk > n and nk - 1 != 1 and (len(s) - len(p)) % (nk - 1) == 0:
                    nk -= 1
                elif k * nk > n and n - k == 2 and (len(s) - len(p)) % (nk - 1) == 0:
                    nk -= 1
                elif n - k != 1 and (len(s) - len(p)) % (nk + 1) == 0:
                    nk += 1
                elif n - k == 1 and (len(s) - len(p)) == 2:
                    nk += 1
            t += 1
    await message.answer(f"Хотите изменить состав команд?")
    await States.waiting_for_user_confirm.set()


async def user_confirm(message: types.Message, state: FSMContext):
    if message.text.lower() == "нет":
        await message.answer(f"Если буду нужен, ты знаешь где меня найти, удачи)")
        await state.finish()
    elif message.text.lower() == "да":
        await magic(message, state)
    else:
        await message.answer(f"Дак да или нет?)")
        return


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(f"Хорошо, начнем сначала.")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_start, Text(equals="привет", ignore_case=True), state="*")
    dp.register_message_handler(cmd_begin, commands="begin", state="*")
    dp.register_message_handler(get_players_names, state=States.waiting_for_players_list)
    dp.register_message_handler(get_teams_number, state=States.waiting_for_teams_number)
    dp.register_message_handler(user_confirm, state=States.waiting_for_user_confirm)
