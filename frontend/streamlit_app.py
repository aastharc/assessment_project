import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

st.title("Employee API Dashboard")

st.markdown("---")

# ------------------- Create Employee -------------------
st.subheader("Create New Employee")
with st.form("create_employee_form"):
    employee_id = st.text_input("Employee ID", key="create_id", placeholder="E.g., E1")
    name = st.text_input("Name", key="create_name", placeholder="E.g., Amrita")
    department = st.text_input("Department", key="create_dept", placeholder="E.g., HR, SWE-1")
    salary = st.number_input("Salary", min_value=0, key="create_salary", help="E.g., 75000")
    joining_date = st.date_input("Joining Date", key="create_date", help="YYYY-MM-DD")
    skills = st.text_input("Skills (comma separated)", key="create_skills", placeholder="E.g., Python")
    submitted = st.form_submit_button("Create Employee")
    if submitted:
        data = {
            "employee_id": employee_id,
            "name": name,
            "department": department,
            "salary": salary,
            "joining_date": str(joining_date),
            "skills": [s.strip() for s in skills.split(",") if s.strip()]
        }
        res = requests.post(f"{BASE_URL}/employees", json=data)
        if res.status_code in (200, 201):
            st.success("Employee created successfully!")
            st.json(res.json())
        else:
            st.error(res.json())

st.markdown("---")

# ------------------- Get Employee by ID -------------------
st.subheader("Get Employee by ID")
get_id = st.text_input("Enter Employee ID", key="get_id", placeholder="E.g., E1")
if st.button("Get Employee"):
    if get_id:
        res = requests.get(f"{BASE_URL}/employees/{get_id}")
        if res.status_code == 200:
            st.json(res.json())
        else:
            st.error(res.json())
    else:
        st.warning("Enter Employee ID")

st.markdown("---")

# ------------------- Update Employee -------------------
st.subheader("Update Employee")
with st.form("update_employee_form"):
    update_id = st.text_input("Employee ID to Update", key="update_id", placeholder="E.g., E1")
    name_upd = st.text_input("Name", key="update_name", placeholder="E.g., Amrita")
    department_upd = st.text_input("Department", key="update_dept", placeholder="E.g., HR, SWE-1")
    salary_upd = st.number_input("Salary", min_value=0, key="update_salary", help="E.g., 75000")
    joining_date_upd = st.date_input("Joining Date", key="update_date", help="YYYY-MM-DD")
    skills_upd = st.text_input("Skills (comma separated)", key="update_skills", placeholder="E.g., Python")
    submitted_upd = st.form_submit_button("Update Employee")
    if submitted_upd:
        data = {}
        if name_upd: data["name"] = name_upd
        if department_upd: data["department"] = department_upd
        if salary_upd: data["salary"] = salary_upd
        if joining_date_upd: data["joining_date"] = str(joining_date_upd)
        if skills_upd:
            data["skills"] = [s.strip() for s in skills_upd.split(",") if s.strip()]
        if not update_id:
            st.warning("Employee ID is required")
        else:
            res = requests.put(f"{BASE_URL}/employees/{update_id}", json=data)
            if res.status_code == 200:
                st.success("Employee updated successfully!")
                st.json(res.json())
            else:
                st.error(res.json())

st.markdown("---")

# ------------------- Delete Employee -------------------
st.subheader("Delete Employee")
delete_id = st.text_input("Employee ID to Delete", key="delete_id",placeholder="E.g., E1")
if st.button("Delete Employee"):
    if delete_id:
        res = requests.delete(f"{BASE_URL}/employees/{delete_id}")
        if res.status_code == 200:
            st.success(res.json().get("message", "Deleted successfully"))
        else:
            st.error(res.json())
    else:
        st.warning("Enter Employee ID")

st.markdown("---")

# ------------------- List Employees by Department -------------------
# st.subheader("List Employees by Department")
# if st.button("List Employees by Department"):
#     res = requests.get(f"{BASE_URL}/employees")
#     if res.status_code == 200:
#         st.json(res.json())
#     else:
#         st.error(res.json())

# st.markdown("---")
st.subheader("List Employees by Department")

# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = 1

# Navigation buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("Previous") and st.session_state.page > 1:
        st.session_state.page -= 1
with col2:
    if st.button("Next"):
        st.session_state.page += 1

# Fetch paginated employees from backend
res = requests.get(f"{BASE_URL}/employees", params={"page": st.session_state.page})

if res.status_code == 200:
    data = res.json()["employees"]
    st.write(f"Page: {res.json()['page']}, Page size: {res.json()['page_size']}")
    for dept, employees in data.items():
        st.markdown(f"#### Department: {dept}") 
        for emp in employees:
            st.write(emp)
else:
    st.error("Failed to fetch employees")

st.markdown("---")


# ------------------- Average Salary by Department -------------------
st.subheader("Average Salary by Department")
if st.button("Average Salary by Department"):
    res = requests.get(f"{BASE_URL}/employees/avg-salary")
    if res.status_code == 200:
        st.json(res.json())
    else:
        st.error(res.json())

st.markdown("---")

# ------------------- Search Employees by Skill -------------------
st.subheader("Search Employees by Skill")
skill = st.text_input("Enter Skill (e.g., Python)", key="search_skill", placeholder="Comma-separated, e.g., Python, MongoDB, APIs")
if st.button("Search Employees"):
    if skill:
        res = requests.get(f"{BASE_URL}/employees/search", params={"skill": skill})
        if res.status_code == 200:
            st.json(res.json())
        else:
            st.error(res.json())
    else:
        st.warning("Enter a skill to search")
