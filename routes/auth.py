from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
import bcrypt, re, random, smtplib, os
from datetime import datetime, timedelta
from email.message import EmailMessage

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
    request.session["code_company"]=  empresa
    schema_name = "demo"  # por defecto
    login_status = "invalid"
    code_company=request.session.get("code_company")
    error = ""
    error1 = ""

    if code_company != "GRL_999":    
        consulta=f"identificador={code_company}"
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
        #query_params = f"active=1&username={username}&password={password}&company_id={company_id}"
        query_params = f"username={username}&password={password}&company_id={company_id}"
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
         #   if bcrypt.checkpw(rut_bytes, stored_hash):
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
            request.session['user_curso_id']=0
            request.session["sale"]= sale['id']
            request.session["user_sale"]= sale['id']
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
    else:
        return RedirectResponse(url=f"/{empresa}/manager", status_code=303)
    # Si no se logró login
    #urlLogin= f"127.0.0.1:8000/{empresa}/manager"
    #return templates.TemplateResponse(urlLogin, {
    #    "request": request,
    #   "error": error or error1 or "Usuario o contraseña incorrectos."
    #})

# Ruta para logout
@router.get("/logout")
async def logout(request: Request):
    redirect_url = request.session.get("url_redirect", "/")
    request.session.clear()
    return RedirectResponse(url=redirect_url , status_code=302)

# ============= SISTEMA DE RECUPERACIÓN DE CONTRASEÑA =============

