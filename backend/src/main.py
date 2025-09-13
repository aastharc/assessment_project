from fastapi import FastAPI, Query
from typing import Optional
from .models import Employee, UpdateEmployee
from . import crud
from fastapi.responses import HTMLResponse
from src.database import db

app = FastAPI(title="Employee Management API", version="1.0")
@app.on_event("startup")
async def startup_db():
    await db.employees.create_index("employee_id", unique=True)


# CRUD Endpoints
@app.get("/", response_class=HTMLResponse)
async def home():
    html_content = """<html>
<head>
    <title>Employee API</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
        }

        .button {
            display: inline-block;
            padding: 10px 20px;
            margin: 5px;
            font-size: 16px;
            color: white;
            background-color: #4CAF50;
            text-decoration: none;
            border-radius: 5px;
        }

        .button:hover {
            background-color: #45a049;
        }

        #skillContainer {
            margin-top: 10px;
        }

        #output {
            text-align: left;
            display: inline-block;
            margin-top: 20px;
            padding: 10px;
            background: #f5f5f5;
            max-width: 90%;
            overflow-x: auto;
        }

        .button-row {
            margin-bottom: 10px;
        }
    </style>
    <script>
        async function fetchEmployees() {
            const res = await fetch('/employees');
            const data = await res.json();
            document.getElementById('output').textContent = JSON.stringify(data, null, 2);
        }

        async function fetchAvgSalary() {
            const res = await fetch('/employees/avg-salary');
            const data = await res.json();
            document.getElementById('output').textContent = JSON.stringify(data, null, 2);
        }

        async function fetchSearch() {
            const skill = document.getElementById('skillInput').value;
            const res = await fetch('/employees/search?skill=' + encodeURIComponent(skill));
            const data = await res.json();
            document.getElementById('output').textContent = JSON.stringify(data, null, 2);
        }
    </script>
</head>
<body>
    <h1>Welcome to Employee API</h1>
    <p>Click a button to see results:</p>

    <!-- Buttons in one row -->
    <div class="button-row">
        <a class="button" href="javascript:void(0)" onclick="fetchEmployees()">List Employees by Department</a>
        <a class="button" href="javascript:void(0)" onclick="fetchAvgSalary()">Average Salary by Department</a>
        <a class="button" href="javascript:void(0)" onclick="fetchSearch()">Search Employees by Skill</a>
        <a class="button" href="/docs">API Documentation (Swagger)</a>
    </div>

    <!-- Skill input below skill button -->
    <div id="skillContainer">
        <input type="text" id="skillInput" placeholder="Skill (e.g., Python)">
    </div>

    <!-- Output display -->
    <pre id="output"></pre>
</body>
</html>


"""
    return HTMLResponse(content=html_content)

@app.get("/employees/search")
async def search_employees(skill: str = Query(...)):
    return await crud.search_employees_by_skill(skill)

@app.get("/employees/avg-salary")
async def avg_salary():
    return await crud.avg_salary_by_department()


@app.post("/employees")
async def create_employee(employee: Employee):
    return await crud.create_employee(employee)

@app.get("/employees/{employee_id}")
async def get_employee(employee_id: str):
    return await crud.get_employee(employee_id)

@app.put("/employees/{employee_id}")
async def update_employee(employee_id: str, updates: UpdateEmployee):
    return await crud.update_employee(employee_id, updates)

@app.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str):
    return await crud.delete_employee(employee_id)

# Query & Aggregation
# @app.get("/employees")
# async def list_employees_by_department(department: Optional[str] = Query(None)):
#     if department:
#         return await crud.list_employees_by_department(department)
#     return {"message": "Please provide a department parameter"}
# @app.get("/employees")
# async def list_employees_by_department(skip: int = Query(0, ge=0, description="Number of records to skip"),
#     limit: int = Query(10, gt=0, le=100, description="Max records to return")):
#     """
#     List employees grouped by department, sorted by joining_date (newest first)
#     """
#     return await crud.list_all_employees_grouped_by_department(skip=skip, limit=limit)

@app.get("/employees")
async def list_employees(page: int = Query(1, ge=1)):
    """
    List employees grouped by department alphabetically, paginated department-wise.
    """
    employees = await crud.list_employees_by_department_paginated(db, page=page)
    return {"page": page, "page_size": crud.PAGE_SIZE, "employees": employees}

