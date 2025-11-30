# Проверка соответствия типов полей таблицы clients

## 📊 Сравнение models.py и init.sql

### Модель Client (models.py)
```python
class Client(Base):
    __tablename__ = "clients"
    
    id = Column(String(50), primary_key=True)                    # String(50)
    target = Column(Float, nullable=True)                        # Float, nullable
    incomeValue = Column("incomeValue", Float, nullable=True)    # Float, nullable
    avg_cur_cr_turn = Column("avg_cur_cr_turn", Float, nullable=True)  # Float, nullable
    ovrd_sum = Column("ovrd_sum", Float, nullable=True, default=0.0)  # Float, nullable, default=0.0
    loan_cur_amt = Column("loan_cur_amt", Float, nullable=True, default=0.0)  # Float, nullable, default=0.0
    hdb_income_ratio = Column("hdb_income_ratio", Float, nullable=True)  # Float, nullable
    created_at = Column(DateTime, default=datetime.utcnow)      # DateTime, default
```

### SQL схема (init.sql)
```sql
CREATE TABLE IF NOT EXISTS clients (
    id VARCHAR(50) PRIMARY KEY,                    -- ✅ Соответствует String(50)
    target FLOAT,                                  -- ✅ Соответствует Float, nullable
    "incomeValue" FLOAT,                           -- ✅ Соответствует Float, nullable
    avg_cur_cr_turn FLOAT,                         -- ✅ Соответствует Float, nullable
    ovrd_sum FLOAT DEFAULT 0,                      -- ✅ Соответствует Float, default=0.0
    loan_cur_amt FLOAT DEFAULT 0,                 -- ✅ Соответствует Float, default=0.0
    hdb_income_ratio FLOAT,                        -- ✅ Соответствует Float, nullable
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- ✅ Соответствует DateTime, default
);
```

## ✅ Результат проверки

**Все типы соответствуют!**

### Маппинг типов SQLAlchemy → PostgreSQL:
- `String(50)` → `VARCHAR(50)` ✅
- `Float` → `FLOAT` ✅
- `DateTime` → `TIMESTAMP` ✅
- `nullable=True` → колонка без NOT NULL ✅
- `default=0.0` → `DEFAULT 0` ✅
- `default=datetime.utcnow` → `DEFAULT CURRENT_TIMESTAMP` ✅

## ⚠️ Важные замечания

1. **incomeValue с кавычками:**
   - В SQL: `"incomeValue"` (с кавычками для сохранения camelCase)
   - В модели: `Column("incomeValue", ...)` (явно указано имя)
   - Это важно для PostgreSQL, который приводит имена к нижнему регистру

2. **Nullable поля:**
   - Все поля кроме `id` и `created_at` могут быть NULL
   - Это соответствует логике, где некоторые данные могут отсутствовать

3. **Default значения:**
   - `ovrd_sum` и `loan_cur_amt` имеют default=0.0
   - Это соответствует логике, где просрочка и кредит могут быть нулевыми

## 🔧 Если нужно исправить типы

Если обнаружено несоответствие, нужно:

1. Обновить `init.sql` - изменить CREATE TABLE
2. Обновить миграцию в `database.py` - добавить ALTER TABLE
3. Перезапустить приложение для применения миграции


