from typing import List

import random
import time
from typing import Dict, Optional

from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session, joinedload
from redis import Redis
from redis_config import get_redis

# from . import models, schemas
import models
import schemas
from database import get_db, engine
import json

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Endpoint untuk menambah jabatan
@app.post("/jabatan/", response_model=schemas.Jabatan)
def create_jabatan(jabatan: schemas.JabatanBase, db: Session = Depends(get_db)):
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

def populate_redis_from_postgres(db: Session = Depends(get_db), redis_client: Redis = Depends(get_redis)):
    """Memindahkan semua data User dan Jabatan dari PostgreSQL ke Redis menggunakan skema Pydantic."""
    print("Memulai pemindahan data dari PostgreSQL ke Redis menggunakan skema Pydantic...")

    # Pindahkan data Jabatan
    jabatan_list = db.query(models.Jabatan).all()
    for jabatan in jabatan_list:
        key = f"jabatan:{jabatan.id_jabatan}"
        jabatan_schema = schemas.Jabatan.from_orm(jabatan) # Membuat instance skema dari objek ORM
        redis_client.set(key, jabatan_schema.json())
        print(f"Jabatan ID {jabatan.id_jabatan} dipindahkan ke Redis dengan key: {key}")

    # Pindahkan data User (dengan relasi Jabatan)
    user_list = db.query(models.User).options(joinedload(models.User.jabatan)).all()
    for user in user_list:
        key = f"user:{user.id_user}"
        user_schema = schemas.User.from_orm(user) # Membuat instance skema dari objek ORM
        redis_client.set(key, user_schema.json())
        print(f"User ID {user.id_user} dipindahkan ke Redis dengan key: {key}")

    print("Pemindahan data selesai.")

# endpoint pemindahan data untuk pengujian
@app.post("/admin/populate_redis")
async def trigger_populate_redis(db:Session = Depends(get_db), redis_client:Redis = Depends(get_redis)):    
    populate_redis_from_postgres(db, redis_client)
    return{"message" : "proses pemindahan data"}

# endpoint menarik data jabatan dari redis
@app.get("/redis/jabatan", response_model=list[schemas.Jabatan])
async def read_all_jabatan_from_redis(redis_client: Redis = Depends(get_redis)):
    jabatan_keys = redis_client.keys("jabatan:*")
    jabatan_list = []
    for key in jabatan_keys:
        cached_jabatan = redis_client.get(key)
        if cached_jabatan:
            jabatan_data = json.loads(cached_jabatan)
            jabatan_list.append(schemas.Jabatan(**jabatan_data))
    return jabatan_list


# endpoint mengambil data user dari redis
@app.get("/redis/users", response_model=List[schemas.User])
async def readAllUsersFromRedis(redis_client: Redis = Depends(get_redis)):
    user_keys = redis_client.keys("user:*")
    user_list = []
    for key in user_keys:
        cached_user = redis_client.get(key)
        if cached_user:
            user_data = json.loads(cached_user)
            # reconstruct objek jabatn jika ada di cache
            jabatan_data = user_data.get("jabatan")
            jabatan_obj = schemas.Jabatan(**jabatan_data) if jabatan_data else None
            user_list.append(schemas.User(jabatan=jabatan_obj, **{k: v for k, v in user_data.items() if k != "jabatan"}))
    return user_list

# endpoint untuk menggenerate OTP
@app.post("/otp/generate", response_model=Dict[str, str])
async def get_otp(id: int = Body(..., embed=True), redis_client: Redis = Depends(get_redis)):
    otp = str(random.randint(100000, 999999))
    otp_key = f"otp:{id}"
    redis_client.setex(otp_key, 300, otp)
    attempts_key = f"otp:attempts:{id}"
    redis_client.delete(attempts_key)
    return {"otp" : otp}

# endpoint untuk memverifikasi OTP
@app.post("/otp/verify", response_model=Dict[str, str])
async def verify_otp(id: int = Body(..., embed=True), otp: str = Body(..., embed=True), redis_client: Redis = Depends(get_redis)):
    otp_key = f"otp:{id}"
    stored_otp = redis_client.get(otp_key)
    attempts_key = f"otp:attempts:{id}"
    attempts = redis_client.get(attempts_key)
    max_attempts = 3

    print(f"OTP dari Redis untuk ID {id}: '{stored_otp}'")
    print(f"OTP dari request untuk ID {id}: '{otp}'")

    if stored_otp is None :
        raise HTTPException(status_code=404, detail="Error OTP")
    
    if attempts is not None and int(attempts) >= max_attempts:
        redis_client.delete(otp_key)
        raise HTTPException(status_code=429, detail="Unverified!")
    
    if stored_otp == otp:
        redis_client.delete(otp_key)
        return {"message" : "Verified"}
    else:
        redis_client.incr(attempts_key)
        raise HTTPException(status_code=400, detail="OTP wrong")
    

# endpoint mencari user by ID di redis
@app.get("/redis/users/{user_id}", response_model=Optional[schemas.User])
async def read_user_from_redis(user_id: int, redis_client: Redis = Depends(get_redis)):
    """Mengambil data user dari Redis berdasarkan ID."""
    user_key = f"user:{user_id}"
    cached_user = redis_client.get(user_key)

    if cached_user:
        print(f"Cache hit untuk user ID: {user_id}")
        user_data = json.loads(cached_user)
        # Rekonstruksi objek jabatan jika ada di cache
        jabatan_data = user_data.get("jabatan")
        jabatan_obj = schemas.Jabatan(**jabatan_data) if jabatan_data else None
        return schemas.User(jabatan=jabatan_obj, **{k: v for k, v in user_data.items() if k != "jabatan"})
    else:
        print(f"Cache miss untuk user ID: {user_id}")
        raise HTTPException(status_code=404, detail=f"User dengan ID {user_id} tidak ditemukan di cache.")
