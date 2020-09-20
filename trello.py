import sys
import requests

base_url = "https://api.trello.com/1/{}"
auth_params = {
    'key': "3106fccf2a97c4a6db0e85f17b4b223e",
    'token': "fe5884d20855377b78d4ac905c0d506a02b19bc77bada5b733f0227b83297a7c", }
board_id = "LVWnKMdQ"

board_data = []


def read():
    board_data.clear()

    # Получим данные всех колонок на доске:
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:
    for column in column_data:
        clmn = {'id': column['id'], 'name': column['name'], 'tasks': []}
        board_data.append(clmn)

        # Получим данные всех задач в колонке и перечислим все названия
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in task_data:
            tsk = {'id': task['id'], 'name': task['name']}
            clmn['tasks'].append(tsk)


def print_board_data():
    for clmn in board_data:
        if not clmn['tasks']:
            print(clmn['name'] + ' - 0 задач')
        else:
            print(clmn['name'] + ' - ' + str(len(clmn['tasks'])) + ' задач(и):')
            for tsk in clmn['tasks']:
                print('\t' + tsk['id'] + ' ' + tsk['name'])


def crt_list(name):
    if name:
        response = \
            requests.post(base_url.format('boards') + '/' + board_id + '/lists', data={'name': name, **auth_params})
        if response.status_code == 200:
            print('Колонка "{}" успешно создана'.format(name))


def create(name, column_name):
    # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна
    for clmn in board_data:
        if clmn['name'] == column_name:
            # Создадим задачу с именем _name_ в найденной колонке
            response = requests.post(base_url.format('cards'), data={'name': name, 'idList': clmn['id'], **auth_params})
            if response.status_code == 200:
                print('Задача "{}" в колонке "{}" успешно создана'.format(name, column_name))
            break


def move(id, name, column_name):
    # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу
    for clmn in board_data:
        if clmn['name'] == column_name:
            # И выполним запрос к API для перемещения задачи в нужную колонку
            response = requests.put(base_url.format('cards') + '/' + id + '/idList',
                         data={'value': clmn['id'], **auth_params})
            if response.status_code == 200:
                print('Задача "{}" успешно перенесена в колонку "{}"'.format(name, column_name))
            break


def get_choice(prompt, opts):
    while True:
        print(prompt)
        for i, opt in enumerate(opts.values()):
            print(str(i + 1) + ' - ' + opt)

        try:
            index = int(input())
            if index in range(1, len(opts) + 1):
                return next(k for i, k in enumerate(opts.keys()) if i == index - 1)
        except Exception:
            pass


def get_tasks(name):
    result = {}
    for clmn in board_data:
        for tsk in clmn['tasks']:
            if tsk['name'] == name:
                result[tsk['id']] = tsk['id'] + ' - ' + clmn['name']
    return result


def is_column(col_name):
    for clmn in board_data:
        if clmn['name'] == col_name:
            return True
    return False


if __name__ == "__main__":
    if len(sys.argv) <= 2:
        read()
        print_board_data()
    elif sys.argv[1] == 'create':
        if sys.argv[2] and sys.argv[3]:
            read()
            tasks = get_tasks(sys.argv[2])
            if tasks:
                print('Задача "{}" найдена в колонках:'.format(sys.argv[2]))
                for k in tasks.keys():
                    print(tasks[k])
                opt = get_choice('Выберите опцию:', {1:'Создать задачу', 2:'Не создавать задачу'})
                if opt == 1:
                    create(sys.argv[2], sys.argv[3])
            else:
                create(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'move':
        if sys.argv[2] and sys.argv[3]:
            tsk = ''
            read()
            tasks = get_tasks(sys.argv[2])
            if not tasks:
                print('Задача "{}" не найдена'.format(sys.argv[2]))
            elif len(tasks) == 1:
                tsk = list(tasks.keys())[0]
                move(tsk, sys.argv[2], sys.argv[3])
            elif len(tasks) > 1:
                tsk = get_choice('Найдено несколько задач "{}". Выберите задачу из колонок:'.format(sys.argv[2]), tasks)
                move(tsk, sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'create_column':
        if sys.argv[2]:
            read()
            if is_column(sys.argv[2]):
                print('Колонка "{}" уже есть.'.format(sys.argv[2]))
                opt = get_choice('Выберите опцию:', {1:'Создать колонку', 2:'Не создавать колонку'})
                if opt == 1:
                    crt_list(sys.argv[2])
            else:
                crt_list(sys.argv[2])

