from fastapi import FastAPI, Request, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
from libraries.helper import Helper
import requests,json, uuid, os, bcrypt,re
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

    respuesta = await api.get_data("country",schema="global")
    country= respuesta['data'] if respuesta['status']=='success' else []

    respuesta = await api.get_data("airports",schema="global")
    airport=respuesta['data'] if respuesta['status']=='success' else []

    consulta=f'state=V&company_id={company_id}'
    respuesta = await api.get_data("sale/informe",query=consulta,schema=schema_name)
    sale=respuesta['data'] if respuesta['status']=='success' else []

     # Fecha de hoy
    hoy = datetime.today()
    start_date = hoy.strftime("%Y-%m-%d")
    return templates.TemplateResponse("gdsair/index.html", {"request": request,"countrys":country,"airports":airport,"sale":sale,"start_date":start_date,"empresa":empresa})            

#get vuelos
@router.post("/getflights", response_class=HTMLResponse)
async def getflights(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id = int(request.session.get("company"))

    form_data = await request.form()
    country_origin = form_data.get('origin')    
    country_destination = form_data.get('destination')
    origin_code = form_data.get('origincode')    
    destination_code = form_data.get('destinationcode')
    sale = form_data.get('sale')
    max = form_data.get('cnt_offers')
    start_date= form_data.get('start_date')
    date_min= form_data.get('start_date')
        
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        menos_15 = start_date + timedelta(days=4)
        date_max = menos_15.strftime("%Y-%m-%d")

    #date_min = start_date
    html=""
        
        
    #buscar los aeropuestos de salida y destino segun el pais solicitado
    origin={}
    consulta=f'country={country_origin}'
    respuesta = await api.get_data("airports", schema="global")
    origin_airport=respuesta['data'] if respuesta['status'] == 'success' else []
    for item in origin_airport:
        origin[item['iata']] = item['name']

    destination={}
    consulta=f'country={country_destination}'
    respuesta = await api.get_data("airports", schema="global")
    destination_airport= respuesta['data'] if respuesta['status'] == 'success' else []
    for item in origin_airport:
        destination[item['iata']]=item['name'];    
        
    #obtener token    
    client_id = 'dPNt0QeocGA7Rd9G2plAEoDDzCTkjpuw'
    client_secret = '9icdTUq8xg4bqnQg'

    url = 'https://test.api.amadeus.com/v1/security/oauth2/token'

    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        access_token = result["access_token"]
        print("Access Token:", access_token)
    else:
        print("Error:", response.status_code, response.text)


    #Oferta vuelos
    url=f'https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode={origin_code}&destinationLocationCode={destination_code}&departureDate={date_min}&returnDate={date_max}&adults=1&max={max}'

    headers = {
         "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        result = response.json()
    else:
        print("Error:", response.status_code, response.text)

    meta=result['meta']

    if meta['count']>0:

        count_offers=len(result['data'])
 
        aircraft={}
        carriers={}
        dictionaries=result['dictionaries']['aircraft']
        
        for index, value in dictionaries.items():
            code=str(index)
            aircraft[code]=value
            
        

        dictionaries=result['dictionaries']['carriers']
        for index, value in dictionaries.items():
            code=str(index)
            carriers[code]=value
               
    
        #crear informe
        html=""
        error=0
    
        html +='<ul class="nav nav-tabs left-aligned">'

        for i in range(0,count_offers):
            if i == 0:
                active = "active"
            else:
                active = ""

            cnt = i + 1
            html += '''
                <li class="nav-item">
                    <a class="nav-link '.$active.'" href="#tab'.$i.'" data-toggle="tab">
                        <h4>Oferta '.$cnt.'/'.$count_offers.'</h4>
                    </a>
                </li>
            '''
        
        html +='</ul>'
        html += '<div class="tab-content">'
        for i in range (0,count_offers):
            data=result['data'][i]
            numberOfBookableSeats=data['numberOfBookableSeats']
            itineraries=data["itineraries"]
            travelerPricings=data['travelerPricings']
            if i==0:
               active = "active"
            else:    
               active = ''
             
            html+=f'<div class="tab-pane {active}" id="tab{i}">'
                
            for indexi, itinerary in enumerate(itineraries):
                if indexi == 0:    
                    tipoViaje = 'IDA'
                else:
                    tipoViaje = 'VUELTA'

                html += f"<h3>{tipoViaje}</h3>"
                html += f"<p><strong>Duracion total:</strong>{format_duration(itinerary['duration'])}</p>"
                
                for segmento in itinerary['segments']:
                    airline = carriers.get(segmento['carrierCode'], 'Desconocida') 
                    airport_or = origin.get(segmento['departure']['iataCode'], 'Desconocido')
                    airport_de = destination.get(segmento['arrival']['iataCode'], 'Desconocido')
                    segmentId = segmento['id']
                    # Ejemplo: segmento['departure']['at'] = "2025-11-04T13:45:00"
                    fecha_str = segmento['departure']['at']
                    fecha = datetime.fromisoformat(fecha_str)
                    fecha_dp = fecha.strftime("%d/%m/%Y %H:%M")
 
                    fecha_str = segmento['arrival']['at']
                    fecha = datetime.fromisoformat(fecha_str)
                    fecha_ar = fecha.strftime("%d/%m/%Y %H:%M")
 
                    html += f"""<div class='card'>
                        <p><strong>Vuelo:</strong> {segmento['carrierCode']}{segmento['number']} $airline</p>
                        <p><strong>Salida:</strong> {segmento['departure']['iataCode']} {airport_or} a las {fecha_dp}</p>
                        <p><strong>Llegada:</strong> {segmento['arrival']['iataCode']} {airport_de} a las {fecha_ar}</p>
                        <p><strong>Duraci贸n:</strong> {format_duration(segmento['duration'])}</p>
                        <p><strong>Aeronave:</strong> {aircraft.get(segmento['aircraft']['code'] , segmento['aircraft']['code'])}</p>
                        <p><strong>Asientos Reservables:</strong> {numberOfBookableSeats}</p>
                        <p><strong>Paradas:</strong> {segmento['numberOfStops']}</p>"""
                            
                    if segmento['numberOfStops']!=0:
                        html += "<div>"
                        for item in segmento['stops']:
                            airport_stp = origin.get(item['iataCode'], 'Desconocido')
                            arrival = datetime.fromisoformat(item["arrivalAt"])
                            departure = datetime.fromisoformat(item["departureAt"])
                            html += f"""  
                                    <p><strong>Escalas:</strong></p>
                                    <p><strong>Aeropuerto:</strong> {item['iataCode']} $airport_stp </p>
                                    <p><strong>Duracion:</strong>{format_duration(item['duration'])}</p>
                                    <p><strong>Llegada:</strong>{arrival.strftime('%d/%m/%Y %H:%M')}</p>
                                    <p><strong>Salida:</strong>{departure.strftime('%d/%m/%Y %H:%M')}</p>"""
                            
                        html += "</div>"
                    
                
                    #Mostrar precios y servicios por pasajero para este segmento
                    for indexp, traveler in enumerate(travelerPricings):
                        pax = indexp + 1
                        html += f"""<div class='card'>
                            <h4>Pasajero $pax ({traveler['travelerType']})</h4>
                            <p><strong>Tarifa base:</strong> {traveler['price']['base']} {traveler['price']['currency']}</p>
                            <p><strong>Total:</strong> {traveler['price']['total']} {traveler['price']['currency']}</p>"""
                
                        #Buscar el segmento correspondiente al pasajero
                        for fareSegment in traveler['fareDetailsBySegment']:
                            if fareSegment['segmentId'] == segmentId: 
                                includedCheckedBags = fareSegment.get('includedCheckedBags', {}).get('quantity', 0)
                                includedCabinBags = fareSegment.get('includedCabinBags', {}).get('quantity' , 0)
                                html += f"""<hr>
                                    <p><strong>Segmento ID:</strong> $segmentId</p>
                                    <p><strong>Cabina:</strong> {fareSegment['cabin']} | <strong>Clase:</strong> {fareSegment['class']}</p>
                                    <p><strong>Maletas facturadas incluidas:</strong> {includedCheckedBags}</p>
                                    <p><strong>Equipaje de mano incluido:</strong> {includedCabinBags}</p>"""
                
                                if fareSegment.get('amenities'):
                                    html += "<p><strong>Servicios incluidos:</strong></p>"
                                    html += "<ul>"
                                    for  amenity in fareSegment['amenities']:
                                        if amenity['isChargeable']:
                                             isChargeable = '(Con cargo)'
                                        else:
                                            isChargeable = '(Incluido)'
                                        html += f"<li>{amenity['description']} {isChargeable}</li>"
                                    
                                        html += "</ul>"
                                else:
                                    html += "<p>No hay servicios listados para este segmento.</p>"
                    html += "</div>" # cierre card pasajero
                html += "</div>" # cierre card segmento
            html+="</div>"
        html+="</div>"
        html+="<hr size='2px' color='black' />"      

    return JSONResponse(content={'error':error,'cuerpo': html})


#Busca aeropuertos de origen
@router.post("/origin")
async def getorigin(origin_id: str = Form(...)):
    getQuery=f"country={origin_id}"
    response = await api.get_data("airports",query=getQuery, schema="global")
    airport=response['data'] if response["status"] == "success" else []
    print("origin ",airport)
    return JSONResponse(content={"data": airport})

#Busca aeropuertos de destinos
@router.post("/destination")
async def getdestination(destination_id: str = Form(...),):
    getQuery=f"country={destination_id}"
    response = await api.get_data("airports",query=getQuery, schema="global")
    airport=response['data'] if response["status"] == "success" else []
    return JSONResponse(
        content={
            "data": airport
        })

def format_duration(duration: str) -> str:
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', duration)
    if not match:
        return ""

    hours = f"{match.group(1)}h" if match.group(1) else ""
    minutes = f"{match.group(2)}m" if match.group(2) else ""
    return f"{hours} {minutes}".strip()