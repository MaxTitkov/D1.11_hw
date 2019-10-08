from trello_token import API_KEY, API_TOKEN, BOARD_ID
import requests, sys, collections

auth_params = {
	"key": API_KEY,
	"token": API_TOKEN,
}

board_id = BOARD_ID

base_url = "https://api.trello.com/1/{}"

def read():
	column_data = requests.get(base_url.format("boards") + "/" + board_id + "/lists", params=auth_params).json()
	trello_data = collections.defaultdict(list)
	tasks_counter = collections.Counter()
  
	for column in column_data:
		tasks_list = requests.get(base_url.format("lists") + "/" + column['id'] + "/cards", params=auth_params).json()
		if not tasks_list:
			trello_data[column["name"]].append('Нет задач')
			tasks_counter[column["name"]] = 0
			continue

		for task in tasks_list:
			tasks_counter[column["name"]] += 1
			trello_data[column["name"]].append(task['name'])
    
	for column in tasks_counter:
		print(tasks_counter[column], column)
		[print("\t"+ task) for task in trello_data[column]] 

def create(name, column_name):            
	column_data = requests.get(base_url.format("boards") + "/" + board_id + "/lists", params=auth_params).json()
	for column in column_data:
		if column["name"] == column_name:
			requests.post(base_url.format("cards"), data={'name': name, "idList": column["id"], **auth_params})
			break


def move(name, column_name):
	column_data = requests.get(base_url.format("boards") + "/" + board_id + "/lists", params=auth_params).json()

	task_ids = collections.defaultdict(str)
	task_to_move_id = ""

	for column in column_data:
		column_tasks = requests.get(base_url.format("lists") + "/" + column["id"] + "/cards", params=auth_params).json()
		for task in column_tasks:
			if task["name"] == name:
				task_ids[column["name"]] = task["id"]

	if len(task_ids)>1:
		col_to_move_from = input(f"Задачи с таким имененм находятся в колонках {[task for task in task_ids]}.\nИз какой колонки будем переносить?")
		task_to_move_id = task_ids[col_to_move_from]
		print(task_to_move_id)
	else:
		task_to_move_id = [task_id for task_id in task_ids.values()][0]

	for column in column_data:
		if column["name"] == column_name:
			requests.put(base_url.format("cards") + "/" + task_to_move_id + "/idList", data={"value": column["id"], **auth_params})
			break

def create_column(name):
	column_data = requests.get(base_url.format("boards") + "/" + board_id + "/lists", params=auth_params).json()
	column_names = [column['name'] for column in column_data]
	if name in column_names:
		print(f"Колонка с именем {name} уже есть на доске\n")
		user_answer = input("Желаете добавить колонку с тем же именем? y/n ")
		if user_answer.lower() == "y":
			requests.post(base_url.format("boards") + "/" + board_id + "/lists", data={"name": name, **auth_params})
		elif user_answer.lower() == "n":
			input_name = input("Выберите другое имя: ")
			create_column(input_name)
		else:
			user_answer = input("Введите y или n: ")
	else:
		requests.post(base_url.format("boards") + "/" + board_id + "/lists", data={"name": name, **auth_params})
		print(f"Колонка {name} добавлена!")

if __name__=="__main__":
	if len(sys.argv) <=2:
		read()
	elif sys.argv[1] == "create":
		create(sys.argv[2], sys.argv[3])
	elif sys.argv[1] == "move":
		move(sys.argv[2], sys.argv[3])
	elif sys.argv[1] == "create_column":
		create_column(sys.argv[2])