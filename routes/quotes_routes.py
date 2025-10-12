from fastapi import FastAPI, Request, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
from libraries.helper import Helper
import json, uuid
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

    getQuery = f"active=1&company_id={company_id}"
    response = await api.get_data("users",query= getQuery,schema=schema_name)
    sellers = response["data"] if response["status"] == "success" else []

    getQuery="company_id=0"
    response = await api.get_data("colegio",query= getQuery,schema=schema_name)
    schools0 = response["data"] if response["status"] == "success" else []

    getQuery=f"company_id={company_id}"
    response = await api.get_data("colegio",query= getQuery,schema=schema_name)
    schools1 = response["data"] if response["status"] == "success" else []

    schools0.extend(schools1)
    schools = schools0

    # Fecha de hoy
    hoy = datetime.today()
    now_date = hoy.strftime("%Y-%m-%d")

    # Fecha de hoy
    hoy = datetime.today()
    end_date = hoy.strftime("%Y-%m-%d")

    # Fecha de hace 15 días
    menos_15 = hoy - timedelta(days=15)
    start_date = menos_15.strftime("%Y-%m-%d")
    
    cant_access = {  
        "can_update": await rst.access_permission("quotes", "UPDATE", request.session),
        "can_delete": await rst.access_permission("quotes", "DELETE", request.session),
        "can_insert": await rst.access_permission("quotes", "INSERT", request.session)
    }
    return templates.TemplateResponse("quotes/index.html", {"request": request, "session":request.session,"cant_access":cant_access,"_schools": schools,"schools": schools, "sellers": sellers,"end_date":end_date,"start_date":start_date,"now_date":now_date,"empresa":empresa})

