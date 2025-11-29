from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# USERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(500), nullable=False)
    full_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User(email={self.email})>"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLIENTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(String(50), primary_key=True)
    target = Column(Float, nullable=True)
    incomeValue = Column("incomeValue", Float, nullable=True)  # Явно указываем имя с кавычками
    avg_cur_cr_turn = Column("avg_cur_cr_turn", Float, nullable=True)
    ovrd_sum = Column("ovrd_sum", Float, nullable=True, default=0.0)
    loan_cur_amt = Column("loan_cur_amt", Float, nullable=True, default=0.0)
    hdb_income_ratio = Column("hdb_income_ratio", Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Client(id={self.id}, incomeValue={self.incomeValue})>"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PREDICTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Prediction(Base):
    __tablename__ = "predictions"
    
    prediction_id = Column(String(50), primary_key=True)
    client_id = Column(String(50), ForeignKey("clients.id"), nullable=False)
    predicted_income = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    category = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Prediction(client_id={self.client_id}, income={self.predicted_income})>"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RECOMMENDATIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    recommendation_id = Column(String(50), primary_key=True)
    client_id = Column(String(50), ForeignKey("clients.id"), nullable=False)
    product_type = Column(String(100), nullable=False)
    recommendation_text = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Recommendation(client_id={self.client_id}, product={self.product_type})>"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODEL METRICS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ModelMetrics(Base):
    __tablename__ = "model_metrics"
    
    metric_id = Column(String(50), primary_key=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    model_version = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ModelMetrics(name={self.metric_name}, value={self.metric_value})>"
