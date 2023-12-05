import streamlit as st
import requests
from datetime import datetime, timedelta
import os
import time
import pandas as pd

static_variable = 0

# Base URL for backend API
BACKEND_API = 'http://127.0.0.1:5000'

def login_user(username, password):
    response = requests.post(f'{BACKEND_API}/login', json={"username": username, "password": password})
    print("Response: ",response)
    if response.status_code == 200:
        return response.json()
    return None

def show_employee_dashboard(static_variable):
    """
    st.write("Employee Dashboard")
    if st.button('Clock In'):
        # Logic for clocking in
        st.write("Clocked In Successfully")
    """
    # Function to format time duration
    def format_duration(duration):
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return "{:02}:{:02}".format(hours, minutes)
    
    with open('C:/Users/Vidyuth/Downloads/adt_project-main/adt_project-main/frontend/wave.css') as f:
        css = f.read()

    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

    #st.markdown(custom_style, unsafe_allow_html=True)
 
    # Main content
    st.title(':orange[Your Time Card] :clock3:')

    # Create a box with buttons and time information
    st.markdown("<div class='box'>", unsafe_allow_html=True)

    # Store clock in time in session state
    if "clock_in_time" not in st.session_state:
        st.session_state.clock_in_time = None

    button_style = """
        <style>
        .stButton > button {
        position: relative;
            color: orange;
            background: gray;
            width: 100px;
            height: 50px;
        }
        </style>
        """
    
    #st.markdown("<h1 style='text-align: center;'>st.button</h1> ", unsafe_allow_html = True)

    st.markdown("<div class='button-container'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        button1 = st.button('Clock in')

    with col2:
        button2 = st.button('Clock out')

    with st.markdown(button_style, unsafe_allow_html=True):

             # Clock In button logic
            if button1:
                st.session_state.clock_in_time = datetime.now()
                st.success(f"Clock In Time: {st.session_state.clock_in_time.strftime('%Y-%m-%d %H:%M:%S')}")

                clockintime = datetime.now()
                print("Clock in time: ###############",clockintime)
                print(static_variable)
                clockintime = clockintime.strftime('%Y-%m-%d %H:%M:%S')
                with open("C:/Users/Vidyuth/OneDrive/Desktop/adtproject/frontend/time.txt", "w") as f:
                    f.write(clockintime)
                # Request to update clock in time
                response = requests.post(f'{BACKEND_API}/clockin', json={"employee": static_variable, "clockintime": clockintime})
                print("Response: ",response)
                if response.status_code == 200:
                    print(response.json())
                else:
                    print("Couldn't clock in")
            

    with st.markdown(button_style, unsafe_allow_html=True):
            # Clock Out button logic
            if button2:
                if st.session_state.clock_in_time is None:
                    st.warning("Please Clock In first.")
                else:
                    clock_out_time = datetime.now()
                    st.success(f"Clock Out Time: {clock_out_time.strftime('%Y-%m-%d %H:%M:%S')}")

                    # Calculate time spent
                    time_spent = clock_out_time - st.session_state.clock_in_time
                    formatted_time_spent = format_duration(time_spent)

                    with open("C:/Users/Vidyuth/OneDrive/Desktop/adtproject/frontend/time.txt", "r") as f:
                        clock_intime = f.read()
                    clock_intime = str(clock_intime)
                    clockouttime = time.strftime("%H:%M:%S", time.localtime())
                    response = requests.post(f'{BACKEND_API}/clockout', json={"employee": static_variable, "clockouttime": clockouttime, "totalhours": formatted_time_spent, 'clockedinat': clock_intime})
                    print("Response: ",response)
                    if response.status_code == 200:
                        print(response.json())
                    else:
                        print("Couldn't clock out")

                    # Display the time spent
                    st.success(f"Time Spent: {formatted_time_spent}")

                    # Reset clock in time
                    st.session_state.clock_in_time = None


def show_manager_dashboard(employee_id):
    """
    st.write("Manager Dashboard")
    if st.button('Add Employee'):
        st.session_state['current_page'] = 'add_employee'
    """
    print("At manager's page now", employee_id)
    st.title("Hello Manager")

    # Create a container to center the buttons
    container = st.container()

    # Create two buttons inside the container
    button1 = container.button("Employee Dashboard", key="button1", help="Click this button")
    button2 = container.button("Add New Employee ", key="button2", help="Click this button")
    button3 = container.button("Delete An Employee", key="button3")    
    button4 = container.button("Update employee details", key="button4")    

    if button1:
        #st.session_state['current_page'] == 'Employee Dashboards'
        return 1
    elif button2:
        print("here")
        #st.session_state['current_page'] == 'Create'
        return 2

    elif button3:
        #st.session_state['current_page'] == 'Delete'
        return 3
    elif button4:
        return 10
    
    # if st.session_state['current_page'] == 'Employee Dashboards':
    #     dashboard_page()
    
    # elif st.session_state['current_page'] == 'Create':
    #     print("here as well")
    #     createpage()
    
    # elif st.session_state['current_page'] == 'Delete':
    #     deletepage()

def add_employee_page():
    st.write("Add Employee")
    with st.form("add_employee_form"):
        emp_name = st.text_input("Employee Name", key='emp_name')
        dept_name = st.text_input("Department Name", key='dept_name')
        location_name = st.text_input("Location Name", key='location_name')
        username = st.text_input("Username", key='username')
        password = st.text_input("Password", type="password", key='password')
        is_manager = st.checkbox("Is Manager?", key='is_manager')
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            response = requests.post(f'{BACKEND_API}/add_employee', json={
                "emp_name": emp_name,
                "dept_name": dept_name,
                "location_name": location_name,
                "username": username,
                "password": password,
                "is_manager": is_manager
            })

            if response.status_code == 201:
                st.success("Employee added successfully.")
                st.session_state['current_page'] = 'manager_dashboard'
            else:
                st.error("Failed to add employee. Please try again.")


def emp_update():
    print("At update abhi")
    st.write("Update Employee")
    with st.form("add_employee_form"):
        emp_id = st.text_input("Employee ID", key='emp_id')
        new_password = st.text_input("New password", key='new_password')
        
        submit_button = st.form_submit_button("Submit")
        if submit_button:
            response = requests.post(f'{BACKEND_API}/update', json={
                "emp_name": emp_id,
                "new_password": new_password})      
            if response.status_code == 201:
                st.success("Employee updates successfully.")
                st.session_state['current_page'] = 'manager_dashboard'
            else:
                st.error("Failed to add employee. Please try again.")



def dashboard_page():
    print("At dashboard page abhi")
    response = requests.post(f'{BACKEND_API}/dashboarddata')
    res = response.json()
    print("Response: ",res['Data'])
    data = pd.DataFrame(res['Data'])

    st.bar_chart(data['Emp_ID'].value_counts())



def createpage():
    print("At create page abhi")
    st.title("Enter New Employee Details")

    # Create a form with 5 input fields
    input1 = st.text_input("Employee ID", key="input1")
    input2 = st.text_input("Employee Name", key="input2")
    input3 = st.text_input("Scheduled Hours", key="input3")
    input4 = st.text_input("Department", key="input4")
    input5 = st.text_input("Location", key="input5")

    print(input1, input2, input3, input4, input5)

    st.button("Submit")
    response = requests.post(f'{BACKEND_API}/createdata', json={"employeeid": input1, "empname": input2, "schdhrs": input3, "dept": input4, "location": input5})
    if response.status_code == 200:
        return response.json()
    if st.button("Back"):
        return 4


def deletepage():
    print("At delete page abhi")
    st.title("Delete Employee")
    with st.form("delete_employee_form"):
        emp_name = st.text_input("Employee Name", key='emp_name')
        emp_id = st.text_input("Employee ID", key='emp_id')
        submit_button = st.form_submit_button("Delete")

        if submit_button:
            if emp_name and emp_id:
                response = requests.post(f'{BACKEND_API}/delete_employee', json={
                    "emp_name": emp_name,
                    "emp_id": emp_id
                })

                if response.status_code == 200:
                    st.success("Employee deleted successfully.")
                    st.session_state['current_page'] = 'manager_dashboard'
                else:
                    st.error("Failed to delete employee. Please try again.")
            else:
                st.error("Please enter both Employee Name and ID.")



# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'login'

# Title
st.title('Employee Timesheet Management System')

# Page logic
if st.session_state['current_page'] == 'login':
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    print(username, password)


    if st.button('Login'):
        user_info = login_user(username, password)
        print("Here I am",user_info)
        if user_info['message'] == True:
            st.success('Logged in successfully.')
            print("Here, because the employee is a manager")
            st.session_state['current_page'] = 'manager_dashboard'
            print("returned value: ", user_info['employee id'])
            with open("C:/Users/Vidyuth/OneDrive/Desktop/adtproject/frontend/empids.txt", "w") as f:
                f.write(str(user_info['employee id']))
        elif user_info['message'] == False:
            print("Here because you are just another employee")
            st.session_state['current_page'] = 'employee_dashboard'
            print("returned value: ", user_info['employee id'])
            with open("C:/Users/Vidyuth/OneDrive/Desktop/adtproject/frontend/empids.txt", "w") as f:
                f.write(str(user_info['employee id']))
        else:
            st.error('Login Falied!')

   
elif st.session_state['current_page'] == 'employee_dashboard':
    with open("C:/Users/Vidyuth/OneDrive/Desktop/adtproject/frontend/empids.txt", "r") as f:
        static_variable = f.read()
    static_variable = int(static_variable)
    print("Before sending: ", static_variable)
    show_employee_dashboard(static_variable)

elif st.session_state['current_page'] == 'manager_dashboard':
    with open("C:/Users/Vidyuth/OneDrive/Desktop/adtproject/frontend/empids.txt", "r") as f:
        static_variable = f.read()
    static_variable = int(static_variable)
    page_no = show_manager_dashboard(static_variable)
    if page_no == 2:
        st.session_state['current_page'] = 'Create'
        #createpage()
    if page_no == 1:
        st.session_state['current_page'] = 'Employees'
    if page_no == 3:
        st.session_state['current_page'] = 'Delete'
    if page_no == 4: 
        st.session_state['current_page'] = 'manager_dashboard'
    if page_no == 10:
        st.session_state['current_page'] = 'update'


if st.session_state['current_page'] == 'manager_dashboard':
    show_manager_dashboard

if st.session_state['current_page'] == 'Create':
    createpage()

if st.session_state['current_page'] == 'Delete':
    deletepage()
if st.session_state['current_page'] == 'Employees':
    dashboard_page()
if st.session_state['current_page'] == 'update':
    emp_update()





