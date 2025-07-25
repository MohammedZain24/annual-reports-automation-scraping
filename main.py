from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from src.router import router
import pandas as pd

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.include_router(router.router, prefix="/api")

exchanges = pd.read_csv("inputs\exchange_list.csv").to_dict(orient="records")
industries = pd.read_csv("inputs\industry_list.csv").to_dict(orient="records")

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "exchanges": exchanges,
        "industries": industries
    })

@app.get("/industries", response_class=HTMLResponse)
def industries_page(request: Request):
   return templates.TemplateResponse("industries.html", {
        "request": request,
        "industries": industries
    })
