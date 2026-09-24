from fastapi import FastAPI
from pydantic import BaseModel,Field,computed_field,field_validator
import pickle
import pandas as pd
from typing import Literal,Annotated
from fastapi.responses import JSONResponse
from schema.user_input import UserInput
#import ml model 
with open('models/model.pkl','rb')as f:
    model=pickle.load(f)

app=FastAPI()


#human readable
@app.get('/')
def home():
       return {'message':'insuarrance preimum prediction'}
MODEL_VERSION='1.0.0'
#machine readable
@app.get('/health')
def health_check():
       return{'status':'ok','model_version':MODEL_VERSION}

@app.post('/predict')
def predict_premium(data: UserInput):

    input_df = pd.DataFrame([{
        'bmi': data.bmi,
        'age_group': data.age_group,
        'lifestyle_risk': data.lifestyle_risk,
        'city_tier': data.city_tier,
        'income_lpa': data.income_lpa,
        'occupation': data.occupation
    }])

    prediction = model.predict(input_df)[0]

    return JSONResponse(status_code=200, content={'predicted_category': prediction})

          