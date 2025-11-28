from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Auth Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Client Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ClientInfo(BaseModel):
    client_id: str
    age: int
    gender: str
    city: str
    region: str
    income_real: Optional[float] = None
    income_predicted: Optional[float] = None
    confidence: Optional[float] = None
    income_category: Optional[str] = None

class ClientList(BaseModel):
    total: int
    items: List[ClientInfo]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Prediction Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class PredictionRequest(BaseModel):
    client_id: str = Field(..., description="ID клиента")

class RecommendationItem(BaseModel):
    product: str
    amount: Optional[float] = None
    rate: Optional[float] = None
    reason: str

class ExplanationItem(BaseModel):
    feature: str
    impact: float
    importance: float

class PredictionResponse(BaseModel):
    prediction_id: str
    client_id: str
    predicted_income: float
    actual_income: Optional[float] = None
    confidence: float
    income_category: str
    error: Optional[float] = None
    error_percent: Optional[float] = None
    recommendations: List[RecommendationItem]
    explanation: List[ExplanationItem]
    timestamp: str
    model_version: str

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Dashboard Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class MetricValue(BaseModel):
    metric_name: str
    train_value: float
    test_value: float
    unit: str = ""

class DashboardStats(BaseModel):
    total_predictions: int
    total_clients: int
    avg_confidence: float
    model_version: str
    last_update: str
    metrics: List[MetricValue]

class IncomeDistribution(BaseModel):
    category: str
    count: int
    percentage: float

class DashboardData(BaseModel):
    stats: DashboardStats
    income_distribution: List[IncomeDistribution]
    recent_predictions: List[PredictionResponse]
    top_features: List[ExplanationItem]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Error Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ErrorResponse(BaseModel):
    error: str
    detail: str
    status_code: int
