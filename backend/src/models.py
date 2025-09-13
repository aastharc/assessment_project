from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class Employee(BaseModel):
    employee_id: str = Field(..., example="E1")
    name: str = Field(..., example="Aastha")
    department: str = Field(..., example="SWE-1")
    salary: float = Field(..., example=75000)
    joining_date: date = Field(..., example="2023-01-15")
    skills: List[str] = Field(default_factory=list, example=["Python", "MongoDB", "APIs"])

class UpdateEmployee(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[float] = None
    joining_date: Optional[date] = None
    skills: Optional[List[str]] = None
