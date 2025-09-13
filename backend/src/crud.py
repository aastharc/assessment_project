from fastapi import HTTPException
from .database import employees_collection
from .models import Employee, UpdateEmployee
from typing import List, Dict
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from collections import OrderedDict
PAGE_SIZE = 10 
# 1. Create Employee
async def create_employee(employee: Employee):
    exists = await employees_collection.find_one({"employee_id": employee.employee_id})
    if exists:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    # Convert joining_date to datetime
    data = employee.dict()
    data["joining_date"] = datetime(
        year=data["joining_date"].year,
        month=data["joining_date"].month,
        day=data["joining_date"].day
    )

    await employees_collection.insert_one(data)
    return {"message": "Employee created successfully"}

# 2. Get Employee by ID
async def get_employee(employee_id: str):
    employee = await employees_collection.find_one({"employee_id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    employee["_id"] = str(employee["_id"])
    # Convert joining_date to string for JSON
    if isinstance(employee["joining_date"], datetime):
        employee["joining_date"] = employee["joining_date"].date().isoformat()
    return employee

# 3. Update Employee
async def update_employee(employee_id: str, updates: UpdateEmployee):
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    if "joining_date" in update_data:
        jd = update_data["joining_date"]
        update_data["joining_date"] = datetime(jd.year, jd.month, jd.day)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await employees_collection.update_one(
        {"employee_id": employee_id}, {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee updated successfully"}

# 4. Delete Employee
async def delete_employee(employee_id: str):
    result = await employees_collection.delete_one({"employee_id": employee_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}

# 5. List Employees by Department
# async def list_employees_by_department(department: str):
#     cursor = employees_collection.find({"department": department}).sort("joining_date", -1)
#     employees: List[dict] = []
#     async for emp in cursor:
#         emp["_id"] = str(emp["_id"])
#         if isinstance(emp["joining_date"], datetime):
#             emp["joining_date"] = emp["joining_date"].date().isoformat()
#         employees.append(emp)
#     return employees
# async def list_all_employees_grouped_by_department():
#     # Get all distinct departments
#     departments = await employees_collection.distinct("department")
#     result = {}
#     for dept in departments:
#         cursor = employees_collection.find({"department": dept}).sort("joining_date", -1)
#         employees_list = []
#         async for emp in cursor:
#             emp["_id"] = str(emp["_id"])
#             # convert joining_date to string
#             if isinstance(emp["joining_date"], datetime):
#                 emp["joining_date"] = emp["joining_date"].date().isoformat()
#             employees_list.append(emp)
#         result[dept] = employees_list
#     return result

async def list_employees_by_department_paginated(db: AsyncIOMotorDatabase, page: int = 1) -> Dict[str, List[dict]]:
    """
    Returns employees grouped by department (alphabetically), paginated department-wise.
    page: 1-based page number
    page_size: number of employees per page per department
    """
    result = OrderedDict()
    # Get all distinct departments sorted alphabetically
    departments = await db.employees.distinct("department")
    departments.sort()
    
    for dept in departments:
        skip = (page - 1) * PAGE_SIZE
        cursor = db.employees.find({"department": dept}).sort("joining_date", 1).skip(skip).limit(PAGE_SIZE)
        employees = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            employees.append(doc)
        if employees:
            result[dept] = employees
    return result

# 6. Average Salary by Department
# async def avg_salary_by_department():
#     pipeline = [
#         {"$group": {"_id": "$department", "avg_salary": {"$avg": "$salary"}}},
#         {"$project": {"department": "$_id", "avg_salary": 1, "_id": 0}}
#     ]
#     cursor = employees_collection.aggregate(pipeline)
#     results = []
#     async for doc in cursor:
#         results.append(doc)
#     return results
async def avg_salary_by_department():
    pipeline = [
        {"$group": {"_id": "$department", "avg_salary": {"$avg": "$salary"}}},
        {"$project": {"department": "$_id", "avg_salary": 1, "_id": 0}}
    ]
    cursor = employees_collection.aggregate(pipeline)
    results = []
    async for doc in cursor:
        print(doc)   # <--- debug log
        results.append(doc)
    return results

# 7. Search Employees by Skill
async def search_employees_by_skill(skill: str):
    cursor = employees_collection.find({"skills": skill})
    employees: List[dict] = []
    async for emp in cursor:
        emp["_id"] = str(emp["_id"])
        if isinstance(emp["joining_date"], datetime):
            emp["joining_date"] = emp["joining_date"].date().isoformat()
        employees.append(emp)
    return employees
