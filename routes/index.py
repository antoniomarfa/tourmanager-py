from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from libraries.restriction import Restriction

rst=Restriction()

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema = request.session.get("schema")
    position = request.session.get("rol")

    raw_permisos = await rst.access_Menu(position, schema)
    #cdiccionario de acceso rápido
    permisos = {p["permission"]: True for p in raw_permisos}   
    request.session["permisos"] = permisos 
    return templates.TemplateResponse("home.html", {"request": request,"empresa": empresa})
