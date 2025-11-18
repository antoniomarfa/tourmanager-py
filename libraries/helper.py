from datetime import datetime
import locale, hmac, hashlib, urllib.parse,os 
from fastapi import Request

HASH_KEY = os.getenv("HASH_KEY", "tu_clave_secreta").encode("utf-8")

class Helper:

    @staticmethod
    def formatear(fecha_iso: str) -> str:
        try:
            dt = datetime.strptime(fecha_iso, "%Y-%m-%dT%H:%M:%SZ")
            return dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            return ""  # Retorna vacío si el


    @staticmethod
    def formatear_modificador(fecha_str: str) -> str:
        # Tu fecha original
        #fecha_str = "2025-08-22 19:24:33.779"
        # Convertir a datetime (ignora los microsegundos con %f)
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S.%fZ")

        # Formatear a d/m/Y
        fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
        return fecha_formateada

    @staticmethod
    def format_date_action(fecha_str: str) -> str:
        """
        Convierte una fecha a formato 'YYYY-MM-DD'.
        Acepta tanto 'YYYY-MM-DD' (formato ISO) como 'DD-MM-YYYY'.
        """
        if not fecha_str:
            return None

        for formato in ("%Y-%m-%d", "%d-%m-%Y"):
            try:
                fecha_obj = datetime.strptime(fecha_str, formato)
                return fecha_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue

        # Si no coincide con ningún formato, lanza un error claro
        raise ValueError(f"Formato de fecha no reconocido: {fecha_str}")

    @staticmethod
    def formatear1(fecha_iso: str) -> str:
        try:
            # El formato incluye milisegundos (%f)
            dt = datetime.strptime(fecha_iso, "%Y-%m-%d %H:%M:%S.%f")
            return dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            return ""

    @staticmethod      
    def in_array_r(needle, haystack, strict=False):
        """
        Busca un valor en un array anidado (recursivamente).
        """
        for item in haystack:
            if isinstance(item, dict):
                # Si es diccionario, revisamos sus valores
                if isinstance(needle, item.values(), strict):
                    return True
            elif isinstance(item, list):
                if isinstance(needle, item, strict):
                    return True
            else:
                if (strict and item is needle) or (not strict and item == needle):
                    return True
        return False

    @staticmethod
    def check_permission(array_roles_permissions, permission, action):
        """
        Verifica si existe un permiso y acción en un diccionario de permisos.
        """
        if Helper.in_array_r(permission, array_roles_permissions):
            if permission in array_roles_permissions:
                if action in array_roles_permissions[permission]['actions']:
                    return True
        return False

    @staticmethod
    def format_date_action(fecha_str):
        # Convertir string a objeto datetime
        fecha_obj = datetime.strptime(fecha_str, "%d-%m-%Y")

        # Formatear a yyyy/mm/dd
        fecha_nueva = fecha_obj.strftime("%Y-%m-%d")

        return fecha_nueva
    
    @staticmethod
    def formato_numero(valor):
        return f"{valor:,}".replace(",", ".")

    @staticmethod
    def nombre_mes(mes):
     # Si quieres el mes como nombre, tipo Helper::monthList en PHP
        month_list = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]       
        return  month_list[mes]
    

    @staticmethod
    def signature(parameters: dict) -> str:
        # Ordenar por clave como ksort()
        items = sorted((str(k), "" if v is None else str(v)) for k, v in parameters.items())

        # rawurlencode de nombre y valor, y concatenar con &
        pairs = [
            f"{urllib.parse.quote(k, safe='-_.~')}={urllib.parse.quote(v, safe='-_.~')}"
            for k, v in items
        ]
        concatenated = "&".join(pairs)

        # HMAC-SHA256 en binario (como hash_hmac(..., false))
        digest_bytes = hmac.new(HASH_KEY, concatenated.encode("utf-8"), hashlib.sha256).digest()

        # rawurlencode del binario → quote_from_bytes
        return urllib.parse.quote_from_bytes(digest_bytes)
    
    @staticmethod
    def convertir_fecha(fecha_str: str) -> str:
        """
        Convierte una fecha en formato d/m/Y a formato ISO 8601 (YYYY-MM-DDT00:00:00Z).
        """
        try:
            fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
            return fecha.strftime("%Y-%m-%dT00:00:00Z")
        except ValueError:
            return None  # Si la fecha no tiene el formato
        
    @staticmethod
    def flash_message(request: Request, tipo: str, mensaje: str):
        """
        Guarda un mensaje flash en sesión.
        tipo puede ser: 'success', 'error', 'warning', etc.
        """
        key = f"flash_{tipo}"
        request.session[key] = mensaje


    @staticmethod
    def get_flash(request: Request):
        """
        Obtiene y elimina los mensajes flash de la sesión.
        Retorna un diccionario con 'success', 'error', etc.
        """
        tipos = ["success", "error", "warning", "info"]
        mensajes = {}
        for tipo in tipos:
            key = f"flash_{tipo}"
            if key in request.session:
                mensajes[tipo] = request.session.pop(key)
        return mensajes

    @staticmethod
    def number_format(valor, decimales=0, sep_miles=",", sep_decimal="."):
        valor = float(valor)
        entero, decimal = divmod(abs(valor), 1)
        entero = int(entero)
        decimal = round(decimal * (10 ** decimales))
        entero_formateado = f"{entero:,}".replace(",", sep_miles)
        decimal_formateado = f"{decimal:0{decimales}d}"
        
        if decimales > 0:
            return f"{entero_formateado}{sep_decimal}{decimal_formateado}"
        return entero_formateado