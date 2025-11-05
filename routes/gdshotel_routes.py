from fastapi import FastAPI, Request, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
from libraries.helper import Helper
import requests, json
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

    respuesta = await api.get_data("airports/informe",schema="global")
    country= respuesta['data'] if respuesta['status']=='success' else []

    consulta=f'state=V&company_id={company_id}'
    respuesta = await api.get_data("sale/informe",query=consulta,schema=schema_name)
    sale=respuesta['data'] if respuesta['status']=='success' else []

     # Fecha de hoy
    hoy = datetime.today()
    start_date = hoy.strftime("%Y-%m-%d")
    return templates.TemplateResponse("gdshotel/index.html", {"request": request,"countrys":country,"sale":sale,"start_date":start_date,"empresa":empresa})            


@router.post("/getOffers", response_class=HTMLResponse)
async def getOffers(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id = int(request.session.get("company"))

    error=0
    html=""
    form_data = await request.form()
    country_txt=form_data.get('origen_code') 
    adultos=form_data.get('adultos') 
    habitaciones=form_data.get('habitaciones') 
    start_date=form_data.get('start_date') 
    sale=form_data.get('sale')
    start_date=form_data.get('start_date')

    #buscar el country segun el city
    consulta=f'city={country_txt.strip()}'
    respuesta = await api.get_data("airports",query=consulta,schema="global")
    airport=respuesta['data'][0] if respuesta['status'] == 'success' else []

    country_code=airport["country"]
        
    client_id = 'dPNt0QeocGA7Rd9G2plAEoDDzCTkjpuw'
    client_secret = '9icdTUq8xg4bqnQg'

    #Autentication
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
    #    print("Access Token:", access_token)
    else:
        print("Error:", response.status_code, response.text)
        

    #Buscar el codigo iataCode de la ciudad
    url=f'https://test.api.amadeus.com/v1/reference-data/locations/cities?countryCode={country_code}&keyword={country_txt}'

    headers = {
         "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
    else:
        print("Error:", response.status_code, response.text)
        return JSONResponse(content={'error':1,'cuerpo': response.text})

 
    if data['meta']['count']>0:
        count = data['meta']['count']
        for item in  data["data"]:
            nameCity=item["name"]
            if nameCity.strip().upper() == country_txt.strip().upper():
                iataCode = item["iataCode"]        
                break
    
    if iataCode:
        #con el codigo iataCode obtener los hoteles en un rango de 10 KM 
        url=f'https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city?cityCode={iataCode}'
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
        else:
            data = json.loads(response.text)
            detail = data["errors"][0]["detail"]            
            #print("Error:", response.status_code, response.text)
            return JSONResponse(content={'error':1,'cuerpo': data})
        
        if data['meta']['count']>0:
            hotelId=[]
            for item in data["data"]:
                hotelId.append(item["hotelId"])
            
        
        for id in hotelId: 
    
            #segun los hoteles encontrados en el json anterior buscar disponibilidad en la fecha
            url=f'https://test.api.amadeus.com/v3/shopping/hotel-offers?hotelIds={id}&adults={adultos}&checkInDate={start_date}&roomQuantity={habitaciones}'
            print("url ",url)
            headers = {
                "Authorization": f"Bearer {access_token}"
            }

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
            else:
                print("Error disponibilidad :", response.status_code, response.text)
                return JSONResponse(content={'error':1,'cuerpo': response.text})


            if 'errors' not in data:
    
                #Extraemos la info para comodidad
                hotel = data['data'][0]['hotel']
                offer = data['data'][0]['offers'][0]
                available = 'Si' if data['data'][0]['available'] else 'No'

                roomDescription = offer['room']['description']['text']  
                tax = 0; 
                taxIncluded = 'incluido' if tax['included'] else 'no incluido'
                taxAmount = f"{tax['amount']}  {tax['currency']}"
                precioBase=""
                if offer['price']['base']:
                    precioBase=f"{offer['price']['currency']} {offer['price']['base']}"
                
                precioTotal=f"{offer['price']['currency']} {offer['price']['total']}"
            
                html+=f"""
                    <h2>Oferta de Hotel - {hotel['name']}</h2>
                      <table>
                        <tr><th colspan="2">Informacion del Hotel</th></tr>
                        <tr><th>Nombre</th><td>{hotel['name']}</td></tr>
                        <tr><th>Ciudad (IATA)</th><td>{hotel['cityCode']}</td></tr>
                        <tr><th>Coordenadas</th><td>{hotel['latitude']}, {hotel['longitude']}</td></tr>
                        <tr><th>Disponible</th><td>{available}</td></tr>
                      </table>
                        
                      <h3>Detalles de la Oferta</h3>
                        
                      <table>
                        <tr><th>Fechas</th><td>{offer['checkInDate']} - {offer['checkOutDate']}</td></tr>
                        <tr><th>Habitacion</th><td></td></tr>
                        <tr><th>Descripcion</th><td>{roomDescription}</td></tr>
                        <tr><th>Adultos</th><td>{offer['guests']['adults']}</td></tr>
                        <tr><th>Precio Base</th><td>{precioBase}</td></tr>
                        <tr><th>Precio Total</th><td>{precioTotal}</td></tr>
                        <tr><th>Impuestos</th><td>{taxAmount} ({taxIncluded})</td></tr>
                        <tr><th>Pago</th><td>{offer['policies']['paymentType']} - Tarjeta de credito</td></tr>
                        <tr><th>Politica de Cancelacion</th><td></td></tr>
                        </table>
                        <br><br><hr>"""
               
        
    
    return JSONResponse(content={'error':error,'cuerpo': html})