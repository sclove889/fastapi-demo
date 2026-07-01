from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import news, users, favorite, history
from utils.exception_handlers import register_exception_handler

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

register_exception_handler(app)

#允许的来源（可以是域名列表)
origins=[
    "http://localhost",
    "http://localhost:5173"
]
#添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  #允许访问的源
    allow_credentials=True, #允许携带 Cookie
    allow_methods=["*"],    #允许所有请求方法
    allow_headers=["*"]     #允许所有请求头
)



app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)


