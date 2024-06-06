from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# Создание объекта FastAPI
app = FastAPI()

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://isp_p_Sakicheva:12345@192.168.25.23/isp_p_Sakicheva"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Определение моделей SQLAlchemy
class Drug(Base):
    __tablename__ = "drugs"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True)
    name = Column(String(50))
    manufacturer = Column(String(50))
    price = Column(Integer)

class Pharmacy(Base):
    __tablename__ = "pharmacies"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True)
    name = Column(String(50))
    address = Column(String(50))
    phoneNumber = Column(String(10))

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(8))
    pharmacyId = Column(Integer, ForeignKey('pharmacies.id'))
    fulfillmentDate = Column(String(8))

    pharmacy = relationship("Pharmacy", back_populates="requests")
    purchases = relationship("Purchase", back_populates="request")

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    requestId = Column(Integer, ForeignKey('requests.id'))
    drugId = Column(Integer, ForeignKey('drugs.id'))
    quantity = Column(Integer)

    request = relationship("Request", back_populates="purchases")
    drug = relationship("Drug", back_populates="purchases")

Pharmacy.requests = relationship("Request", order_by=Request.id, back_populates="pharmacy")
Drug.purchases = relationship("Purchase", order_by=Purchase.id, back_populates="drug")

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

# Определение Pydantic моделей
class DrugBase(BaseModel):
    code: str
    name: str
    manufacturer: str
    price: int

class DrugCreate(DrugBase):
    pass

class DrugResponse(DrugBase):
    id: int
    name: str
    manufacturer: str
    price: int

    class Config:
        orm_mode = True

class PharmacyBase(BaseModel):
    number: int
    name: str
    address: str
    phone_number: str

class PharmacyCreate(PharmacyBase):
    pass

class PharmacyResponse(PharmacyBase):
    id: int

    class Config:
        orm_mode = True


# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Маршруты для операций с лекарствами
@app.post("/drugs/", response_model=DrugResponse)
def create_drug(drug: DrugCreate, db: Session = Depends(get_db)):
    db_drug = Drug(**drug.dict())
    db.add(db_drug)
    db.commit()
    db.refresh(db_drug)
    return db_drug

@app.get("/drugs/{drug_id}", response_model=DrugResponse)
def read_drug(drug_id: int, db: Session = Depends(get_db)):
    drug = db.query(Drug).filter(Drug.id == drug_id).first()
    if drug is None:
        raise HTTPException(status_code=404, detail="Drug not found")
    return drug