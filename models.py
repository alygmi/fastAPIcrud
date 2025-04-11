from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Jabatan(Base):
    __tablename__ = "jabatan"

    id_jabatan = Column(Integer, primary_key=True, index=True)
    nama_jabatan = Column(String(100))
    deskripsi = Column(Text)

    users = relationship("User", back_populates="jabatan")


class User(Base):
    __tablename__ = "user"

    id_user = Column(Integer, primary_key=True, index=True)
    nama = Column(String(255))
    alamat = Column(Text)
    telepon = Column(String(20))
    id_jabatan = Column(Integer, ForeignKey("jabatan.id_jabatan"))

    jabatan = relationship("Jabatan", back_populates="users")
