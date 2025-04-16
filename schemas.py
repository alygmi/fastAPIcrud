from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class JabatanBase(BaseModel):
    nama_jabatan: str
    deskripsi: Optional[str] = None

class Jabatan(JabatanBase):
    id_jabatan: int
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    nama: str
    alamat: Optional[str] = None
    telepon: Optional[str] = None
    id_jabatan: int

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class User(UserBase):
    id_user: int
    jabatan: Optional[Jabatan] = None
    model_config = ConfigDict(from_attributes=True)