#llena la tabla
@router.post("/gettable", response_class=HTMLResponse)
async def gettable(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
    schema_name = request.session.get("schema")
    can_update= await rst.access_permission("quotes", "UPDATE", request.session),
    can_delete= await rst.access_permission("quotes", "DELETE", request.session),

    form_data = await request.form()
    start_date= Helper.format_date_action(form_data.get("start_date"))
    end_date = Helper.format_date_action(form_data.get("end_date"))
    vendedor = form_data.get("vendedor")

    company_id=int(request.session.get('company'))
    getQuery=f'start_date={start_date}&end_date={end_date}&company_id={company_id}'
        
    if vendedor:
        consulta +='&seller_id={vendedor}'
                
    response = await api.get_data("quotes/informe", query=getQuery,schema=schema_name)
    quotes = response["data"] if response["status"] == "success" else []

    table_body = []

    if quotes:
        for quote in quotes:
            # Select status
            if quote['estado'] == 'C':
                select_status = f'''
                    <a style="cursor: pointer;" class="change-status" data-id="{quote['id']}">
                        <span class="badge text-bg-warning">Cotizacion</span>
                    </a>
                '''
            else:
                select_status = f'''<span class="badge text-bg-danger">Rechazado</span>''' if quote['estado'] == 'R' else f'''<span class="badge text-bg-success">Aceptada</span>'''

            # Colegio
            colegio = "" if quote['establecimiento_id'] == 1 else quote.get('colegios', {}).get('nombre', '')

            # Actions
            actions = ""
            if can_update:  # reemplazar por tu módulo real
                if quote['estado'] == "C":
                    if quote['type_sale'] == 'VG':
                        actions += f'<a class="btn btn-sm btn-warning" href="/quote/editvg/{quote["id"]}"><i class="fa fa-pencil"></i></a> '
                    else:
                        actions += f'<a class="btn btn-sm btn-warning" href="/quote/editge/{quote["id"]}"><i class="fa fa-pencil"></i></a> '
            if can_delete:
                actions += f'<a class="btn btn-sm btn-danger cancel-register" id="{quote["id"]}"><i class="fa fa-trash"></i></a>'

            # Construcción de la fila
            table_body.append([
                quote['id'],
                quote['identificador'],
                "Gira Estudio" if quote['type_sale'] == 'GE' else "Viaje Grupal",
                quote['fecha'],
                quote.get('users', {}).get('username', ''),
                colegio,
                quote['pasajeros'],
                quote.get('programac', {}).get('name', ''),
                Helper.formato_numero(quote['subtotal']),
                Helper.formato_numero(quote['desc']),
                Helper.formato_numero(quote['vprograma']),
                quote['contacto'],
                quote['contactofono'],
                quote['contactoemail'],
                select_status,
                quote['author'],
                Helper.formatear_modificador(quote['UpdatedDate']),
                actions
            ])

        return JSONResponse(content={"data": table_body})
    else:
        return JSONResponse(content={"data": []})   

# Mostrar formulario de creación
@router.get("/create/{type}", response_class=HTMLResponse)
async def create_form(request: Request,type:str):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
        
    schema_name = request.session.get("schema")
    company_id = int(request.session.get("company"))
    response = await api.get_data("company",schema="global")  # Suponiendo que el servicio se llama 'users'    
    companys = response["data"] if response["status"] == "success" else []    

    #viaje grupal
    getQuey=f"active=1&company_id={company_id}"
    response = await api.get_data("users",query=getQuey,schema=schema_name)  # Suponiendo que el servicio se llama 'users'    
    sellers = response["data"] if response["status"] == "success" else []    

    getQuey=f"active=1&company_id={company_id}"
    response = await api.get_data("programac",query=getQuey,schema=schema_name)  # Suponiendo que el servicio se llama 'users'    
    programs = response["data"] if response["status"] == "success" else []    

    if type == "ge":            
        getQuery="company_id=0"
        response = await api.get_data("colegio",query= getQuery,schema=schema_name)
        schools0 = response["data"] if response["status"] == "success" else []

        getQuery=f"company_id={company_id}"
        response = await api.get_data("colegio",query= getQuery,schema=schema_name)
        schools1 = response["data"] if response["status"] == "success" else []

        schools0.extend(schools1)
        schools = schools0
  

    hoy = datetime.today()
    fecha_hoy = hoy.strftime("%d/%m/%Y")

    if type == "vg":    
        return templates.TemplateResponse("quotes/createvg.html", {"request": request, "sellers":sellers, "programs":programs,"quote_date":fecha_hoy,"session": request.session,"empresa":empresa})
    else: 
        return templates.TemplateResponse("quotes/createge.html", {"request": request, "sellers":sellers, "programs":programs,"schools":schools ,"quote_date":fecha_hoy,"session": request.session,"empresa":empresa})

#Crea la Cotizacion
@router.post("/create")
async def create(request:Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")    
    schema_name = request.session.get("schema")
    form_data = await request.form()
    identificador = uuid.uuid4().hex

    colegio=1
    curso=0
    idcurso=""    
    if form_data.get('typesale') == 'GE':
        colegio=int(form_data.get('sel_colegio'))
        curso=int(form_data.get('curso'))
        idcurso=form_data.get('idcurso')

    # Convertir a objeto datetime
    fecha_obj = datetime.strptime(form_data.get('quote_date'), "%d/%m/%Y")

    # Formatear a m/d/Y
    quotedate = fecha_obj.strftime("%Y-%m-%d") + "T00:00:00Z"   
    
    data = {     
            "fecha": quotedate,
            "identificador": identificador,
            "seller_id": int(form_data.get('sel_vendedor')),
            "establecimiento_id": colegio,
            "curso": curso,
            "idcurso": idcurso,
            "pasajeros": int(form_data.get('nroalumno',0)),
            "programa_id": int(form_data.get('sel_programa')),
            "subtotal": int(form_data.get('vprograma',0)),
            "desc": int(form_data.get('vdescuento',0)),
            "vprograma": int(form_data.get('vtotalprog',0)),
            "tipocambio": int(form_data.get('tipocambio')),
            "contacto": form_data.get('contactonombre'),
            "contactofono": form_data.get('contactofono'),
            "contactoemail": form_data.get('contactoemail'),
            "estado": form_data.get('status'),
            "obsestado": form_data.get('Observacion') or "",
            "company_id": int(request.session.get("company")),
            "from_quote":0,
            "author": request.session.get('user_name'),
            "type_sale": form_data.get('typesale'),
            "sale_id":0		
        }
    resp = await api.set_data("quotes", body=json.dumps(data), schema=schema_name)
    return RedirectResponse(url=f"{empresa}/manager/quotes", status_code=303)  


#Buscar valor de programa
@router.post("/getprogramvalue", response_class=HTMLResponse)
async def programvalue(request: Request):
    schema_name = request.session.get("schema")
    form_data = await request.form()
    program_id = int(form_data.get("program_id") or 0)
    nroalumno = int(form_data.get("nroalumno",0))

    getQuery=f"programa_id={program_id}"
    response = await api.get_data("programad",query=getQuery,schema=schema_name)
    programs = response["data"] if response["status"] == "success" else []

    programval = 0
    liberados = 0
    for program in programs:           
        desde = int(program['desde'])
        hasta = int(program['hasta'])
        if desde <= nroalumno <= hasta:
            programval = int(program['valor'])
            liberados = int(program['liberado'])
            break  # Ya encontramos la coincidencia     

    return JSONResponse(content={
        'programval': programval,
        'liberados': liberados
    })


#Cambio estado cotizacion
@router.post("/setstatus")
async def setstatus(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
    schema_name = request.session.get("schema")

    form_data = await request.form()
    status = form_data.get("status")
    id_quote = int(form_data.get("id_quote"))

    error = 1
    message = "Estado de Cotización no se actualizó."

    if status:

       data = {"estado" : status}
       response = await api.update_data("quotes", id=id_quote ,body=json.dumps(data), schema=schema_name)
       message="Estado de Cotizacion  actualizado correctamente." if response["status"] == "success" else "Estado de Cotizacion  no set actualizo." 
       error = 0 if response["status"] == "success" else 1
       if status=='A':
            message = 'Cambio de estatus Cotizacion.'
                            
    return JSONResponse(content={
        "error": error,
        "message": message
        })

# Anular Cotizacion 
@router.get("/cancel/{quote_id}", response_class=HTMLResponse)
async def delete(request: Request,quote_id: int):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
    schema_name = request.session.get("schema")

    data = {"estado" : 'N'}
    response = await api.set_data("quotes", id=quote_id ,body=json.dumps(data), schema=schema_name)
    message="Cotizacion Anulada Correctamente" if response["status"] == "success" else "Cotizacion no fue Anulada." 
    error = 0 if response["status"] == "success" else 1
                            
    return JSONResponse(content={
        "error": error,
        "message": message
        })
