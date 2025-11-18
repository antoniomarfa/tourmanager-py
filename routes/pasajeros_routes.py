from fastapi import FastAPI, Request, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
from libraries.helper import Helper
import json, uuid, os, bcrypt,re
from datetime import datetime, timezone, timedelta
from libraries.restriction import Restriction

router = APIRouter()

templates = Jinja2Templates(directory="templates")

api = RenderRequest()
rst = Restriction()

# Ruta principal: mostrar usuarios
@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    getQuery=f'activo=1&state=V&company_id={company_id}'
    response = await api.get_data("sale",query=getQuery,schema=schema_name)
    ventas=response['data'] if response["status"] == "success" else []

    getQuery="company_id=0"
    response = await api.get_data("colegio",query= getQuery,schema=schema_name)
    schools0 = response["data"] if response["status"] == "success" else []

    getQuery=f"company_id={company_id}"
    response = await api.get_data("colegio",query= getQuery,schema=schema_name)
    schools1 = response["data"] if response["status"] == "success" else []

    schools0.extend(schools1)
    schools = schools0
     # después de combinar schools0 y schools1
    schools_dict = {s["id"]: s["nombre"] for s in schools}
    
    #Busco los Pasajeros segun la venta
    request.session['filter_sales']=""

    form_data = await request.form()
    venta = int(form_data.get('venta') or 0)

    getQuery =f'company_id={company_id}'
    if venta != 0:
        getQuery +=f'&sale_id={venta}'
        request.session['filter_sales']=venta
     
    response = await api.get_data("curso/informe",query=getQuery,schema=schema_name)
    courses = response['data'] if response['status'] == 'success' else []


    cant_access = {  
        "can_update": await rst.access_permission("course", "UPDATE", request.session),
        "can_delete": await rst.access_permission("course", "DELETE", request.session),
        "can_insert": await rst.access_permission("course", "INSERT", request.session),
        "can_export_report": True # await rst.access_permission("users", "EXPORT_REPORT", request.session)
    } 

    context =  {"request": request, 
                "session":request.session, 
                "cant_access":cant_access, 
                "sales": ventas,
                "courses": courses,
                "empresa":empresa,
                "Helper":Helper}

    return templates.TemplateResponse("pasajeros/index.html",context)

