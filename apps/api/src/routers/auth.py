from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel

from src.auth import crud, utils
from src.auth.database import get_auth_db

router = APIRouter(prefix="/auth", tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: str
    password: str
    tenant_name: str
    tenant_description: str | None = None

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    tenant_id: str

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_auth_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    tenant = crud.create_tenant(db=db, name=user.tenant_name, description=user.tenant_description)
    new_user = crud.create_user(db=db, email=user.email, password=user.password, tenant_id=tenant.id, role="admin")
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        role=new_user.role,
        tenant_id=new_user.tenant_id
    )

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_auth_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": user.email, "tenant_id": user.tenant_id, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
