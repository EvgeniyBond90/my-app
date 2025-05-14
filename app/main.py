from fastapi import FastAPI, HTTPException,Request
from pydantic import BaseModel
import psycopg2
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Создаем экземпляр FastAPI
app = FastAPI()


# Подключение шаблонов
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники (замените на конкретные домены в продакшене)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все HTTP-методы
    allow_headers=["*"],  # Разрешить все заголовки
)

@app.options("/items/")
def options_items():
    return {"message": "CORS test complete"}



# Модель данных
class Item(BaseModel):
    name: str
    description: str = None

# Подключение к PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname="mydb",
        user="bond",
        password="123",
        host="postgres"
    )

@app.post("/items/")
def create_item(item: Item):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO items (name, description) VALUES (%s, %s)", (item.name, item.description))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Item created"}

@app.get("/items/")
def read_items():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": row[0], "name": row[1], "description": row[2]} for row in rows]


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id = %s", (item_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": f"Item {item_id} deleted"}
