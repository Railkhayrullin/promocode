from django.core.management.base import BaseCommand
from promocode.settings import DEFAULT_PROMOCODE_DIR

from get_code.utils import get_group


class Command(BaseCommand):
    help = 'Проверка промокода на существование в json-файле'

    def add_arguments(self, parser):
        parser.add_argument('-c', '--code', type=str, help='Промокод')

    def handle(self, *args, **kwargs):
        code = kwargs['code']

        # проверяем значение аргумента
        if code in [' ', '']:
            self.stdout.write('Аргумент -c/--code не может быть None или пустой строкой!')
            return

        # получаем None или название группы
        group = get_group(code)
        if group:
            self.stdout.write('код существует группа = {%s}' % group)
        else:
            self.stdout.write('код не существует')
