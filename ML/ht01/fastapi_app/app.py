from fastapi import FastAPI, UploadFile, Response
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from typing import List
from io import StringIO
import cloudpickle
import pandas as pd
import csv

from models import Item

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    '''
    Загружает модель при запуске сервиса
    '''
    with open('car_price_ridge_model.cloudpickle', 'rb') as f:
        car_price_model = cloudpickle.load(f)

    ml_models['car_price_model'] = car_price_model
    yield
    ml_models.clear()

app = FastAPI(lifespan=lifespan)

@app.get('/', include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse('/docs')

@app.post('/predict_item')
def predict_item(item: Item) -> float:
    '''
    Получение предсказания для одного объекта
    '''
    X = pd.DataFrame([item.model_dump()])
    return ml_models['car_price_model'].predict(X)

@app.post('/predict_items_json')
def predict_items(items: List[Item]) -> List[float]:
    '''
    Получение предсказаний для списка объектов
    '''
    X = pd.DataFrame([item.model_dump() for item in items])
    preds = ml_models['car_price_model'].predict(X)
    return preds.tolist()

@app.post('/predict_items_csv')
def predict_items_csv(file: UploadFile):
    '''
    Получение предсказаний по объектам из csv
    '''
    content = file.file.read()
    with StringIO(content.decode('utf-8')) as buff:
        reader = csv.DictReader(buff)
        items = [Item.model_validate(row) for row in reader]

    X = pd.DataFrame([item.model_dump() for item in items])
    X['selling_price'] = ml_models['car_price_model'].predict(X)

    headers = {'Content-Disposition': 'attachment; filename="data_w_predictions.csv"'}
    return Response(X.to_csv(index=False), headers=headers, media_type='text/csv')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app:app', host='0.0.0.0', port=8080, reload=True)
