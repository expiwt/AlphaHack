"""
ML скрипт для обработки клиентов.

Этот скрипт:
1. Принимает CSV файл с клиентами
2. Преобразует в датафрейм
3. Загружает обученную модель model.json
4. Обрабатывает данные
5. Выгружает результат в fin_clients.csv

Поля выходного файла:
- id (id клиента)
- target (таргет)
- incomeValue (Значение дохода абонента)
- avg_cur_cr_turn (Средний кредитовый оборот по текущим счетам за 3 месяца)
- ovrd_sum (Сумма просрочки)
- loan_cur_amt (Сумма запрашиваемого кредита)
- hdb_income_ratio (Соотношение HDB дохода)
"""

import pandas as pd
import xgboost as xgb
import sys
from pathlib import Path

def process_clients(input_csv_path: str, output_csv_path: str = None):
    """
    Обрабатывает CSV файл с клиентами через ML модель.
    
    Args:
        input_csv_path: Путь к входному CSV файлу
        output_csv_path: Путь к выходному CSV файлу (по умолчанию fin_clients.csv)
    """
    if output_csv_path is None:
        output_csv_path = Path(__file__).parent / "data" / "fin_clients.csv"
    else:
        output_csv_path = Path(output_csv_path)
    
    # Создаем директорию если её нет
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Обработка файла: {input_csv_path}")
    print(f"Результат будет сохранен в: {output_csv_path}")
    
    # Загружаем CSV в датафрейм
    df_test = pd.read_csv(input_csv_path)
    
    # Убираем первые две колонки если они есть (обычно это индексы)
    if len(df_test.columns) > 2:
        df_test = df_test.iloc[:, 2:]
    
    # Загружаем модель
    model_path = Path(__file__).parent / "model.json"
    if not model_path.exists():
        raise FileNotFoundError(f"Модель не найдена: {model_path}")
    
    loaded_model = xgb.Booster()
    loaded_model.load_model(str(model_path))
    
    # Подготовка признаков для теста (без 'target' и 'w' если они есть)
    X_test = df_test.drop(columns=["target", "w"], errors="ignore")
    
    # Создание DMatrix для теста
    dtest = xgb.DMatrix(X_test)
    
    # Получение предсказаний
    predictions = loaded_model.predict(dtest)
    
    # Вычисляем hdb_income_ratio если есть необходимые поля
    if 'hdb_outstand_sum' in df_test.columns and 'incomeValue' in df_test.columns:
        df_test['hdb_income_ratio'] = df_test['hdb_outstand_sum'] / df_test['incomeValue']
    elif 'hdb_income_ratio' not in df_test.columns:
        # Если поля нет, создаем пустую колонку
        df_test['hdb_income_ratio'] = None
    
    # Создание результирующего DataFrame с нужными полями
    pred_df = pd.DataFrame({
        "id": df_test['id'].astype(str) if 'id' in df_test.columns else range(len(predictions)),
        "target": predictions,
        "incomeValue": df_test['incomeValue'] if 'incomeValue' in df_test.columns else None,
        "avg_cur_cr_turn": df_test['avg_cur_cr_turn'] if 'avg_cur_cr_turn' in df_test.columns else None,
        "ovrd_sum": df_test['ovrd_sum'] if 'ovrd_sum' in df_test.columns else 0.0,
        "loan_cur_amt": df_test['loan_cur_amt'] if 'loan_cur_amt' in df_test.columns else 0.0,
        "hdb_income_ratio": df_test['hdb_income_ratio'] if 'hdb_income_ratio' in df_test.columns else None
    })
    
    # Сохраняем результат
    pred_df.to_csv(output_csv_path, index=False)
    print(f"Файл обработан и сохранен: {output_csv_path}")
    print(f"Обработано записей: {len(pred_df)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python ml_script_clients.py <input_csv_path> [output_csv_path]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        process_clients(input_path, output_path)
    except Exception as e:
        print(f"Ошибка обработки: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
