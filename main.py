from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import psycopg2

app = FastAPI()

# Подключение к базе данных PostgreSQL
conn = psycopg2.connect(
    dbname='backup',
    user='postgres',
    password='postgres',
    host='localhost'
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://optvideo.com"],  # Для разрешения всех источников
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get('/oreon_bestprice', response_model=Dict[str, str])
async def get_oreon_bestprice():
    try:
        # Запрос к базе данных для получения code_oreon и best_price из двух таблиц
        with conn.cursor() as cursor:
            sql = """
                SELECT c.code_oreon, b.best_price
                FROM public.logs_cardsproduct c
                JOIN public.logs_bestprice b ON c.code = b.id_product_id
                """
            cursor.execute(sql)
            results = cursor.fetchall()

        if results:
            # Создаем словарь, где ключом будет code_oreon, а значением best_price
            oreon_bestprice = {row[0]: str(row[1]) for row in results}
            return oreon_bestprice
        else:
            raise HTTPException(status_code=404, detail='Данные не найдены')

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@app.post('/oreon_bestprice')
async def receive_ids_from_extension(data: Dict[str, List[str]]):
    try:
        ids = data.get("ids")
        if not ids:
            raise HTTPException(status_code=400, detail='Invalid data. "ids" is missing.')

        # Запрос к базе данных для получения code_oreon и best_price из двух таблиц
        with conn.cursor() as cursor:
            sql = """
                SELECT c.code_oreon, b.best_price
                FROM public.logs_cardsproduct c
                JOIN public.logs_bestprice b ON c.code = b.id_product_id
                """
            cursor.execute(sql)
            results = cursor.fetchall()

        if results:
            # Создаем словарь, где ключом будет code_oreon, а значением best_price
            oreon_bestprice = {row[0]: str(row[1]) for row in results}

            # Выводим результаты только для ключей, содержащихся в списке ids
            selected_oreon_bestprice = {key: value for key, value in oreon_bestprice.items() if key in ids}
            print(selected_oreon_bestprice)

            # Возвращаем результат в формате JSON
            return JSONResponse(content=selected_oreon_bestprice)
        else:
            return JSONResponse(content={}, status_code=404)  # Если результат не найден, возвращаем пустой объект с кодом 404
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)  # Возвращаем информацию об ошибке с кодом 500
