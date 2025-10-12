from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
import bcrypt,re

router = APIRouter()
templates = Jinja2Templates(directory="templates")

api = RenderRequest()
# Ruta para recibir el login
@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(""),
    password: str = Form(""),
    accesscode: str = Form("")
):
    empresa = request.state.empresa 
    schema_name = "demo"  # por defecto
    login_status = "invalid"
    code_company=request.session.get("code_company")
    error = ""
    error1 = ""

    if code_company != "GRL_999":    
        consulta="identificador=" + code_company
        respuesta = await api.get_data("company",query=consulta, schema="global")  
        company=respuesta['data'][0]
        company_id=company['id']
        schema_name= company['schema_name']
        plan= company['plancode_id']
        request.session['company_name']=company['nomfantasia']
        request.session["url_redirect"]=company['website']
    else:
        company_id=0
        schema_name= "travel"

    username = username.strip()
    password = password.strip()
    accesscode = accesscode.strip()

    if not username and not accesscode:
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": "Debes ingresar usuario o código de acceso."
        })

    # Validación y hash de password
    #verificacion de password
    #bcrypt.checkpw(RutApo.encode("utf-8"), hashed)
    
    if password:
        from hashlib import md5
        password = "dfab5165845cfd585c4925b09f3a0d38"

    # 1. Buscar en usuarios
    if username and password:
        query_params = f"active=1&username={username}&password={password}"
        response = await api.get_data("users", query=query_params, schema=schema_name)
        if response["status"] == "success" and len(response["data"]) > 0:
            user = response["data"][0]
            request.session["authenticated"] = True
            request.session["position"]= "Otro"
            request.session["id"] = user["id"]
            request.session["name"] = user["name"]
            request.session["user_name"] = user["username"]
            request.session["rol"] = user["rol"]["description"]
            request.session["company"] = user["company_id"]
            request.session["schema"] = schema_name
            request.session['plancode'] = plan
            request.session["rol"] = user["rol"]["description"]

            login_status = "success"

    # 2. Buscar en cursos si no se encontró en usuarios
    if login_status == "invalid" and username:
        rut_ap = re.sub(r'[.]', '', username)
        rut_ap = rut_ap[:4]

        # clave ingresada en bytes
        rut_bytes = rut_ap.encode("utf-8")

        query_params = f"rutapod={username.upper()}&company_id={company_id}"
        response = await api.get_data("curso/informe", query=query_params, schema=schema_name)
        if response["status"] == "success" and len(response["data"]) > 0:
            course = response["data"][0]
            stored_hash = course["password"].encode("utf-8")
            if bcrypt.checkpw(rut_bytes, stored_hash):
                request.session["authenticated"]= True
                request.session["id"]= course["id"]
                request.session["name"]= course["nombreapod"]
                request.session["position"]= "Apoderado"
                request.session["company"]= course["company_id"]
                request.session["schema"]= schema_name
                request.session["sale"]= course['sale_id']
                request.session["user_rut"]= course['rutapod']
                request.session["user_ruta"]= course['rutalumno']
                request.session["user_name"]= course['nombreapod']
                request.session["user_id"]= course['id']
                request.session["typesale"]= course["sale"]["type_sale"]
                request.session["plancode"]= plan
                login_status = "success"

    # 3. Buscar por código de acceso
    if login_status == "invalid" and accesscode:
        query_params = f"accesscode={accesscode}&activo=1"
        response = await api.get_data("sale",query=query_params, schema=schema_name)

        if response["status"] == "success" and len(response["data"]) > 0:
            sale = response["data"][0]
            request.session["authenticated"]= True
            request.session["id"]= 0
            request.session["name"]= ""
            request.session["position"]= "General"
            request.session["company"]= sale["company_id"]
            request.session["schema"]= schema_name
            request.session["sale"]= sale['id']
            request.session["user_name"]= sale['encargado']
            request.session["company"]= sale["company_id"]
            request.session["typesale"]= sale["type_sale"]
            request.session["plancode"]= plan
            login_status = "success"
        else:
            error1 = "No se encontró el código de acceso."

    # Redirección final
    if login_status == "success":
        position = request.session.get("position")
        if position == "Apoderado":
            return RedirectResponse(url=f"/{empresa}/manager/payment", status_code=303)
        elif position == "General":
            return RedirectResponse(url=f"/{empresa}/manager/opening", status_code=303)
        else:
            return RedirectResponse(url=f"/{empresa}/manager/index", status_code=303)

    # Si no se logró login
    urlLogin= f"127.0.0.1:8000/{empresa}/manager"
    return templates.TemplateResponse(urlLogin, {
        "request": request,
        "error": error or error1 or "Usuario o contraseña incorrectos."
    })

# Ruta para logout
@router.get("/logout")
async def logout(request: Request):
    redirect_url = request.session.get("url_redirect", "/")
    request.session.clear()
    return RedirectResponse(url=redirect_url , status_code=302)
