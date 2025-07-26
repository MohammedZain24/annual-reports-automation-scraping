# src/router/router.py

from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import traceback

from src.service.service import (
    download_all_companies,
    download_companies_by_filter,
    download_company_by_name,
    scrape_company_info_by_filter
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


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
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download/company")
def download_one(
    company_name: str = Form(...),
    start_year: int = Form(...)
):
    try:
        result = download_company_by_name(company_name, start_year)
        if result is None:
            raise HTTPException(status_code=404, detail="Company not found.")
        
        name, file_path = result
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found.")
        
        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type="application/pdf"
        )
    except Exception as e:
        import traceback
        print(traceback.format_exc())  
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download/info-only")
def download_info_only(
    filter_type: str = Form(...),
    filter_value: str = Form(...),
    start_year: int = Form(...)
):
    try:
        if filter_type == "exchange":
            count, file_path = scrape_company_info_by_filter(
                start_year=start_year,
                exchange=filter_value
            )
        elif filter_type == "industry":
            count, file_path = scrape_company_info_by_filter(
                start_year=start_year,
                industry=filter_value
            )
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
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

