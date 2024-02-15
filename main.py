from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import psycopg2

app = FastAPI()

conn = psycopg2.connect(
    dbname='backup',
    user='postgres',
    password='postgres',
    host='localhost'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://optvideo.com"],  
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post('/oreon_bestprice')
async def receive_ids_from_extension(data: Dict[str, List[str]]):
    try:
        ids = data.get("ids")
        if not ids:
            raise HTTPException(status_code=400, detail='Invalid data. "ids" is missing.')

        with conn.cursor() as cursor:
            sql = """
                SELECT c.code_oreon, b.best_price
                FROM public.logs_cardsproduct c
                JOIN public.logs_bestprice b ON c.code = b.id_product_id
                """
            cursor.execute(sql)
            results = cursor.fetchall()

        if results:
            oreon_bestprice = {row[0]: str(row[1]) for row in results}

            selected_oreon_bestprice = {'Offers_' + key: value for key, value in oreon_bestprice.items() if key in ids}

            return JSONResponse(content=selected_oreon_bestprice)
        else:
            return JSONResponse(content={}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500) 
