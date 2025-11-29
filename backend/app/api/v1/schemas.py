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
    id: str
    target: Optional[float] = None
    incomeValue: Optional[float] = None
    avg_cur_cr_turn: Optional[float] = None
    ovrd_sum: Optional[float] = None
    loan_cur_amt: Optional[float] = None
    hdb_income_ratio: Optional[float] = None
    risk_level: Optional[str] = None
    recommendation: Optional[str] = None
    reasoning: Optional[str] = None

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
    last_updated: str
    metrics: List[MetricValue]

class IncomeDistribution(BaseModel):
    category: str
    count: int
    percentage: float

class CreditDecisions(BaseModel):
    approved: int
    rejected: int
    approval_rate: float

class DashboardData(BaseModel):
    stats: DashboardStats
    income_distribution: List[IncomeDistribution]
    credit_decisions: CreditDecisions
    recent_predictions: List[PredictionResponse]
    top_features: List[ExplanationItem]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Error Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ErrorResponse(BaseModel):
    error: str
    detail: str
    status_code: int
