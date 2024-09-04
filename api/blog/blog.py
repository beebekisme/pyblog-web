from datetime import datetime
import os
from typing import List
from fastapi import APIRouter, FastAPI
from nicegui import ui
from .blog_model import BlogPost
from fastapi import HTTPException

blog_router = APIRouter()

def create_blog_card(blog: BlogPost, blog_content_area: ui.column):
    with ui.link() \
                .classes('bg-[#5898d420] p-4 self-stretch rounded flex flex-col gap-2') \
                .style('box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1); text-decoration: none;') \
                .on('click', lambda: load_blog_content(blog.title, blog_content_area)):
        ui.label(blog.title).classes('text-2xl')
        ui.separator()
        ui.markdown(blog.summary).classes('bold-links arrow-links')
        ui.label(f"Created On: {blog.date.strftime('%Y-%m-%d')}")

async def list_blog_posts() -> List[str]:
    files = os.listdir('./api/blog/markdown')
    titles = []
    for file in files:
        if file.endswith('.md'):
            with open(f'./api/blog/markdown/{file}', 'r') as f:
                content = f.read()
                content_sections = content.split('---')
                if len(content_sections) < 3:
                    raise ValueError(f"Unexpected markdown format in file: {file}")
                raw = content_sections[1]
                for line in raw.split('\n'):
                    if 'Title' in line:
                        title = line.split(': ')[1]
                        titles.append(title)
    return titles

@blog_router.get('/blog/{title}')
async def get_blog_info(title: str) -> BlogPost:
    files = os.listdir('./api/blog/markdown')
    for file in files:
        if file.endswith('.md'):
            with open(f'./api/blog/markdown/{file}', 'r') as f:
                content = f.read()
                content_sections = content.split('---')
                if len(content_sections) < 3:
                    raise ValueError(f"Unexpected markdown format in file: {file}")

                raw = content_sections[1]
                file_title = None
                for line in raw.split('\n'):
                    if 'Title' in line:
                        file_title = line.split(': ')[1].strip()
                        break
                
                if file_title == title:
                    summary, date, tags, is_published = '', '', [], False
                    for line in raw.split('\n'):
                        if 'Summary' in line:
                            summary = (line.split(': ')[1])[:100] + '...' if len(line.split(': ')[1]) > 75 else line.split(': ')[1]
                        if 'Date' in line:
                            date = line.split(': ')[1]
                        if 'Tags' in line:
                            tags = line.split(': ')[1].strip('[]').split(', ')
                        if 'Published' in line:
                            is_published = line.split(': ')[1].lower() == 'true'
                    
                    content = content_sections[2]
                    return BlogPost(
                        title=file_title,
                        content=content,
                        date=datetime.strptime(date, '%Y-%m-%d'),
                        tags=tags,
                        is_published=is_published,
                        summary=summary
                    )
    raise HTTPException(status_code=404, detail="Blog not found")

async def load_blog_content(blog_id: str, blog_content_area):
    blog = await get_blog_info(blog_id)
    blog_content_area.clear()
    with blog_content_area:
        ui.label(blog.title).classes('text-2xl font-bold')
        ui.label(f"Published on: {blog.date.strftime('%Y-%m-%d')}").classes('text-sm text-gray-200')
        ui.markdown(blog.content).classes('mt-4')

async def blog_markdown_parser(blog_title: str) -> List: 
    
    pass 

def init(app: FastAPI) -> None: 
        
    @ui.page('/blog')
    async def blog_page():
        ui.page_title('Blog Posts')
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('').classes('flex-i')
            # Place the toggle button directly in the top-right corner
            ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=black')

        # Main blog content area
        with ui.column().classes('w-3/4'):
            ui.label('Blog Title').classes('text-lg font-bold')
            blog_content_area = ui.column()

        with ui.left_drawer(top_corner=False, bottom_corner=True).style('background-color: #d7e3f4'):
            ui.label('Blog Content').classes('text-lg font-bold p-2')

        with ui.right_drawer(elevated=True,fixed=False).style('background-color: #ebf1fa').props('bordered') as right_drawer:
            ui.label('Blog Posts').classes('text-lg font-bold p-2')

            with ui.scroll_area().classes('flex-1 h-[calc(100%-4rem)]'):
                for blog_id in await list_blog_posts():
                    blog = await get_blog_info(blog_id)
                    create_blog_card(blog, blog_content_area)

