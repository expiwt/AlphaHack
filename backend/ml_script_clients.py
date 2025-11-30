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
- target (таргет - предсказанный доход)
- incomeValue (Значение дохода абонента)
- avg_cur_cr_turn (Средний кредитовый оборот по текущим счетам за 3 месяца)
- ovrd_sum (Сумма просрочки)
- loan_cur_amt (Сумма запрашиваемого кредита)
- hdb_income_ratio (Соотношение HDB дохода)
- PDN (Показатель долговой нагрузки)
"""

import pandas as pd
import xgboost as xgb
import sys
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_clients(input_csv_path: str, output_csv_path: str = None):
    """
    Обрабатывает CSV файл с клиентами через ML модель.
    
    Args:
        input_csv_path: Путь к входному CSV файлу
        output_csv_path: Путь к выходному CSV файлу (по умолчанию fin_clients.csv)
    
    Returns:
        Количество обработанных записей
    """
    if output_csv_path is None:
        output_csv_path = Path(__file__).parent / "data" / "fin_clients.csv"
    else:
        output_csv_path = Path(output_csv_path)
    
    # Создаем директорию если её нет
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Обработка файла: {input_csv_path}")
    logger.info(f"Результат будет сохранен в: {output_csv_path}")
    
    try:
        # Загружаем CSV в датафрейм
        df_test = pd.read_csv(input_csv_path)
        logger.info(f"Загружено {len(df_test)} записей из CSV")
        
        # Проверяем обязательные поля
        required_columns = ['id', 'incomeValue']
        missing_columns = [col for col in required_columns if col not in df_test.columns]
        if missing_columns:
            raise ValueError(f"Отсутствуют обязательные колонки: {missing_columns}")
        
        # Убираем первые две колонки если они есть (обычно это индексы)
        if len(df_test.columns) > 2 and df_test.columns[0] == 'Unnamed: 0':
            df_test = df_test.iloc[:, 2:]
            logger.info("Удалены индексные колонки")
        
        # Загружаем модель
        model_path = Path(__file__).parent / "model.json"
        if not model_path.exists():
            raise FileNotFoundError(f"Модель не найдена: {model_path}")
        
        logger.info("Загрузка ML модели...")
        loaded_model = xgb.Booster()
        loaded_model.load_model(str(model_path))
        
        # Подготовка признаков для теста (без 'target' и 'w' если они есть)
        features_to_drop = ["target", "w"]
        X_test = df_test.drop(columns=[col for col in features_to_drop if col in df_test.columns])
        
        # Логируем используемые признаки
        logger.info(f"Используется {len(X_test.columns)} признаков для предсказания")
        
        # Создание DMatrix для теста
        dtest = xgb.DMatrix(X_test)
        
        # Получение предсказаний
        logger.info("Выполнение предсказаний...")
        predictions = loaded_model.predict(dtest)
        logger.info(f"Получено {len(predictions)} предсказаний")
        
        # Вычисляем hdb_income_ratio если есть необходимые поля
        if 'hdb_outstand_sum' in df_test.columns and 'incomeValue' in df_test.columns:
            df_test['hdb_income_ratio'] = df_test['hdb_outstand_sum'] / df_test['incomeValue']
            logger.info("Вычислен hdb_income_ratio")
        elif 'hdb_income_ratio' not in df_test.columns:
            # Если поля нет, создаем пустую колонку
            df_test['hdb_income_ratio'] = None
            logger.info("hdb_income_ratio не найден, создана пустая колонка")
        
        # Вычисляем PDN (Показатель долговой нагрузки)
        if 'hdb_outstand_sum' in df_test.columns and 'incomeValue' in df_test.columns:
            df_test['PDN'] = (df_test['hdb_outstand_sum'] / df_test['incomeValue']) * 100
            logger.info("Вычислен PDN")
        else:
            df_test['PDN'] = None
            logger.info("Не удалось вычислить PDN, создана пустая колонка")
        
        # Создание результирующего DataFrame с нужными полями
        pred_df = pd.DataFrame({
            "id": df_test['id'].astype(str),  # ID как строка для совместимости с БД
            "target": predictions,  # Предсказанный доход
            "incomeValue": df_test['incomeValue'],
            "avg_cur_cr_turn": df_test.get('avg_cur_cr_turn', None),
            "ovrd_sum": df_test.get('ovrd_sum', 0.0),
            "loan_cur_amt": df_test.get('loan_cur_amt', 0.0),
            "hdb_income_ratio": df_test.get('hdb_income_ratio', None),
            "PDN": df_test.get('PDN', None)
        })
        
        # Заполняем NaN значения
        pred_df['ovrd_sum'] = pred_df['ovrd_sum'].fillna(0.0)
        pred_df['loan_cur_amt'] = pred_df['loan_cur_amt'].fillna(0.0)
        
        # Сохраняем результат
        pred_df.to_csv(output_csv_path, index=False)
        logger.info(f"Файл обработан и сохранен: {output_csv_path}")
        logger.info(f"Обработано записей: {len(pred_df)}")
        
        return len(pred_df)
        
    except Exception as e:
        logger.error(f"Ошибка обработки: {e}")
        raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python ml_script_clients.py <input_csv_path> [output_csv_path]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        count = process_clients(input_path, output_path)
        print(f"Успешно обработано {count} записей")
    except Exception as e:
        print(f"Ошибка обработки: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
