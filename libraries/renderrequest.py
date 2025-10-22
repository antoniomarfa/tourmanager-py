import httpx

#RENDER_ENDPOINT = "https://tourmanager-3jic.onrender.com/api/v3.5"  # reemplaza con tu URL real
RENDER_ENDPOINT = "https://stingray-app-trnzb.ondigitalocean.app/api/v3.5"
class RenderRequest:
   # 
   # def __init__(self, schema=""):
   #     self.headers = {
   #         "Accept": "application/json",
   #         "X-Tenant-Schema": schema
   #     }

    async def get_data(self, service, query="", id="",schema=""):
        # Modificamos headers dinámicamente según "schema"  
        headers = {
            "Accept": "application/json",
            "X-Tenant-Schema": schema
        }

        url = f"{RENDER_ENDPOINT}/{service}"
        if id:
            url += f"/{id}"
        if query:
            url += f"?{query}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                result = response.json()
                if not result.get("success"):
                    return {"status": "error", "data": [], "message": result.get("error", "Error desconocido")}
                return {"status": "success", "data": result["data"], "message": ""}
            except Exception as e:
                return {"status": "error", "data": [], "message": str(e)}

    async def set_data(self, service, body="", query="", id="",schema=""):
        # Modificamos headers dinámicamente según "schema"
        headers = {
            "Accept": "application/json",
            "X-Tenant-Schema": schema
            }


        url = f"{RENDER_ENDPOINT}/{service}"
        if id:
            url += f"/{id}"
        if query:
            url += f"?{query}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, data=body, headers=headers)
                result = response.json()
                if result.get("error"):
                    return {"status": "error", "data": [], "message": result["error"]}
                return {"status": "success", "data": result, "message": ""}
            except Exception as e:
                return {"status": "error", "data": [], "message": str(e)}

    async def update_data(self, service, body="", query="", id="", schema=""):
        # Modificamos headers dinámicamente según "schema"
        headers = {
            "Accept": "application/json",
            "X-Tenant-Schema": schema
        }

        url = f"{RENDER_ENDPOINT}/{service}"
        if id:
            url += f"/{id}"
        if query:
            url += f"?{query}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.patch(url, data=body, headers=headers)
                result = response.json()
                return {"status": "success", "data": result, "message": ""}
            except Exception as e:
                return {"status": "error", "data": [], "message": str(e)}

    async def delete_data(self, service, query="", id="", schema=""):
        # Modificamos headers dinámicamente según "schema"
        headers = {
            "Accept": "application/json",
            "X-Tenant-Schema": schema
        }

        url = f"{RENDER_ENDPOINT}/{service}"
        if id:
            url += f"/{id}"
        if query:
            url += f"?{query}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(url, headers=headers)
                result = response.json()
                return {"status": "success", "data": result, "message": ""}
            except Exception as e:
                return {"status": "error", "data": [], "message": str(e)}
