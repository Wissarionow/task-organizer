import streamlit as st
import requests

#api links
#BASE_API_URL = "http://django_api:8000"
#BASE_API_URL = "http://localhost:8000"
BASE_API_URL = "http://backend:8000"


login_url = f"{BASE_API_URL}/api/token/"
register_url = f"{BASE_API_URL}/api/user/register/"
get_user_tasks_url = f"{BASE_API_URL}/api/user/tasks/"
add_task_url = f"{BASE_API_URL}/api/task/create/"
get_users_url = f"{BASE_API_URL}/api/user/all/"
get_tasks_url = f"{BASE_API_URL}/api/task/all/"
get_task_url = f"{BASE_API_URL}/api/task/"
edit_task_url = f"{BASE_API_URL}/api/task/edit/"
task_history_url = f"{BASE_API_URL}/api/task/history/"
get_task_filter_url = f"{BASE_API_URL}/api/task/filter/"


if 'token' not in st.session_state:
    st.session_state.token = None


##data serialization
class Task:
    def __init__(self, name, description, status, assigned_user):
        self.name = name
        self.description = description
        self.status = status
        self.assigned_user = assigned_user

    def __str__(self):
        return f"{self.name} {self.id}"

def task_serializer(task):
    return Task(task['name'], task['description'], task['status'], task['assigned_user'])



###################
##login functions##
###################

def login(name, password):
    response = requests.post(login_url, json={"username": name, "password": password})
    if response.status_code == 200:
        return response.json()['access']  
    return None


def register(username, email, password):
    response = requests.post(register_url, json={"username": username, "email": email, "password": password})
    if response.status_code == 201:
        return response.json()['access'] 
    return None

def login_screen():
    st.sidebar.title("Login or register")
    name = st.sidebar.text_input("Name")
    password = st.sidebar.text_input("Password", type="password")
    email = st.sidebar.text_input("Email")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.sidebar.button("Login"):
            st.session_state.token = login(name, password)
            if st.session_state.token:
                st.sidebar.success("Logged in successfully")
            else:
                st.sidebar.error("Invalid name or password")
    with col2:
        if st.sidebar.button("Register"):
            token = register(name, email, password)
            if token is None:
                st.sidebar.error("There was an error during registration")
            else:
                st.session_state.token = token
                st.sidebar.success("Registered and logged in successfully")


######################
##get info functions##
######################

def get_user_id(name):
    response = requests.get(get_users_url)
    users = response.json()
    for user in users:
        if user['username'] == name:
            return user['id']
    return None


def get_user_name(usr_id):
    response = requests.get(get_users_url)
    users = response.json()
    for user in users:
        if user['id'] == usr_id:
            return user['username']
    return None


def get_task_history(task_id):
    response = requests.get(task_history_url+str(task_id))
    for entry in response.json():
        entry['created_at'] = entry['created_at'].replace("T", " ").replace("Z", "")
        entry['created_at'] = entry['created_at'].replace("T", " ").replace("Z", "")
        entry['updated_at'] = entry['updated_at'].replace("T", " ").replace("Z", "")
        if entry['deleted_at']:
            entry['deleted_at'] = entry['deleted_at'].replace("T", " ").replace("Z", "")
    if response.status_code == 200:
        return response.json()
    return []


def get_user_tasks(usr_id):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(get_user_tasks_url + str(usr_id), headers=headers)
    tasks = response.json()
    task_list = []
    for task in tasks:
        task_list.append(task_serializer(task))
    return task_list


def get_task(task_id):
    response = requests.get(get_task_url + str(task_id))
    task = response.json()
    return task_serializer(task)


def api_filter_tasks(status=None, keyword=None, assigned_user=None):
    params = {}
    if status:
        params['status'] = status.upper()
    if keyword:
        params['keyword'] = keyword
    if assigned_user:
        params['assigned_user'] = assigned_user

    response = requests.get(get_task_filter_url, params=params)
    
    if response.status_code == 200:
        return response.json()
    return []



###############################
##data manipulation functions##
###############################
def api_add_task(name, description, status, assigned_user):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    task_data = {
        "name": name, 
        "description": description, 
        "status": status.replace(" ", "_").upper(), 
        "assigned_user": assigned_user
    }
    print("Posting JSON:", task_data)
    response = requests.post(add_task_url, json=task_data, headers=headers)
    if response.status_code == 201:
        return True
    return False

def api_edit_task(task_id, name, description, status, assigned_user):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    task_data = {
        "id": task_id,
        "name": name, 
        "description": description, 
        "status": status.replace(" ", "_").upper(), 
        "assigned_user": assigned_user
    }
    print("Posting JSON:", task_data)
    response = requests.post(edit_task_url + str(task_id) + "/", json=task_data, headers=headers)
    if response.status_code == 201 or response.status_code == 200:
        return True
    return False

