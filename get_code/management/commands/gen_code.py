from django.core.management.base import BaseCommand
from promocode.settings import DEFAULT_PROMOCODE_PATH, DEFAULT_AMOUNT, DEFAULT_PROMOCODE_LENGTH

from get_code.utils import get_code, save_json


class Command(BaseCommand):
    help = 'Создание промокодов для указанной группы'

    def add_arguments(self, parser):
        parser.add_argument('-a', '--amount', type=int, help='Количество создаваемых промокодов')
        parser.add_argument('-g', '--group', type=str, help='Название группы с промокодами')
        parser.add_argument('-l', '--length', type=int, help='Количество символов промокода (в пределах от 6 до 16)')

    def handle(self, *args, **kwargs):
        amount = kwargs['amount']
        group = kwargs['group']
        length = kwargs['length']

        # проверяем значения аргументов
        if amount is None:
            amount = DEFAULT_AMOUNT
        if amount <= 0:
            self.stdout.write('Аргумент -a/--amount может быть только целым положительным числом!')
            return
        if group in ['', ' ']:
            self.stdout.write('Аргумент -g/--group не может быть пустой строкой!')
            return
        if length is None:
            length = DEFAULT_PROMOCODE_LENGTH
        if length < 6 or length > 16:
            self.stdout.write('Аргумент -l/--length может быть только числом в пределах от 6 до 16!')
            return

        # получаем коды
        codes = get_code(amount, length)
        self.stdout.write(f'Промокоды в количестве "{amount} шт" для группы "{group}" успешно созданы!')

        # создаем словарь
        data = {
            'group': group,
            'codes': codes
        }

        # передаем данные в функцию для сохранения
        save_json(data, length)
        self.stdout.write(f'Промокоды сохранены в файл: {DEFAULT_PROMOCODE_PATH}')