# Función auxiliar para enviar código por correo
async def send_verification_code(email: str, code: str, company_name: str, empresa: str):
    """Envía el código de verificación al correo del usuario"""
    try:
        # Configuración SMTP desde variables de entorno
        SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
        USERNAME = os.getenv("USERNAME")
        PASSWORD = os.getenv("PASSWORD")
        
        if not USERNAME or not PASSWORD:
            raise Exception("Credenciales SMTP no configuradas")
        
        # Crear el mensaje
        msg = EmailMessage()
        msg['Subject'] = f'Código de Recuperación de Contraseña - {company_name}'
        msg['From'] = USERNAME
        msg['To'] = email
        
        # Cuerpo del correo en HTML
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; color: #2e58a6; margin-bottom: 30px; }}
                .code-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px; margin: 20px 0; }}
                .code {{ font-size: 36px; font-weight: bold; letter-spacing: 10px; }}
                .info {{ color: #666; font-size: 14px; line-height: 1.6; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Recuperación de Contraseña</h1>
                    <h3>{company_name}</h3>
                </div>
                
                <p class="info">Hola,</p>
                <p class="info">Has solicitado recuperar tu contraseña. Utiliza el siguiente código de verificación:</p>
                
                <div class="code-box">
                    <div class="code">{code}</div>
                    <p style="margin-top: 10px; font-size: 14px;">Código de Verificación</p>
                </div>
                
                <p class="info">Este código es válido por <strong>15 minutos</strong>.</p>
                <p class="info">Si no solicitaste este código, puedes ignorar este correo de forma segura.</p>
                
                <div class="footer">
                    <p>Este es un correo automático, por favor no respondas.</p>
                    <p>&copy; {datetime.now().year} {company_name}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.add_alternative(html_body, subtype='html')
        
        # Enviar el correo
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(USERNAME, PASSWORD)
            smtp.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
        return False

# Ruta GET: Mostrar formulario de recuperación de contraseña
@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_form(request: Request):
    empresa = request.state.empresa
    
    # Obtener información de la empresa para la imagen
    consulta = f"identificador={empresa}"
    respuesta = await api.get_data("company", query=consulta, schema="global")
    ruta_image = "uploads/company/logo/login_logo_GRL_999.png"  # Imagen por defecto
    ruta_image = os.path.abspath(ruta_image)
    if respuesta['status'] == 'success' and len(respuesta['data']) > 0:
        company = respuesta['data'][0]
        if len(company) > 1:
            ruta_image = f"/uploads/company/logo/login_logo_{company['identificador']}.png"
            ruta_image = os.path.abspath(ruta_image)

    return templates.TemplateResponse("auth/forgot_password.html", {
        "request": request,
        "empresa": empresa,
        "ruta_image": ruta_image
    })

# Ruta POST: Procesar solicitud de recuperación y enviar código
@router.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password_send_code(request: Request, email: str = Form("")):
    empresa = request.state.empresa
    schema_name = "demo"
    
    # Obtener información de la empresa
    consulta = f"identificador={empresa}"
    respuesta = await api.get_data("company", query=consulta, schema="global")
    
    ruta_image = f"/uploads/company/logo/login_logo_GRL_999.png"
    ruta_image = os.path.abspath(ruta_image)
    company_name = "Sistema"
    company_id = 0
    
    if respuesta['status'] == 'success' and len(respuesta['data']) > 0:
        company = respuesta['data'][0]
        company_id = company['id']
        schema_name = company['schema_name']
        company_name = company['nomfantasia']
        if company:
            ruta_image = f"/uploads/company/logo/login_logo_{company['identificador']}.png"
            ruta_image = os.path.abspath(ruta_image)
    
    email = email.strip().lower()
    
    if not email:
        return templates.TemplateResponse("auth/forgot_password.html", {
            "request": request,
            "empresa": empresa,
            "ruta_image": ruta_image,
            "error": "Debes ingresar un correo electrónico."
        })
    
    # Buscar usuario por email en la tabla users
    query_params = f"email={email}&company_id={company_id}"
    response = await api.get_data("users", query=query_params, schema=schema_name)
    
    user = None
    user_type = None  # 'user' o 'passenger'
    
    if response["status"] == "success" and len(response["data"]) > 0:
        user = response["data"][0]
        user_type = "user"
    else:
        # Si no se encuentra en users, buscar en cursos (pasajeros)
        query_params = f"correo={email}&company_id={company_id}"
        response = await api.get_data("curso/informe", query=query_params, schema=schema_name)
        
        if response["status"] == "success" and len(response["data"]) > 0:
            user = response["data"][0]
            user_type = "passenger"
    
    # Si no se encontró en ninguna tabla
    if user is None:
        return templates.TemplateResponse("auth/forgot_password.html", {
            "request": request,
            "empresa": empresa,
            "ruta_image": ruta_image,
            "error": "No se encontró ninguna cuenta asociada a este correo electrónico."
        })
    
    # Generar código aleatorio de 6 dígitos
    verification_code = str(random.randint(100000, 999999))
    
    # Guardar en sesión el código, email, tipo de usuario y tiempo de expiración
    request.session["reset_code"] = verification_code
    request.session["reset_email"] = email
    request.session["reset_user_id"] = user["id"]
    request.session["reset_user_type"] = user_type  # 'user' o 'passenger'
    request.session["reset_expires"] = (datetime.now() + timedelta(minutes=15)).isoformat()
    
    # Enviar código por correo
    email_sent = await send_verification_code(email, verification_code, company_name, empresa)
    
    if not email_sent:
        return templates.TemplateResponse("auth/forgot_password.html", {
            "request": request,
            "empresa": empresa,
            "ruta_image": ruta_image,
            "error": "Error al enviar el correo. Por favor, intenta nuevamente."
        })
    
    # Redirigir a la página de verificación
    return RedirectResponse(url=f"/{empresa}/manager/verify-code", status_code=303)

# Ruta GET: Mostrar formulario de verificación de código
@router.get("/verify-code", response_class=HTMLResponse)
async def verify_code_form(request: Request):
    empresa = request.state.empresa
    
    # Verificar que exista una sesión de recuperación activa
    if "reset_email" not in request.session:
        return RedirectResponse(url=f"/{empresa}/manager/forgot-password", status_code=303)
    
    # Obtener información de la empresa para la imagen
    consulta = f"identificador={empresa}"
    respuesta = await api.get_data("company", query=consulta, schema="global")
    
    ruta_image = "/statics/images/login_logo_GRL_999.png"
    if respuesta['status'] == 'success' and len(respuesta['data']) > 0:
        company = respuesta['data'][0]
        if len(company) > 1:
            ruta_image = f"/uploads/company/logo/login_logo_{request.session.get('code_company', 'GRL_999')}.png"
            ruta_image = os.path.abspath(ruta_image)
    
    return templates.TemplateResponse("auth/verify_code.html", {
        "request": request,
        "empresa": empresa,
        "ruta_image": ruta_image,
        "email": request.session.get("reset_email")
    })

# Ruta POST: Verificar código y permitir acceso
@router.post("/verify-code", response_class=HTMLResponse)
async def verify_code_process(request: Request, code: str = Form("")):
    empresa = request.state.empresa
    schema_name = "demo"
    
    # Obtener información de la empresa
    consulta = f"identificador={empresa}"
    respuesta = await api.get_data("company", query=consulta, schema="global")
    
    ruta_image = "/uploads/company/logo/login_logo_GRL_999.png"
    company_id = 0
    plan = None
    
    if respuesta['status'] == 'success' and len(respuesta['data']) > 0:
        company = respuesta['data'][0]
        company_id = company['id']
        schema_name = company['schema_name']
        plan = company['plancode_id']
        request.session['company_name'] = company['nomfantasia']
        if company:
            ruta_image = f"/uploads/company/logo/login_logo_{company['identificador']}.png"
    
    # Verificar que exista una sesión de recuperación activa
    if "reset_code" not in request.session or "reset_email" not in request.session:
        return RedirectResponse(url=f"/{empresa}/manager/forgot-password", status_code=303)
    
    # Verificar expiración del código
    expires_str = request.session.get("reset_expires")
    if expires_str:
        expires = datetime.fromisoformat(expires_str)
        if datetime.now() > expires:
            # Limpiar sesión
            request.session.pop("reset_code", None)
            request.session.pop("reset_email", None)
            request.session.pop("reset_user_id", None)
            request.session.pop("reset_expires", None)
            
            return templates.TemplateResponse("auth/verify_code.html", {
                "request": request,
                "empresa": empresa,
                "ruta_image": ruta_image,
                "email": request.session.get("reset_email", ""),
                "error": "El código ha expirado. Por favor, solicita uno nuevo."
            })
    
    code = code.strip()
    stored_code = request.session.get("reset_code")
    
    # Verificar que el código coincida
    if code != stored_code:
        return templates.TemplateResponse("auth/verify_code.html", {
            "request": request,
            "empresa": empresa,
            "ruta_image": ruta_image,
            "email": request.session.get("reset_email"),
            "error": "Código incorrecto. Por favor, verifica e intenta nuevamente."
        })
    
    # Código correcto - Obtener información del usuario según el tipo
    user_id = request.session.get("reset_user_id")
    user_type = request.session.get("reset_user_type")
    
    if user_type == "user":
        # Buscar en la tabla users
        response = await api.get_data("users", id=user_id, schema=schema_name)
        
        if response["status"] != "success":
            return templates.TemplateResponse("auth/verify_code.html", {
                "request": request,
                "empresa": empresa,
                "ruta_image": ruta_image,
                "email": request.session.get("reset_email"),
                "error": "Error al recuperar información del usuario."
            })
        
        user = response["data"]
        
        # Limpiar datos de recuperación
        request.session.pop("reset_code", None)
        request.session.pop("reset_email", None)
        request.session.pop("reset_user_id", None)
        request.session.pop("reset_user_type", None)
        request.session.pop("reset_expires", None)
        
        # Iniciar sesión automáticamente como usuario normal
        request.session["authenticated"] = True
        request.session["position"] = "Otro"
        request.session["id"] = user["id"]
        request.session["name"] = user["name"]
        request.session["user_name"] = user["username"]
        request.session["rol"] = user["rol"]["description"]
        request.session["company"] = user["company_id"]
        request.session["schema"] = schema_name
        request.session['plancode'] = plan
        
        # Redirigir al dashboard
        return RedirectResponse(url=f"/{empresa}/manager/index", status_code=303)
    
    elif user_type == "passenger":
        # Buscar en la tabla curso
        query_params = f"id={user_id}"
        response = await api.get_data("curso/informe", query=query_params, schema=schema_name)
        
        if response["status"] != "success" or len(response["data"]) == 0:
            return templates.TemplateResponse("auth/verify_code.html", {
                "request": request,
                "empresa": empresa,
                "ruta_image": ruta_image,
                "email": request.session.get("reset_email"),
                "error": "Error al recuperar información del pasajero."
            })
        
        course = response["data"][0]
        
        # Limpiar datos de recuperación
        request.session.pop("reset_code", None)
        request.session.pop("reset_email", None)
        request.session.pop("reset_user_id", None)
        request.session.pop("reset_user_type", None)
        request.session.pop("reset_expires", None)
        
        # Iniciar sesión automáticamente como pasajero/apoderado
        request.session["authenticated"] = True
        request.session["id"] = course["id"]
        request.session["name"] = course["nombreapod"]
        request.session["position"] = "Apoderado"
        request.session["company"] = course["company_id"]
        request.session["schema"] = schema_name
        request.session["sale"] = course['sale_id']
        request.session["user_rut"] = course['rutapod']
        request.session["user_ruta"] = course['rutalumno']
        request.session["user_name"] = course['nombreapod']
        request.session["user_id"] = course['id']
        request.session["typesale"] = course["sale"]["type_sale"]
        request.session["plancode"] = plan
    
        # Redirigir a la página de pagos
        return RedirectResponse(url=f"/{empresa}/manager/payment", status_code=303)
    
    else:
        # Tipo de usuario desconocido
        return templates.TemplateResponse("auth/verify_code.html", {
            "request": request,
            "empresa": empresa,
            "ruta_image": ruta_image,
            "email": request.session.get("reset_email"),
            "error": "Error: tipo de usuario no válido."
        })

