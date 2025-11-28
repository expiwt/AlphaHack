from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, Date
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
    
    client_id = Column(String(50), primary_key=True)
    dt = Column(Date, nullable=True)
    age = Column(Integer)
    gender = Column(String(20))
    city = Column(String(255))
    region = Column(String(255))
    income_real = Column(Float, nullable=True)
    income_predicted = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    income_category = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Client(id={self.client_id}, age={self.age})>"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PREDICTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Prediction(Base):
    __tablename__ = "predictions"
    
    prediction_id = Column(String(50), primary_key=True)
    client_id = Column(String(50), ForeignKey("clients.client_id"), nullable=False)
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
    client_id = Column(String(50), ForeignKey("clients.client_id"), nullable=False)
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
