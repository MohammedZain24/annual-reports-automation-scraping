# src/router.router.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
import os
from fastapi import Form
import traceback 
from src.schema.schema import (
    DownloadAllRequest,
    DownloadByFilterRequest,
    DownloadSpecificCompanyRequest
)
from src.service.service import (
    download_all_companies,
    download_companies_by_filter,
    download_company_by_name,
    download_company_info_excel
)
import pandas as pd

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/download/all")

@router.post("/download/all")
def download_all(start_year: int = Form(...)):
    try:
        count, file_path = download_all_companies(start_year)
        if os.path.exists(file_path):
            return FileResponse(
                path=file_path,
                filename=os.path.basename(file_path),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        raise HTTPException(status_code=500, detail="File not found after generation.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/download/filter")
def download_filter(
    filter_type: str = Form(...),
    filter_value: str = Form(...),
    start_year: int = Form(...)
):
    try:
        if filter_type == "exchange":
            count, file_path = download_companies_by_filter(start_year=start_year, exchange=filter_value)
        elif filter_type == "industry":
            count, file_path = download_companies_by_filter(start_year=start_year, industry=filter_value)
        else:
            raise HTTPException(status_code=400, detail="Invalid filter_type. Use 'exchange' or 'industry'.")
        
        if os.path.exists(file_path):
            return FileResponse(
                path=file_path,
                filename=os.path.basename(file_path),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        raise HTTPException(status_code=500, detail="File not found after generation.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/download/company")
def download_one(
    company_name: str = Form(...),
    start_year: int = Form(...)
):
    try:
        file_path = download_company_by_name(company_name, start_year)
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Company not found or file missing.")
        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type="application/pdf"  
        )
    except Exception as e:
        traceback.print_exc()  
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/download/info-only")
def download_info_only():
    try:
        file_path = download_company_info_excel()
        if os.path.exists(file_path):
            return FileResponse(
                path=file_path,
                filename=os.path.basename(file_path),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        raise HTTPException(status_code=500, detail="File not found after generation.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





# @router.get("/options/exchanges")
# def get_exchange_options():
#     try:
#         result = extract_exchange_options()
#         return {"status": "ok", "data": result}
#     except Exception as e:
#         print(" ERROR:", e)
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))

# @router.get("/options/industries")
# def get_industry_options():
#     try:
#         industries = extract_industry_options()
#         return JSONResponse(content={"industries": industries})
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))