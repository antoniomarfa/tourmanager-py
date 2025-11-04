from fastapi import FastAPI, Request, Form, Query
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import  HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
import os
from routes import all_routers   # <-- traemos la lista centralizada

app = FastAPI()
api = RenderRequest()

app.mount("/static", StaticFiles(directory="statics"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="templates")

app.add_middleware(SessionMiddleware, secret_key="tu_clave_secreta")

#Middleware para detectar empresa desde la URL
@app.middleware("http")
async def detectar_empresa(request: Request, call_next):
    path_parts = request.url.path.strip("/").split("/")
    empresa = path_parts[0] if len(path_parts) > 0 else None

    # Si la URL comienza con /static o /uploads, no procesamos
    if empresa in ("static", "uploads"):
        return await call_next(request)

    if empresa:
        request.state.empresa = empresa

    response = await call_next(request)
    return response

@app.get("/{empresa}/manager", response_class=HTMLResponse)
async def login_form(request: Request,empresa: str):
    #consulta=f"nomfantasia={empresa}"
    consulta=f"identificador={empresa}"
    respuesta = await api.get_data("company",query=consulta, schema="global")  
    company=respuesta['data'][0] if respuesta['status'] == 'success' else []
    
    # Validar existencia de empresa
    if not respuesta or respuesta.get('status') != 'success' or not respuesta.get('data'):
        # Mostrar mensaje de error o redirigir a una página genérica
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "mensaje": f"La empresa '{empresa}' no existe o no está activa."
            },
            status_code=404
        )


    request.session["code_company"]=company['identificador']

    ruta_image = f"/uploads/company/logo/login_logo_{request.session.get('code_company', 'GRL_999')}.png"
    ruta_image = os.path.abspath(ruta_image)
    return templates.TemplateResponse("auth/login.html", {"request": request,"ruta_image":ruta_image,"empresa": empresa})

# Incluir routers dinámicamente
for router, prefix in all_routers:
    app.include_router(router, prefix="/{empresa}/manager" + prefix)