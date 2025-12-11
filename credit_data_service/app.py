from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import random
import uvicorn

app = FastAPI()


class GenerateRequest(BaseModel):
    user_id: str
    has_credit_history: bool


class GenerateResponse(BaseModel):
    user_id: str
    has_credit_history: bool
    features: Dict[str, float]


#  ГЕНЕРАТОР

class CreditDataGenerator:
    RANGES = {
        'INCOME': (0, 662094),
        'SAVINGS': (0, 2911863),
        'T_EXPENDITURE_12': (1177, 472924),
        'T_TAX_12': (0, 17013),
        'DEBT': (0, 5968620),
    }

    @staticmethod
    def generate(has_history: bool) -> Dict[str, float]:
        """
        Генерирует данные
        """
        data = {}

        # 1. Генерируем ОСНОВНЫЕ 5 параметров
        for key, (min_val, max_val) in CreditDataGenerator.RANGES.items():
            if key == 'DEBT' and not has_history:
                data[key] = 0  # Нет истории → долг = 0
            else:
                data[key] = random.randint(min_val, max_val)

        # 2. Категориальные
        data['CAT_DEPENDENTS'] = 1 if random.random() < 0.5 else 0

        # 3. ВЫЧИСЛЯЕМ отношения
        safe_div = lambda a, b: a / b if b != 0 else 0.0

        data['R_SAVINGS_INCOME'] = round(safe_div(data['SAVINGS'], data['INCOME']), 2)
        data['R_EXPENDITURE_INCOME'] = round(safe_div(data['T_EXPENDITURE_12'], data['INCOME']), 2)
        data['R_DEBT_INCOME'] = round(safe_div(data['DEBT'], data['INCOME']), 2)
        data['R_DEBT_SAVINGS'] = round(safe_div(data['DEBT'], data['SAVINGS']), 2)
        data['CAT_DEBT'] = 1 if data['DEBT'] > 0 else 0

        return data


#  API

@app.post("/api/generate")
def generate_data(request: GenerateRequest):

    features = CreditDataGenerator.generate(
        has_history=request.has_credit_history
    )

    return GenerateResponse(
        user_id=request.user_id,
        has_credit_history=request.has_credit_history,
        features=features
    )


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "credit_data_generator"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)