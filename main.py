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

# Маршрут для получения списка всех лекарств
@app.get("/drugs/", response_model=List[DrugResponse])
def read_all_drugs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    drugs = db.query(Drug).offset(skip).limit(limit).all()
    return drugs

# Маршрут для обновления информации о лекарстве
@app.put("/drugs/{drug_id}", response_model=DrugResponse)
def update_drug(drug_id: int, updated_drug: DrugCreate, db: Session = Depends(get_db)):
    db_drug = db.query(Drug).filter(Drug.id == drug_id).first()
    if db_drug is None:
        raise HTTPException(status_code=404, detail="Drug not found")
    for attr, value in updated_drug.dict().items():
        setattr(db_drug, attr, value)
    db.commit()
    db.refresh(db_drug)
    return db_drug

# Маршрут для удаления лекарства
@app.delete("/drugs/{drug_id}", response_model=DrugResponse)
def delete_drug(drug_id: int, db: Session = Depends(get_db)):
    db_drug = db.query(Drug).filter(Drug.id == drug_id).first()
    if db_drug is None:
        raise HTTPException(status_code=404, detail="Drug not found")
    db.delete(db_drug)
    db.commit()
    return db_drug

# Маршрут для получения списка всех аптек
@app.get("/pharmacies/", response_model=List[PharmacyResponse])
def read_all_pharmacies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    pharmacies = db.query(Pharmacy).offset(skip).limit(limit).all()
    return pharmacies

# Маршрут для обновления информации об аптеке
@app.put("/pharmacies/{pharmacy_id}", response_model=PharmacyResponse)
def update_pharmacy(pharmacy_id: int, updated_pharmacy: PharmacyCreate, db: Session = Depends(get_db)):
    db_pharmacy = db.query(Pharmacy).filter(Pharmacy.id == pharmacy_id).first()
    if db_pharmacy is None:
        raise HTTPException(status_code=404, detail="Pharmacy not found")
    for attr, value in updated_pharmacy.dict().items():
        setattr(db_pharmacy, attr, value)
    db.commit()
    db.refresh(db_pharmacy)
    return db_pharmacy

# Маршрут для удаления аптеки
@app.delete("/pharmacies/{pharmacy_id}", response_model=PharmacyResponse)
def delete_pharmacy(pharmacy_id: int, db: Session = Depends(get_db)):
    db_pharmacy = db.query(Pharmacy).filter(Pharmacy.id == pharmacy_id).first()
    if db_pharmacy is None:
        raise HTTPException(status_code=404, detail="Pharmacy not found")
    db.delete(db_pharmacy)
    db.commit()
    return db_pharmacy

# Маршрут для создания новой поставки
@app.post("/supplies/", response_model=SupplyResponse)
def create_supply(supply: SupplyCreate, db: Session = Depends(get_db)):
    db_supply = Supply(**supply.dict())
    db.add(db_supply)
    db.commit()
    db.refresh(db_supply)
    return db_supply

# Маршрут для получения информации о конкретной поставке
@app.get("/supplies/{supply_id}", response_model=SupplyResponse)
def read_supply(supply_id: int, db: Session = Depends(get_db)):
    supply = db.query(Supply).filter(Supply.id == supply_id).first()
    if supply is None:
        raise HTTPException(status_code=404, detail="Supply not found")
    return supply

# Маршрут для обновления информации о поставке
@app.put("/supplies/{supply_id}", response_model=SupplyResponse)
def update_supply(supply_id: int, updated_supply: SupplyCreate, db: Session = Depends(get_db)):
    db_supply = db.query(Supply).filter(Supply.id == supply_id).first()
    if db_supply is None:
        raise HTTPException(status_code=404, detail="Supply not found")
    for attr, value in updated_supply.dict().items():
        setattr(db_supply, attr, value)
    db.commit()
    db.refresh(db_supply)
    return db_supply

# Маршрут для удаления поставки
@app.delete("/supplies/{supply_id}", response_model=SupplyResponse)
def delete_supply(supply_id: int, db: Session = Depends(get_db)):
    db_supply = db.query(Supply).filter(Supply.id == supply_id).first()
    if db_supply is None:
        raise HTTPException(status_code=404, detail="Supply not found")
    db.delete(db_supply)
    db.commit()
    return db_supply

# Маршрут для создания нового заказа
@app.post("/orders/", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

# Маршрут для получения информации о конкретном заказе
@app.get("/orders/{order_id}", response_model=OrderResponse)
def read_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# Маршрут для обновления информации о заказе
@app.put("/orders/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, updated_order: OrderCreate, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    for attr, value in updated_order.dict().items():
        setattr(db_order, attr, value)
    db.commit()
    db.refresh(db_order)
    return db_order

# Маршрут для удаления заказа
@app.delete("/orders/{order_id}", response_model=OrderResponse)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(db_order)
    db.commit()
    return db_order
