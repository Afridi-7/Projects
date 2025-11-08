from fastapi import FastAPI , Path , HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel , Field , computed_field
from typing import Optional , Literal , Annotated , Dict
import json

app = FastAPI()

class Patient(BaseModel):
    id : Annotated[str , Field(...,description="ID of the patient", example="P001")]
    name : Annotated[str , Field(...,description="Name of the patient", example="John Doe")]
    city : Annotated[str , Field(...,description="City of the patient", example="New York")]
    age : Annotated[int , Field(...,description="Age of the patient", example=30, ge=0, le=120)]
    gender : Annotated[Literal["male","female","other"], Field(...,description="Gender of the patient", example="male")]
    height : Annotated[float , Field(...,description="Height of the patient in meters", example=1.75, ge=0.5, le=2.5)]
    weight : Annotated[float , Field(...,description="Weight of the patient in kilograms", example=70.5, ge=2, le=500)]     
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height ** 2), 2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 24.9:
            return "Normal"
        elif 25 <= self.bmi < 29.9:
            return "Overweight"
        else:
            return "Obese"


class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

    
def load_data():
    with open("patients.json","r") as f:
        data = json.load(f)
    return data

def save_data(data):
    with open("patients.json","w") as f:
        json.dump(data,f)


@app.get("/")
def hello():
    return {"message": "Welcome to the Patient Management API"}

@app.get("/about")
def about():
    return {"message": "This API allows you to manage patient records including BMI calculation."}

@app.get("/view")
def view_patients():
    data = load_data()
    return JSONResponse(content=data)

@app.get("/patient/{patient_id}")
def view_patients(patient_id: str = Path(...,description="ID of the patient", example="P001")):
    # Load existing data
    data = load_data()
    if patient_id in data:
        patient_data = data[patient_id]
        patient = Patient(id=patient_id, **patient_data)
        return JSONResponse(content=patient.model_dump())
    else:
        raise HTTPException(status_code=404, detail="Patient not found")


@app.get("/sort")
def sort_patients(sort_by:str = Query(..., description="Sort on the basis of height, weight or bmi"), order: str = Query("asc", description="Sort order", example="asc")):
    valid_fields = ["height", "weight", "bmi"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by field. Must be one of {valid_fields}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order. Must be 'asc' or 'desc'")
    
    data = load_data()
    
    sort_order = True if order == "desc" else False
    
    sorted_data = sorted(data.values(), key=lambda x:x.get(sort_by,0), reverse=sort_order)
    return sorted_data

@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()
    
    # Check if patient ID already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient ID already exists")    
    
    # Add new patient
    data[patient.id] = patient.model_dump(exclude=["id"])
    
    # Save updated data
    save_data(data) 
    return JSONResponse(content={"message": "Patient created successfully", "patient": patient.model_dump()})



@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    #existing_patient_info -> pydantic object -> updated bmi + verdict
    existing_patient_info['id'] = patient_id
    patient_pydandic_obj = Patient(**existing_patient_info)
    #-> pydantic object -> dict
    existing_patient_info = patient_pydandic_obj.model_dump(exclude='id')

    # add this dict to data
    data[patient_id] = existing_patient_info

    # save data
    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):

    # load data
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient deleted'})
