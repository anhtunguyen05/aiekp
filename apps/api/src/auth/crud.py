from sqlalchemy.orm import Session
from . import models
from .utils import get_password_hash
import uuid


def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_tenant(db: Session, tenant_id: str):
    return db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()


def create_tenant(db: Session, name: str, description: str = None):
    tenant_id = str(uuid.uuid4())
    db_tenant = models.Tenant(id=tenant_id, name=name, description=description)
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant


def create_user(
    db: Session, email: str, password: str, tenant_id: str, role: str = "user"
):
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(password)
    db_user = models.User(
        id=user_id,
        email=email,
        hashed_password=hashed_password,
        tenant_id=tenant_id,
        role=role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
