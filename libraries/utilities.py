from libraries.renderrequest import RenderRequest
from docx import Document
import os,io,base64
from docx.shared import Inches
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from libraries.helper import Helper

api = RenderRequest()

class Utilities:

    @staticmethod
    def docx_to_html(plantilla_path, docx_path, valores):
        doc = Document(plantilla_path)

        def reemplazar_runs(parrafo, valores):
            for key, value in valores.items():
                placeholder = f"${{{key}}}"
                i = 0
                while i < len(parrafo.runs):
                    run = parrafo.runs[i]
                    if placeholder in run.text:
                        # Si es imagen (ej: firma en base64)
                        if key == "firma" and value:
                            run.text = run.text.replace(placeholder, "")  # limpiar placeholder
                            try:
                                image_data = base64.b64decode(value)
                                image_stream = io.BytesIO(image_data)
                                # Insertamos la imagen en el párrafo
                                run.add_picture(image_stream, width=Inches(1.5))  
                            except Exception as e:
                                print(f"Error insertando imagen: {e}")
                        else:
                            # Reemplazo de texto normal
                            run.text = run.text.replace(placeholder, str(value))
                    else:
                        # Revisar si la variable está partida en varios runs
                        combined_text = run.text
                        j = i + 1
                        while placeholder not in combined_text and j < len(parrafo.runs):
                            combined_text += parrafo.runs[j].text
                            j += 1
                        if placeholder in combined_text:
                            if key == "firma" and value:
                                for k in range(i, j):
                                    parrafo.runs[k].text = ""  # limpiar runs del placeholder
                                try:
                                    image_data = base64.b64decode(value)
                                    image_stream = io.BytesIO(image_data)
                                    parrafo.add_run().add_picture(image_stream, width=Inches(1.5))
                                except Exception as e:
                                    print(f"Error insertando imagen: {e}")
                            else:
                                new_text = combined_text.replace(placeholder, str(value))
                                index = 0
                                for k in range(i, j):
                                    run_len = len(parrafo.runs[k].text)
                                    parrafo.runs[k].text = new_text[index:index+run_len]
                                    index += run_len
                    i += 1

        # Reemplazo en párrafos
        for p in doc.paragraphs:
            reemplazar_runs(p, valores)

        # Reemplazo en tablas
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        reemplazar_runs(p, valores)

        doc.save(docx_path)

    @staticmethod
    def signature_doc(doc_path: str, signature_path: str, width_inches: float = 1.2):
        """
        Inserta la imagen signature_path en el lugar del marcador ${firma}
        dentro de doc_path (.docx). Reemplaza la primera ocurrencia encontrada
        en cada párrafo / celda. Preserva estilos en los runs.
        """
        if not os.path.isfile(doc_path):
            raise FileNotFoundError(f"Documento no encontrado: {doc_path}")
        if not os.path.isfile(signature_path):
            raise FileNotFoundError(f"Firma no encontrada: {signature_path}")

        doc = Document(doc_path)
        placeholder = "${firma}"
        width = Inches(width_inches)

        def insert_image_at_placeholder_in_paragraph(p):
            # obtener textos originales de los runs
            run_texts = [r.text for r in p.runs]
            if not run_texts:
                return False

            full_text = "".join(run_texts)
            if placeholder not in full_text:
                return False

            # posición de la primera ocurrencia
            start_index = full_text.find(placeholder)

            # nuevo texto sin el placeholder (solo la primera ocurrencia para mantener control)
            new_full_text = full_text.replace(placeholder, "", 1)

            # repartir new_full_text en los runs usando las longitudes originales
            idx = 0
            for i, orig in enumerate(run_texts):
                l = len(orig)
                # asignar parte correspondiente (si nos pasamos, asignar resto y luego '')
                segment = new_full_text[idx: idx + l] if idx < len(new_full_text) else ""
                p.runs[i].text = segment
                idx += l

            # si hay runs adicionales (poco probable), limpiarlos
            if len(p.runs) > len(run_texts):
                for r in p.runs[len(run_texts):]:
                    r.text = ""

            # calcular en qué run empieza el placeholder (usando longitudes originales)
            acc = 0
            run_start_idx = None
            for i, orig in enumerate(run_texts):
                if acc + len(orig) > start_index:
                    run_start_idx = i
                    break
                acc += len(orig)
            if run_start_idx is None:
                run_start_idx = max(0, len(p.runs) - 1)

            # crear un nuevo run con la imagen y moverlo antes del run detectado
            new_run = p.add_run()
            try:
                # add_picture sobre Run (o sobre el run nuevo)
                new_run.add_picture(signature_path, width=width)
            except Exception as e:
                # fallback: intentar con p.add_run().add_picture(...) (ambas deberían funcionar)
                try:
                    r2 = p.add_run()
                    r2.add_picture(signature_path, width=width)
                    new_run = r2
                except Exception as e2:
                    # si falla, re-lanzamos para debugging
                    raise

            # mover el run con la imagen al lugar correcto (antes del run_start)
            target_run = p.runs[run_start_idx]
            # insertar el nuevo run antes del target_run en el XML
            target_run._r.addprevious(new_run._r)

            return True

        # 1) reemplazar en párrafos del body
        for p in doc.paragraphs:
            insert_image_at_placeholder_in_paragraph(p)

        # 2) reemplazar en tablas (cada celda)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        insert_image_at_placeholder_in_paragraph(p)

        # 3) (opcional) podrías querer buscar también en headers/footers si tu plantilla lo usa

        # Guardar el documento (sobre-escribe el original)
        doc.save(doc_path)

    @staticmethod
    def docx_to_pdf_with_images(docx_path: str, pdf_path: str):
        """
        Convierte un docx a PDF preservando:
            - texto
            - saltos de línea
            - tablas
            - imágenes (incluida la firma insertada previamente)
        """
        if not os.path.isfile(docx_path):
            raise FileNotFoundError(f"Documento no encontrado: {docx_path}")

        doc = Document(docx_path)
        c = canvas.Canvas(pdf_path, pagesize=A4)
        page_width, page_height = A4
        x_margin = inch
        y_position = page_height - inch
        line_height = 14  # altura de línea aproximada

        def draw_paragraph(p):
            nonlocal y_position
            for r in p.runs:
                # dibujar texto si existe
                if r.text.strip():
                    for line in r.text.split('\n'):
                        c.drawString(x_margin, y_position, line)
                        y_position -= line_height
                        if y_position < inch:
                            c.showPage()
                            y_position = page_height - inch

                # dibujar imágenes asociadas al run
                for rel in r.part.rels.values():
                    if "image" in rel.reltype:
                        image_bytes = rel.target_part.blob
                        img_stream = BytesIO(image_bytes)
                        img_reader = ImageReader(img_stream)
                        img_width = 1.2 * inch
                        img_height = 1.2 * inch
                        # colocar la imagen en la misma línea aproximada
                        c.drawImage(img_reader, page_width - x_margin - img_width, y_position, width=img_width, height=img_height)
                        y_position -= img_height + 2
                        if y_position < inch:
                            c.showPage()
                            y_position = page_height - inch

            # agregar espacio entre párrafos
            y_position -= line_height
            if y_position < inch:
                c.showPage()
                y_position = page_height - inch

        def draw_table(table):
            nonlocal y_position
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        draw_paragraph(p)
                y_position -= line_height
                if y_position < inch:
                    c.showPage()
                    y_position = page_height - inch

        # dibujar todos los párrafos
        for p in doc.paragraphs:
            draw_paragraph(p)

        # dibujar todas las tablas
        for table in doc.tables:
            draw_table(table)

        c.save()
        print(f"PDF generado correctamente: {pdf_path}")

        
    @staticmethod    
    async def formCharge(session: dict):
        info_index=[]
        schema_name = session.get("schema")
        company_id=int(session.get('company'))

        response = await api.get_data("company",id=company_id,schema="global")
        company = response['data'] if response["status"] == "success" else [] 

        getQuery=f"id={session.get('sale')}"
        response = await api.get_data("sale/informe",query=getQuery,schema=schema_name)
        venta=response['data'][0] if response["status"] == "success" else [] 

        programid=int(venta['program_id'])
        response = await api.get_data("programac",id=programid,schema=schema_name)
        program=response['data'] if response["status"] == "success" else []
        
        colegioid=int(venta['establecimiento_id'])
        response = await api.get_data("colegio",id=colegioid,schema=schema_name)
        colegio=response['data'] if response["status"] == "success" else []

        info_index = {
            "curso": f"{colegio['nombre']}-{venta['curso']}-{venta['idcurso']}",
            "programa": program["name"],
            "fechaultimo": Helper.formatear(venta["fecha_ultpag"]),
            "fechasalida": Helper.formatear(venta["fechasalida"]),
            "company": company["nomfantasia"],
        }

        return info_index     
    

    @staticmethod    
    async def formPaymentCharge(session: dict):
        info_index=[]
        schema_name = session.get("schema")
        company_id=int(session.get('company'))

        response = await api.get_data("company",id=company_id,schema="global")
        company = response['data'] if response["status"] == "success" else [] 

        response = await api.get_data("sale",id=int(session.get('sale')),schema=schema_name)
        venta = response['data'] if response["status"] == "success" else []

        consulta = f"sale_id={session.get('sale')}&rutapod={session.get('user_rut')}"
        response = await api.get_data("curso",query=consulta,schema=schema_name)
        cursos = response['data'][0] if response["status"] == "success" else []
    
        colegioid=int(venta['establecimiento_id'])
        response = await api.get_data("colegio",id=colegioid,schema=schema_name)
        colegio=response['data'] if response["status"] == "success" else []
        
        program_id= int(venta["program_id"])
        response = await api.get_data("programac",id=program_id,schema=schema_name)
        program = response['data'] if response["status"] == "success" else []


        info_index = {
            "colegio": colegio["nombre"],
            "nomcurso": f'{venta["curso"]}-{venta["idcurso"]}',
            "programa": program["name"],
            "curso": cursos,
            "apoderado": cursos['nombreapod'],
            "alumno": cursos['nombrealumno'],
            "rutalumno": cursos["rutalumno"], 
            "pasaporte": cursos["pasaporte"],
            "fechanac": Helper.formatear(cursos['fechanac']),
            "regionid": cursos["region_id"],
            "comunaid": cursos["comuna_id"],
            "dircalle": cursos['dircalle'],
            "dirnumero": cursos['dirnumero'],
            "nrodepto": cursos['nrodepto'],
            "fono": cursos['fono'],
            "celular": cursos['celular'],
            "correo": cursos['correo'],
            "cuotas": venta["cuotas"],
            "fechaultimo": Helper.formatear(venta['fecha_ultpag']),
            "fechasalida": Helper.formatear(venta['fechasalida'])
        }

        return info_index 