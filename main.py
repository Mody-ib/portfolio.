from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from db import SessionLocal, User, find_by_email, db_insert

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

@app.post("/register")
def register(user_data: RegisterSchema, db: Session = Depends(get_db)):
    if find_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email is already registered")

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=user_data.password
    )
    db_insert(db, new_user)
    return {"message": "Registered successfully", "name": new_user.name}

@app.post("/login")
def login(user_data: LoginSchema, db: Session = Depends(get_db)):
    user = find_by_email(db, user_data.email)
    if not user or user.password != user_data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"message": "Login successful", "name": user.name}
if __name__ =="__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)