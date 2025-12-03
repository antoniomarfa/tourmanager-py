from fastapi import FastAPI, Request, Form, Depends, APIRouter,UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from libraries.renderrequest import RenderRequest
from libraries.helper import Helper
from pathlib import Path
import shutil,os,json

router = APIRouter()

templates = Jinja2Templates(directory="templates")

api = RenderRequest()

UPLOAD_DIR = Path("uploads/company")
UPLOAD_DIR_IMG = Path("uploads/company/logo")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR_IMG.mkdir(parents=True, exist_ok=True)

# Mostrar formulario de edición
@router.get("/edit", response_class=HTMLResponse)
async def edit_form(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
       
    response = await api.get_data("region",schema="global")  # Suponiendo que el servicio se llama 'users'    
    regions = response["data"] if response["status"] == "success" else []

    response = await api.get_data("comunas",schema="global")  # Suponiendo que el servicio se llama 'users'    
    communes = response["data"] if response["status"] == "success" else []

    response = await api.get_data("company",id=request.session.get("company") ,schema="global")  # Suponiendo que el servicio se llama 'users'    
    company = response["data"] if response["status"] == "success" else []

    flash = Helper.get_flash(request)

    context = {
        "request": request,
        "company": company,
        "regions": regions,
        "communes": communes,
        "session": request.session,
        "empresa": empresa,
        "msg": flash.get("success"),
        "error": flash.get("error")
    }


    return templates.TemplateResponse("company/edit.html", context)

# Actualizar compañia
@router.post("/update")
async def update(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")   
     
    schema_name = request.session.get("schema")

    form_data = await request.form()
    payload = dict(form_data)  # convierte a dict para enviar como JSON o lo que sea

    company_id = int(payload.pop("id"))
    
     # Obtener archivos
    contratoge: UploadFile = form_data.get("contratoge")
    contratovg: UploadFile = form_data.get("contratovg")
    archive_image: UploadFile = form_data.get("archive_image")

    payload["author"] = request.session.get("user_name")
    
    payload = {
                "rut": form_data.get('rut'),
                "razonsocial": form_data.get('rsocial'),
                "nomfantasia": form_data.get('nfantasia'),
                "direccion": form_data.get('direccion'),
                "comuna_id": int(form_data.get('commune_id')),
                "region_id": int(form_data.get('region_id')),
                "rutreplegal": form_data.get('rutrl'),
                "nomreplegal": form_data.get('rl'),
                "nombrecontacto1": form_data.get('nombrecontacto1'),
                "fonocontacto1": form_data.get('fonocontacto1'),
                "emailcontacto1": form_data.get('emailcontacto1'),
                "nombrecontacto2": form_data.get('nombrecontacto2'),
                "fonocontacto2": form_data.get('fonocontacto2'),
                "emailcontacto2": form_data.get('emailcontacto2'),
                "contrato": "",
                "contratovg": "",
                "author":request.session.get("user_name"),
                "active": 1,
                "website": form_data.get('website'),
                "email": form_data.get('email'),
                "additionaluser": int(form_data.get('aditionaluser') or 0)
            }

    json_payload = json.dumps(payload)
    response = await api.update_data("company", id=company_id, body=json_payload, schema=schema_name)
    print(response)
    if response['status']=='success':
        message="Grabado Ok"
        Helper.flash_message(request, "success", "Empresa actualizada correctamente.")
        # === Guardar archivos si existen con validaciones ===
        company = request.session.get("company")
        MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
        
        contrato_dir = UPLOAD_DIR / "contrato" / str(company)
        contrato_dir.mkdir(parents=True, exist_ok=True)

        # Validar y guardar contrato de gira de estudio
        if contratoge and contratoge.filename:
            # Validar extensión
            ext = os.path.splitext(contratoge.filename)[1].lower()
            if ext != ".docx":
                Helper.flash_message(request, "error", "El archivo de Contrato GE debe ser .docx")
                return RedirectResponse(url=f"/{empresa}/manager/company/edit", status_code=303)
            
            # Validar tamaño
            contents = await contratoge.read()
            if len(contents) > MAX_FILE_SIZE:
                Helper.flash_message(request, "error", f"El archivo de Contrato GE excede el tamaño máximo de 2MB")
                return RedirectResponse(url=f"/{empresa}/manager/company/edit", status_code=303)
            
            # Guardar archivo
            nuevo_nombre = f"Contratoge_{request.session.get('code_company')}{ext}"
            file_location = contrato_dir / nuevo_nombre
            with open(file_location, "wb") as buffer:
                buffer.write(contents)

        # Validar y guardar contrato de viajes grupales
        if contratovg and contratovg.filename:
            # Validar extensión
            ext = os.path.splitext(contratovg.filename)[1].lower()
            if ext != ".docx":
                Helper.flash_message(request, "error", "El archivo de Contrato VG debe ser .docx")
                return RedirectResponse(url=f"/{empresa}/manager/company/edit", status_code=303)
            
            # Validar tamaño
            contents = await contratovg.read()
            if len(contents) > MAX_FILE_SIZE:
                Helper.flash_message(request, "error", f"El archivo de Contrato VG excede el tamaño máximo de 2MB")
                return RedirectResponse(url=f"/{empresa}/manager/company/edit", status_code=303)
            
            # Guardar archivo
            nuevo_nombre = f"Contratovg_{request.session.get('code_company')}{ext}"
            file_location = contrato_dir / nuevo_nombre
            with open(file_location, "wb") as buffer:
                buffer.write(contents)

        # Validar y guardar logo
        if archive_image and archive_image.filename:
            # Validar extensión
            ext = os.path.splitext(archive_image.filename)[1].lower()
            if ext != ".png":
                Helper.flash_message(request, "error", "El logo debe ser un archivo .png")
                return RedirectResponse(url=f"/{empresa}/manager/company/edit", status_code=303)
            
            # Validar tamaño
            contents = await archive_image.read()
            if len(contents) > MAX_FILE_SIZE:
                Helper.flash_message(request, "error", f"El logo excede el tamaño máximo de 2MB")
                return RedirectResponse(url=f"/{empresa}/manager/company/edit", status_code=303)
            
            # Guardar archivo
            nuevo_nombre = f"login_logo_{request.session.get('code_company')}{ext}"
            file_location = UPLOAD_DIR_IMG / nuevo_nombre
            UPLOAD_DIR_IMG.mkdir(parents=True, exist_ok=True)
            with open(file_location, "wb") as buffer:
                buffer.write(contents)
    if response['status']=='error':
        Helper.flash_message(request, "error", response["message"])

    return RedirectResponse(url=f"/{empresa}/manager/index", status_code=303)


@router.post("/getcomune")
async def status(request: Request,region_id: int = Form(...),):
    getQuery=f"regions_id={region_id}"
    response = await api.get_data("comunas",query=getQuery, schema="global")
    communes=response['data']
    return JSONResponse(
        content={
            "data": communes
        })