#llena la tabla
@router.post("/gettable", response_class=HTMLResponse)
async def gettable(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id = int(request.session.get("company"))
    
    can_update = await rst.access_permission("course", "UPDATE", request.session)
    can_delete = await rst.access_permission("course", "DELETE", request.session)

    request.session['filter_sales']=""

    form_data = await request.form()
    venta = int(form_data.get('venta') or 0)

    getQuery =f'company_id={company_id}'
    if venta != 0:
        getQuery +=f'&sale_id={venta}'
        request.session['filter_sales']=venta
     
    response = await api.get_data("curso/informe",query=getQuery,schema=schema_name)
    courses = response['data'] if response['status'] == 'success' else []

    table_body = []
   
    if courses:
        for course in courses:
            cnt_ingreso=0
           
            ficha=""
            filename = f"ficha-medica-{course['sale_id']}-{course['rutalumno']}.pdf"
            ruta = "https://localhost/upload/" + filename
            ficha = f'<a href="{ruta}" target="_blank"><i class="fa fa-file-pdf-o"></i></a>'

            acepta = f'<span class="badge badge text-bg-success">Aceptado</span>' if course['acepta_contrato']==1  else ''
            enviocorreo = f'<a type="button" class="btn btn-sm btn-success" data-toggle="tooltip" data-placement="top" title="Correo"  href="/pasajeros/enviarCorreo/{course["id"]}"><i class="fa fa-envelope"></i></a> '
            
            actions=""
            if can_update:
                actions += f'<a type="button" class="btn btn-sm btn-warning" data-toggle="tooltip" data-placement="top" title="" data-original-title="Editar" href="/pasajeros/edit/{course["id"]}"><i class="fa fa fa-pencil"></i></a> '
            
            if can_delete:
                if cnt_ingreso == 0:
                    actions += f'<a type="button" class="btn btn-sm btn-danger delete-register" data-toggle="tooltip" data-placement="top" title="" data-original-title="Eliminar" data-id="{course["id"]}"><i class="fa fa-trash"></i></a>'
            
            table_body.append([
                f"{course['sale_id']}-{cnt_ingreso}",
                "Gira Estudio" if course['sale']['type_sale'] == 'GE' else "Viaje Grupal",
                course['rutalumno'],
                course['nombrealumno'],
                course['rutapod'],
                course['nombreapod'],
                course['celular'],
                course['correo'],
                Helper.formato_numero(course['vpagar']),
                Helper.formato_numero(course['descto']),
                Helper.formato_numero(course['apagar']),
                acepta,
                ficha,
                enviocorreo,
                actions
                ])
        return JSONResponse(content={"data": table_body})
    else:
        return JSONResponse(content={"data": []})

# Mostrar formulario de creacion
@router.get("/create", response_class=HTMLResponse)
async def create_form(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")


    schema_name = request.session.get("schema")
    company_id = request.session.get("company")  

    hoy = datetime.today()
    fecha_hoy = hoy.strftime("%Y-%m-%d")
  
    response = await api.get_data("region",schema="global")  # Suponiendo que el servicio se llama 'users'    
    regions = response["data"] if response["status"] == "success" else {}

    response = await api.get_data("comunas",schema="global")  # Suponiendo que el servicio se llama 'users'    
    communes = response["data"] if response["status"] == "success" else {}

    getQuery=f"company_id={company_id}"
    response = await api.get_data("sale",query=getQuery,schema=schema_name)
    sales=response['data'] if response["status"] == "success" else []

    return templates.TemplateResponse("pasajeros/create.html", {"request": request, "session":request.session, "regions":regions, "communes":communes, "sales":sales,"fecha_hoy":fecha_hoy,"helper":Helper,"empresa":empresa})

#Crea los pasajeros
@router.post("/create")
async def create(request:Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    form_data = await request.form()

    #print(RutApo[:4])     # "1234"
    #print(RutApo[2:6])    # "3456"  (equivalente a substr($RutApo,2,4))

    if form_data.get('typesale') == 'VG':
        RutApo = form_data.get('rutalumno')
    else:
        RutApo = form_data.get('rutapoderado')

    RutApo = re.sub(r'[.]', '', RutApo)
    RutApo =RutApo[:4]
    hashed = bcrypt.hashpw(RutApo, bcrypt.gensalt())

    password = hashed.decode('utf-8')  # guarda como string

    fecha_obj = form_data.get('fechanac')
    if fecha_obj:
        fechanac = datetime.fromisoformat(fecha_obj).strftime('%Y-%m-%dT00:00:00Z')

    data={
        "sale_id": form_data.get('venta_id'),  
        "rutalumno": form_data.get('rutalumno'),
        "nombrealumno": form_data.get('nombrealumno'),
        "fechanac": fechanac,
        "rutapod": form_data.get('rutapoderado'),
        "nombreapod": form_data.get('nombreapoderado'),
        "dircalle": form_data.get('calle'),
        "dirnumero": form_data.get('numdir'),
        "nrodepto": form_data.get('numdepto'),
        "region_id": form_data.get('region_id'),   
        "comuna_id": form_data.get('commune_id'),  
        "fono": form_data.get('fono'),
        "celular": form_data.get('celular'),
        "correo": form_data.get('correo'),
        "vpagar": form_data.get('apagar'),
        "descto": form_data.get('descto'),
        "apagar": form_data.get('a_pagar'),
        "liberado": int(form_data.get('liberado') or 0),
        "enviado":"",
        "estado":"",
        "password": password,
        "acepta_contrato":0,
        "signature":"",
        "author": request.session.get('user_name'),
        "company_id": request.session.get("company"),
        "pasaporte": form_data.get('pasaporte')
    }
    response = await api.set_data("curso",body=json.dumps(data), schema=schema_name)
    if response.get("status") == "success":
        message = ""
    
    return RedirectResponse(url=f"/{empresa}/manager/pasajeros", status_code=303) 

# Mostrar formulario de edicion
@router.get("/edit/{course_id}", response_class=HTMLResponse)
async def edit_form(request: Request,course_id:int):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    empresa = request.state.empresa 
    
    schema_name = request.session.get("schema")
    company_id = request.session.get("company")

    response = await api.get_data("company",id=request.session.get("company"),schema="global")  # Suponiendo que el servicio se llama 'users'    
    companys = response["data"] if response["status"] == "success" else []    

    cant_access = {  
        "can_update": await rst.access_permission("course", "UPDATE", request.session),
        "can_delete": await rst.access_permission("course", "DELETE", request.session),
        "can_insert": await rst.access_permission("course", "INSERT", request.session),
        "can_export_report": True # await rst.access_permission("users", "EXPORT_REPORT", request.session)
    } 

    response = await api.get_data("region",schema="global")  # Suponiendo que el servicio se llama 'users'    
    regions = response["data"] if response["status"] == "success" else {}

    response = await api.get_data("comunas",schema="global")  # Suponiendo que el servicio se llama 'users'    
    communes = response["data"] if response["status"] == "success" else {}
    
    getQuery=f"id={course_id}"
    response = await api.get_data("curso/informe",query=getQuery,schema=schema_name)
    course = response['data'][0]if response['status'] == "success" else []

    getQuery=f"company_id={company_id}"
    response = await api.get_data("sale",query=getQuery,schema=schema_name)
    sales=response['data'] if response["status"] == "success" else []

    getQuery="company_id=0"
    response = await api.get_data("colegio",query= getQuery,schema=schema_name)
    schools0 = response["data"] if response["status"] == "success" else []

    getQuery=f"company_id={company_id}"
    response = await api.get_data("colegio",query= getQuery,schema=schema_name)
    schools1 = response["data"] if response["status"] == "success" else []

    schools0.extend(schools1)
    schools = schools0
     # después de combinar schools0 y schools1
    schools_dict = {s["id"]: s["nombre"] for s in schools}

    return templates.TemplateResponse("pasajeros/edit.html", {"request": request, "session":request.session, "cant_access":cant_access, "regions":regions, "communes":communes, "course":course,"_schools":schools_dict,"sales":sales,"helper":Helper,"empresa":empresa})

 #Editar la venta
@router.post("/update")
async def create(request:Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    form_data = await request.form()

    #print(RutApo[:4])     # "1234"
    #print(RutApo[2:6])    # "3456"  (equivalente a substr($RutApo,2,4))

    if form_data.get('typesale') == 'VG':
        RutApo = form_data.get('rutalumno')
    else:
        RutApo = form_data.get('rutapoderado')

    RutApo = re.sub(r'[.]', '', RutApo)
    RutApo =RutApo[:4]
    hashed = bcrypt.hashpw(RutApo, bcrypt.gensalt())

    password = hashed.decode('utf-8')  # guarda como string

    fecha_obj = form_data.get('fechanac')
    if fecha_obj:
        fechanac = datetime.fromisoformat(fecha_obj).strftime('%Y-%m-%dT00:00:00Z')

    data={
        "sale_id": form_data.get('venta_id'),  
        "rutalumno": form_data.get('rutalumno'),
        "nombrealumno": form_data.get('nombrealumno'),
        "fechanac": fechanac,
        "rutapod": form_data.get('rutapoderado'),
        "nombreapod": form_data.get('nombreapoderado'),
        "dircalle": form_data.get('calle'),
        "dirnumero": form_data.get('numdir'),
        "nrodepto": form_data.get('numdepto'),
        "region_id": form_data.get('region_id'),   
        "comuna_id": form_data.get('commune_id'),  
        "fono": form_data.get('fono'),
        "celular": form_data.get('celular'),
        "correo": form_data.get('correo'),
        "vpagar": form_data.get('apagar'),
        "descto": form_data.get('descto'),
        "apagar": form_data.get('a_pagar'),
        "liberado": form_data.get('liberado') or 0,
        "enviado":"",
        "estado":"",
        "password": password,
        "acepta_contrato":0,
        "signature":"",
        "author": request.session.get('user_name'),
        "company_id": request.session.get("company"),
        "pasaporte": form_data.get('pasaporte')
    }
    response = await api.update_data("curso",body=json.dumps(data), schema=schema_name)
    if response.get("status") == "success":
        message = ""
    
    return RedirectResponse(url=f"/{empresa}/manager/pasajeros", status_code=303) 

# Eliminar pasajero
@router.get("/delete/{pasajero_id}")
async def delete(request: Request,pasajero_id: int):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema") 
    response=await api.delete_data("curso", id=pasajero_id, schema=schema_name)
    message=response['status']
    error="Registro eliminado correctamente."

    if message != "success":
        error=response['error']
    request.session['flash_message'] = message    
    request.session['flash_error'] = error    
    return RedirectResponse(url=f"{empresa}/manager/pasajeros/", status_code=303)

@router.post("/getcomune")
async def status(request: Request,region_id: int = Form(...),):
    getQuery=f"regions_id={region_id}"
    response = await api.get_data("comunas",query=getQuery, schema="global")
    communes=response['data']
    return JSONResponse(
        content={
            "data": communes
        })

@router.post("/getventa")
async def status(request: Request,venta_id: int = Form(...),):
    schema_name = request.session.get("schema")
    getQuery=f"id={venta_id}"
    response = await api.get_data("sale",query=getQuery, schema=schema_name)
    print(response)
    sale = response['data'][0]
 
    subtotal=int(sale["subtotal"])
    descuento=int(sale["descm"])
    valor=int(sale["vprograma"])
    typesale=sale['type_sale']

    return JSONResponse(
        content={
            'subtotal': subtotal,
            'descuento': descuento,
            'valor': valor,
            'typesale': typesale
        })