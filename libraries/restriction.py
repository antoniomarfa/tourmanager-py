from libraries.renderrequest import RenderRequest

api = RenderRequest()

class Restriction:

    async def access_Menu(self,position,schema):
        getQuery=f"description={position}"
        response = await api.get_data("roles",query=getQuery,schema=schema)
        rol = response["data"] if response["status"] == "success" else []
        
        if not rol:
            return []

        # traer todos los permisos de ese rol
        getQuery = f"roles_id={rol[0]['id']}"
        response = await api.get_data("permission", query=getQuery, schema=schema)

        if response["status"] == "success":
            return response["data"]  # lista de permisos
        return []
    
    async def access_permission(sel,module,action,session):
        user_id=int(session.get('id'))
        response = await api.get_data("users",id=user_id,schema=session.get('schema'))
        #Busca el Usuario para obtener el Roles_id
        user = response['data'] if response['status'] == 'success' else []

        if not user:
            return False
      
        roles_id=int(user['roles_id'])
        getquery = f"roles_id={roles_id}&permission={module}"
        response = await api.get_data("permission",query=getquery,schema=session.get('schema'))
        permissions = response['data'] if response['status'] == 'success' else []
        
        for p in permissions:
                if action in p["actions"].split("|"):
                    return True
        return False