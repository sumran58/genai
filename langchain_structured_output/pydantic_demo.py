from pydantic import BaseModel ,EmailStr ,Field
from typing import Optional
class Student(BaseModel):
    name:str='Sim'
    age:Optional[int]=None
    email:EmailStr
    cgpa:float=Field(ge=0,le=10)
new_student={'age':'32','email':'simhar67@gmail.com','cgpa':10}
#even though i gave the age in string but pydantic is smart enough to understand that it need to be converted so it did type coercsion 
student=Student(**new_student)
print(student)