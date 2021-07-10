import json
from json import JSONDecodeError

from django.utils.crypto import get_random_string

from promocode.settings import DEFAULT_PROMOCODE_PATH


def get_code(amount, length):
    """Функция для создания уникальных кодов"""
    # генерируем коды
    codes = [get_random_string(length=length) for i in range(amount)]
    while True:
        # преобразуем "list" в "set" чтобы удалить повторяющиеся промокоды
        unique_codes = list(
            set(codes)
        )

        len_unique_codes = len(unique_codes)
        # сравниваем количество кодов и добавляем новый промокод, если кодов в unique_codes меньше, чем в codes
        if amount > len_unique_codes:
            count = amount - len_unique_codes
            codes = unique_codes
            codes += [get_random_string(length=length) for i in range(count)]
        else:
            # если количество кодов равно - останавливаем цикл
            break

    return codes


def check_codes(codes, file_codes, length):
    """Функция для проверки кодов на дубликаты"""
    # создаем список из совпадающих промокодов, одновременно удаляя промокод из списка "codes"
    duplicate_codes = []
    [duplicate_codes.append(codes.pop(i)) for i in range(len(codes)) if codes[i] in file_codes]

    for _ in duplicate_codes:
        while True:
            # в цикле создаем новый промокод
            code = get_random_string(length=length)
            # если промокод не содержится в списке "file_codes", то добавляем его в список "codec"
            if code not in file_codes:
                codes.append(code)
                # останавливаем бесконечный цикл и переходим к следующей итерации
                break
    return codes


def save_json(data, length):
    """Функция для сохранения данных в json"""
    # пробуем открыть файл с промокодами
    try:
        with open(DEFAULT_PROMOCODE_PATH, 'r') as file:
            file_data = json.load(file)

        # если файл существует - читаем в нем существующие промокоды
        file_codes = []
        [file_codes.extend(i['codes']) for i in file_data['data']]

        codes = data['codes']
        group = data['group']

        # сравниваем коды в открытом файле и новые промокоды на уникальность
        unique_codes = check_codes(codes, file_codes, length)
        unique_data = {
            'group': group,
            'codes': unique_codes
        }

        # проверяем есть ли название группы в файле json
        flag = True
        try:

            for i in range(len(file_data['data'])):
                # если название группы есть файле - добавляем промокоды к уже существующей группе
                if file_data['data'][i]['group'] == group:
                    file_data['data'][i]['codes'].extend(unique_codes)
                    flag = False
                    break

            with open(DEFAULT_PROMOCODE_PATH, 'w') as file:
                json.dump(
                    {'data': file_data['data']},
                    file,
                    ensure_ascii=False
                )

        except Exception as exc:
            print(f'Error with code: {exc}')

        if flag:
            # добавляет новые промокоды в конец файла, если одинаковых групп не найдено
            try:
                with open(DEFAULT_PROMOCODE_PATH, 'a') as file:
                    file.seek(file.truncate(file.tell() - 2))
                    file.write(', ' + json.dumps(unique_data, ensure_ascii=False) + ']}')
            except Exception as exc:
                print(f'Error with code: {exc}')

    # если получаем ошибку при открытии - то создаем новый файл и сохраняем туда промокоды
    except (FileNotFoundError, JSONDecodeError):
        try:
            with open(DEFAULT_PROMOCODE_PATH, 'w') as file:
                json.dump(
                    {'data': [data]},
                    file,
                    ensure_ascii=False
                )
        except Exception as exc:
            print(f'Error with code: {exc}')


def get_group(code):
    # читаем содержимое json файла, в котором храняться промокоды
    try:
        with open(DEFAULT_PROMOCODE_PATH, 'r') as file:
            file_data = json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError('File not found')

    group = None
    for item in file_data['data']:
        if code in item['codes']:
            group = item['group']
            break
    return group
