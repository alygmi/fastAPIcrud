from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

# from . import models, schemas
import models
import schemas
from database import get_db, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Endpoint untuk menambah jabatan
@app.post("/jabatan/", response_model=schemas.Jabatan)
def create_jabatan(jabatan: schemas.Jabatanbase, db: Session = Depends(get_db)):
    db_jabatan = models.Jabatan(**jabatan.dict())
    db.add(db_jabatan)
    db.commit()
    db.refresh(db_jabatan)
    return db_jabatan

# Endpoint untuk mendapatkan daftar semua jabatan


@app.get("/jabatan/", response_model=List[schemas.Jabatan])
def read_jabatan(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jabatan = db.query(models.Jabatan).offset(skip).limit(limit).all()
    return jabatan

# endpoint untuk mendapatkan detail jabatan berdasarkan ID


@app.get("/jabatan/{jabatan_id}", response_model=schemas.Jabatan)
def read_jabatan_by_id(jabatan_id: int, db: Session = Depends(get_db)):
    db_jabatan = db.query(models.Jabatan).filter(
        models.Jabatan.id_jabatan == jabatan_id).first()
    if db_jabatan is None:
        raise HTTPException(status_code=404, detail="jabatan tidak ditemukan!")
    return db_jabatan

# endpoint untuk membuat user baru


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_jabatan = db.query(models.Jabatan).filter(
        models.Jabatan.id_jabatan == user.id_jabatan).first()
    if not db_jabatan:
        raise HTTPException(status_code=400, detail="jabatan tidak valid")
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# endpoint untuk mendapatkan semua user


@app.get("/users/", response_model=List[schemas.User])
def read_all_user(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


# endpoint get user by id
@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.id_user == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User Not found")
    return db_user

# endpoint untuk memperbarui data user berdasarkan ID


@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.id_user == user_id).first()  # Cari User berdasarkan ID
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id_jabatan is not None:
        db_jabatan = db.query(models.Jabatan).filter(
            models.Jabatan.id_jabatan == user.id_jabatan).first()
        if not db_jabatan:
            raise HTTPException(status_code=400, detail="Jabatan tidak valid")
        db_user.id_jabatan = user.id_jabatan  # Update id_jabatan pada objek User

    for key, value in user.dict(exclude_unset=True).items():
        if key != "id_jabatan":  # Jangan set ulang id_jabatan di sini karena sudah ditangani di atas
            setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# endpoint untuk menghapus user


@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).options(joinedload(models.User.jabatan)).filter(
        models.User.id_user == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Users not found!")
    db.delete(db_user)
    db.commit()
    return db_user
