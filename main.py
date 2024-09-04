from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.blog.blog import blog_router, list_blog_posts, load_blog_content, get_blog_info
from api.blog import blog
from nicegui import ui
from api.home import home

app = FastAPI()

origina = [
    'localhost:8000',
    'https://localhost:8000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origina,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(blog_router)

blog.init(app)
home.init(app)