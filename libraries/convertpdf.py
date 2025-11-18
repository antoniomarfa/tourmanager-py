import requests
import os


class Convertpdf:

    #Obtener token
    def get_aspose_token(self, client_id, client_secret):
        url = "https://api.aspose.cloud/connect/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.post(url, data=data, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Error obteniendo token: {response.text}")

        json_data = response.json()

        if "access_token" not in json_data:
            raise Exception(f"Token inválido. Respuesta: {response.text}")

        return json_data["access_token"]

    #Subir archivo DOCX a Aspose
    def upload_to_aspose(self, token, local_path, remote_name):
        if not os.path.exists(local_path):
            raise Exception(f"Archivo no encontrado: {local_path}")

        url = f"https://api.aspose.cloud/v4.0/words/storage/file/{remote_name}"

        headers = {
            "Authorization": f"Bearer {token}"
        }

        with open(local_path, "rb") as f:
            response = requests.put(url, data=f, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Fallo al subir DOCX. Código: {response.status_code}. Respuesta: {response.text}")

    #Convertir DOCX a PDF
    def convert_docx_to_pdf(self, token, remote_docx_name, output_file_name, local_pdf_output):
        url = f"https://api.aspose.cloud/v4.0/words/{remote_docx_name}/saveAs"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        body = {
            "SaveFormat": "pdf",
            "FileName": output_file_name
        }

        response = requests.put(url, json=body, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Fallo en conversión. Código: {response.status_code}. Respuesta: {response.text}")

        #Descargar PDF
        download_url = f"https://api.aspose.cloud/v4.0/words/storage/file/{output_file_name}"

        download_resp = requests.get(download_url, headers={"Authorization": f"Bearer {token}"})

        if download_resp.status_code != 200:
            raise Exception(f"No se pudo descargar el PDF. Código: {download_resp.status_code}")

        # Guardar archivo PDF en local
        with open(local_pdf_output, "wb") as f:
            f.write(download_resp.content)