def api_delete_task(task_id):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.delete(edit_task_url + str(task_id) + "/", headers=headers)
    if response.status_code == 204:
        return True
    return False


############
#dropdowns##
############
def api_get_all_users():
    try:
        response = requests.get(get_users_url, timeout=5)  # Add timeout
        if response.status_code != 200:
            print(f"Error: API returned status code {response.status_code}")
            return {}  
        users_list = response.json()
        return {user["id"]: user["username"] for user in users_list}  # Convert to dictionary
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {}

def api_get_all_tasks():
    try:
        response = requests.get(get_tasks_url, timeout=5)  # Add timeout
        if response.status_code != 200:
            print(f"Error: API returned status code {response.status_code}")
            return {}  
        tasks = response.json()
        print("API response:", tasks)
        task_dict = {task['id']: task['name'] for task in tasks}
        return task_dict
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {}


def main(): 
    login_screen()

    add_task, edit_task, check_task, task_history = st.tabs(["Add task", "Edit task", "Check task", "Task history"])
   
    with add_task:
        st.title("Add task")
        name = st.text_input("Task name")
        description = st.text_area("Description")
        status = st.selectbox("Status", ["New", "In progress", "Solved"])
        users = api_get_all_users()
        assigned_user_name = st.selectbox("Assigned user", list(users.values()))
        assigned_user_id = list(users.keys())[list(users.values()).index(assigned_user_name)] if assigned_user_name in users.values() else None
        if st.button("Add task"):
           if api_add_task(name, description, status, assigned_user_id):
               st.success("Task added")
           else:
                st.error("Failed to add task")
            
    with edit_task:
        st.title("Edit task")
        
        tasks = api_get_all_tasks()
        selected_task = st.selectbox("Select task to edit", list(tasks.values()))
        
        task_id = list(tasks.keys())[list(tasks.values()).index(selected_task)]
        task = get_task(task_id)
        
        name1 = st.text_input("Task name", value=task.name)
        description1 = st.text_area("Description", value=task.description)
        status1 = st.selectbox("Status", ["New", "In progress", "Solved"], placeholder='choose status')
        users = api_get_all_users()
        assigned_user_name = st.selectbox("Assigned user", list(users.values()), placeholder='choose user')
        assigned_user_id = list(users.keys())[list(users.values()).index(assigned_user_name)] if assigned_user_name in users.values() else None
        
        col1, col2 = st.columns(2, gap='small')
        with col1:
            if st.button("Edit task"):
                if api_edit_task(task_id, name1, description1, status1, assigned_user_id):
                    st.success("Task edited")
                else:
                    st.error("Failed to edit task")
        with col2:   
            if st.button("Delete task", icon="🚨"):
                if api_delete_task(task_id):
                    st.success("Task deleted")
                else:
                    st.error("Failed to delete task")
        
    with check_task:
        st.title("Filter tasks")
        users = api_get_all_users()
        status_filter = st.selectbox("Filter by status", ["", "New", "In progress", "Solved"])
        keyword_filter = st.text_input("Search by keyword in description")
        assigned_user_filter = st.selectbox("Filter by assigned user", [""] + list(users.values()))
        
        if st.button("Apply Filters"):
            filtered_tasks = api_filter_tasks(status=status_filter, keyword=keyword_filter, assigned_user=get_user_id(assigned_user_filter))
            print("Status filter:", status_filter)
            print("Keyword filter:", keyword_filter)
            print("Assigned user filter:", assigned_user_filter)
            print("Filtered tasks:", filtered_tasks)  
            if filtered_tasks:
                for task in filtered_tasks:
                    st.write(f"**{task['name']}** - {task['status']}")
                    st.write(f"Description: {task['description']}")
                    st.write(f"Assigned to: {get_user_name(task['assigned_user'])}")
                    st.write("---")
            else:
                st.write("No tasks match the filters.")
        
    with task_history:
        st.title("Task History")

        tasks = api_get_all_tasks()
        selected_task = st.selectbox("Select Task", list(tasks.values()))

        if st.button("Show History"):
            task_id = list(tasks.keys())[list(tasks.values()).index(selected_task)]
            history_data = get_task_history(task_id)

            if history_data:
                for entry in history_data:
                    st.write(f"**Updated At:** {entry['updated_at']}")
                    st.write(f"**Task Name:** {entry['name']}")
                    st.write(f"**Description:** {entry['description']}")
                    st.write(f"**Assigned User:** {entry['assigned_user']}")
                    st.write(f"**Created At:** {entry['created_at']}")
                    st.write(f"**Deleted At:** {entry['deleted_at'] if entry['deleted_at'] else 'Not Deleted'}")
                    st.write("---")
            else:
                st.write("No history available for this task.")

if __name__ == "__main__":
    main()

