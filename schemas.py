from pydantic import BaseModel


class Jabatanbase(BaseModel):
    nama_jabatan: str
    deskripsi: str


class Jabatan(Jabatanbase):
    id_jabatan: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    nama: str
    alamat: str
    telepon: str
    id_jabatan: int


class UserCreate(UserBase):
    pass


class User(UserBase):
    id_user: int
    jabatan: Jabatan

    class Config:
        orm_mode = True


class UserUpdate(UserBase):
    nama: str | None = None
    alamat: str | None = None
    telepon: str | None = None
    id_jabatan: int | None = None
