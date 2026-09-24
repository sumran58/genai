from fastapi import FastAPI,Path,HTTPException,Query
import json 
from typing import Annotated,Literal
from pydantic import BaseModel,Field
from fastapi.responses import JSONResponse
app=FastAPI()

class Patient(BaseModel):
    id:Annotated[str,Field(...,description='id of the patient',example='P1001')]
    name:Annotated[str,Field(...,description='name of the patient')]
    gender:Annotated[Literal['male','female','others'],Field(...,description="gender of the person")]
    blood_group:Annotated[str,Field(...,description="blood gorup of the patient")]
    condition:Annotated[str,Field(...,description='condition of the patient')]
    height:Annotated[float,Field(...,gt=0,description='height of the patient')]
    weight:Annotated[float,Field(...,gt=0,description='weight of the patient')]

from typing import Annotated, Literal
from pydantic import BaseModel, Field


class PatientUpdate(BaseModel):

    
    name: Annotated[
        str | None,
        Field(description="name of the patient")
    ] = None

    gender: Annotated[
        Literal["male", "female", "others"] | None,
        Field(description="gender of the person")
    ] = None

    blood_group: Annotated[
        str | None,
        Field(description="blood group of the patient")
    ] = None

    condition: Annotated[
        str | None,
        Field(description="condition of the patient")
    ] = None

    height: Annotated[
        float | None,
        Field(gt=0, description="height of the patient")
    ] = None

    weight: Annotated[
        float | None,
        Field(gt=0, description="weight of the patient")
    ] = None


#load the data 
def load_data():
    with open("patient.json","r")as f:
        data=json.load(f)
    return data

#save the data 
def save_data(data):
    with open('patient.json','w')as f:
        json.dump(data,f)


@app.get('/view')
def view():
    
    data=load_data()
    return data

@app.get('/patient/{patient_id}') #path param which is a dynamic part of the url 
def view_aptient(patient_id:str=Path(...,description="this gives the infomation about the specific patient",example="P1001")):
    #path function increase the readability of the path parameter we can add description,example,validation 
    #load the data 
    data=load_data()

    if patient_id in data:
        return data[patient_id]
    else:
        raise HTTPException (status_code=404,detail='patient not found')

@app.get('/sort')
def sort_patient(
    sort_by: str = Query(..., description='sort on the basis of height and weight'),
    order: str = Query('asc', description='sort in ascending or descending order')
):
    valid_field = ['height', 'weight']

    if sort_by not in valid_field:
        raise HTTPException(
            status_code=400,
            detail=f'invalid field select from {valid_field}'
        )

    if order not in ['asc', 'desc']:
        raise HTTPException(
            status_code=400,
            detail="invalid order select between asc and desc"
        )

    data = load_data()

    sort_order = True if order == 'desc' else False

    sorted_data = sorted(
        data.values(),
        key=lambda x: x.get(sort_by, 0),
        reverse=sort_order
    )

    return sorted_data

@app.post('/create')
def create_patient(patient:Patient):

    #load the existing data 
    data=load_data()
    if patient.id in data:
        raise HTTPException (status_code=400,detail='patient already exist')
    data[patient.id]=patient.model_dump(exclude=['id'])

    save_data(data)
    return JSONResponse(status_code=201,content={'message':'patient created successfully'})

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):

    # Load existing data
    data = load_data()

    # Check patient exists
    if patient_id not in data:
        raise HTTPException(
            status_code=404,
            detail='patient not found'
        )

    # Existing patient information
    existing_patient_info = data[patient_id]

    # Only fields provided by user
    updated_patient_info = patient_update.model_dump(
        exclude_unset=True
    )

    # Update existing information with new information
    existing_patient_info.update(updated_patient_info)

    # Save back to JSON
    data[patient_id] = existing_patient_info

    save_data(data)

    return JSONResponse(
        status_code=200,
        content={'message': 'patient data updated'}
    )

@app.put('/delete/{patient_id}')
def delete_patient(patient_id:str):
    #load the data
    data=load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail='patient not found in the data')

    
    del data[patient_id]
    save_data(data)
    return JSONResponse(status_code=200,content={'message':'patient deleted successfully'})










@app.get('/')
def send():
    return {"message":"patient management system"}

@app.get('/about')
def about():
    return {"message":"This is about learning the fastapi using the patient form data "}