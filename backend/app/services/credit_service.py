"""
Сервис для расчета кредитных решений на основе метрик клиента.
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

def calculate_credit_decision(client_data: Dict) -> Dict:
    """
    Вычисляет решение по кредиту на основе метрик.
    
    Правила:
    - debt_burden_ratio < 0.3 → LOW риск
    - 0.3 ≤ debt_burden_ratio < 0.6 → MEDIUM риск  
    - debt_burden_ratio ≥ 0.6 → HIGH риск
    
    - Если LOW риск → APPROVE
    - Если MEDIUM и income высокий → APPROVE
    - Если HIGH → REJECT
    
    Args:
        client_data: Словарь с данными клиента:
            - debt_burden_ratio: float (0-1) - отношение просрочки к доходу
            - predicted_income: float (incomeValue)
            - total_debt: float (ovrd_sum - сумма просрочки)
            - loan_amount: float (loan_cur_amt - запрашиваемая сумма)
            - avg_cur_cr_turn: float (средний кредитовый оборот)
    
    Returns:
        dict с полями:
            - credit_eligible: bool
            - risk_level: str (LOW/MEDIUM/HIGH)
            - recommendation: str (APPROVE/REJECT/REVIEW)
            - reasoning: str
    """
    debt_burden_ratio = client_data.get('debt_burden_ratio', 0.0)
    predicted_income = client_data.get('predicted_income', 0.0)
    total_debt = client_data.get('total_debt', 0.0)
    loan_amount = client_data.get('loan_amount', 0.0)
    avg_cur_cr_turn = client_data.get('avg_cur_cr_turn', 0.0)
    
    # Определяем уровень риска
    if debt_burden_ratio < 0.3:
        risk_level = "LOW"
    elif debt_burden_ratio < 0.6:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
    
    # Определяем рекомендацию
    if risk_level == "LOW":
        credit_eligible = True
        recommendation = "APPROVE"
        reasoning = "Низкая долговая нагрузка, стабильный доход"
    elif risk_level == "MEDIUM":
        # Для среднего риска проверяем доход
        if predicted_income >= 150000:  # Высокий доход
            credit_eligible = True
            recommendation = "APPROVE"
            reasoning = "Средняя долговая нагрузка, но высокий доход позволяет одобрить"
        else:
            credit_eligible = False
            recommendation = "REVIEW"
            reasoning = "Средняя долговая нагрузка, требуется дополнительный анализ"
    else:  # HIGH
        credit_eligible = False
        recommendation = "REJECT"
        reasoning = "Высокая долговая нагрузка, риск дефолта"
    
    # Дополнительные проверки
    if total_debt > predicted_income * 0.8 and predicted_income > 0:
        # Если просрочка больше 80% дохода - отклоняем
        credit_eligible = False
        recommendation = "REJECT"
        reasoning = "Сумма просрочки превышает 80% дохода"
        risk_level = "HIGH"
    
    if loan_amount > predicted_income * 2 and predicted_income > 0:
        # Если запрашиваемая сумма больше 2x дохода - отклоняем
        credit_eligible = False
        recommendation = "REJECT"
        reasoning = "Запрашиваемая сумма кредита превышает 200% дохода"
        risk_level = "HIGH"
    
    if avg_cur_cr_turn > 0 and avg_cur_cr_turn < predicted_income * 0.3:
        # Если средний оборот очень низкий относительно дохода - средний риск
        if risk_level == "LOW":
            risk_level = "MEDIUM"
            if credit_eligible:
                recommendation = "REVIEW"
                reasoning = "Низкий кредитовый оборот относительно дохода"
    
    return {
        "credit_eligible": credit_eligible,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "reasoning": reasoning
    }

def get_risk_level_color(risk_level: str) -> str:
    """
    Возвращает цвет для уровня риска.
    
    Args:
        risk_level: LOW, MEDIUM, HIGH
    
    Returns:
        CSS класс или цвет
    """
    colors = {
        "LOW": "#22C55E",      # Зеленый
        "MEDIUM": "#F59E0B",   # Желтый
        "HIGH": "#EF4444"      # Красный
    }
    return colors.get(risk_level, "#666666")

