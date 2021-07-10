import re
import os
import json
from io import StringIO
from django.test import TestCase
from django.core.management import call_command

from promocode.settings import DEFAULT_PROMOCODE_PATH, DEFAULT_PROMOCODE_LENGTH


class CommandsTestCase(TestCase):
    def test_command_gen_code(self):
        """Проверка комманды gen_code (генерации промокодов)"""

        # если json файл с промокодами существует, то удаляем его
        if os.path.exists(DEFAULT_PROMOCODE_PATH):
            os.remove(DEFAULT_PROMOCODE_PATH)

        # вызываем комманды с тестовыми атрибутами
        call_command('gen_code', **{'amount': 10,
                                    'group': 'агенства'})
        call_command('gen_code', **{'amount': 1,
                                    "group": 'агенства'})
        call_command('gen_code', **{'amount': 42,
                                    'group': 'avtostop'})
        call_command('gen_code', **{'amount': 5,
                                    'group': '1',
                                    'length': 15})

        # открываем созданный json файл
        with open(DEFAULT_PROMOCODE_PATH) as file:
            file_data = json.load(file)

        # создаем список из созданных групп и промокодов
        groups = [i['group'] for i in file_data['data']]
        codes = []
        [codes.extend(i['codes']) for i in file_data['data']]

        # удаляем созданный json файл
        # os.remove(DEFAULT_PROMOCODE_PATH)

        # проверяем, что количество групп равно 3 (при генерации кодов две одинаковые группы должны были объединиться)
        self.assertEqual(len(groups), 3)

        # проверяем, что количество промокодов равно 58
        self.assertEqual(len(codes), 58)

        # проверяем, что длина промокодов групп "агенства" и "avtostop" равна DEFAULT_PROMOCODE_LENGTH
        for code in codes[:53]:
            self.assertEqual(len(code), DEFAULT_PROMOCODE_LENGTH)

        # проверяем, что длина промокодов из последней группы равна 15
        for code in codes[53:]:
            self.assertEqual(len(code), 15)

    def test_command_get_group(self):
        """Проверка комманды get_group (поиск группы по промокоду)"""

        # открываем созданный json файл
        with open(DEFAULT_PROMOCODE_PATH) as file:
            file_data = json.load(file)

        # создаем список из названий групп, которые должны получиться в json файле
        groups = ['агенства', 'avtostop', '1']
        files = file_data['data']

        # паттерн для поиска названия группы из вывода команды
        pattern = '([^{]*?)(?=\})'

        # проверим каждый промокод на принадлежность к группе
        for i in range(len(files)):
            for code in files[i]['codes']:
                out = StringIO()
                call_command('get_group', **{'code': code}, stdout=out)
                value = re.search(pattern, out.getvalue()).group()
                group = groups[i]
                self.assertEqual(value, groups[i])

        # удаляем созданный json файл
        os.remove(DEFAULT_PROMOCODE_PATH)
