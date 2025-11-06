from libraries.renderrequest import RenderRequest
import smtplib,os
from datetime import datetime
from email.message import EmailMessage


api = RenderRequest()

HASH_KEY = os.getenv("HASH_KEY", "tu_clave_secreta").encode("utf-8")
BASE_URL =os.getenv("BASE_URL")
MAIL_COLOR_TEXT= os.getenv("MAIL_COLOR_TEXT","#2e58a6")
MAIL_COLOR_BACKGROUND= os.getenv("MAIL_COLOR_BACKGROUND","#f6f6f6")
MAIL_COLOR_FOOTER_TEXT= os.getenv("MAIL_COLOR_FOOTER_TEXT","#ffffff")

class Mailutil:


    @staticmethod
    async def email_usuarios(idUser, password, subject, title, message, session: dict):

        schema_name = session.get("schema")
        company_id=int(session.get('company'))

        respuesta = await api.get_data("users",id=idUser,schema=schema_name)
        user=respuesta['data'] if respuesta['status'] == 'success' else []

        respuesta = await api.get_data("company",id=company_id,schema="global")
        company=respuesta['data'] if respuesta['status'] == 'success' else []
        WebMailContacto = company['email']


        URL = f"{BASE_URL}/{company['identificador']}/manager"
        WebFecha = datetime.now().year
        WebTitulo = company['nomfantasia']


        #  $mail->AddEmbeddedImage(ROOT . 'public' . DS . 'themes' . DS . DEFAULT_LAYOUT . DS . 'images' . DS . 'login_logo_1.png', 'imgHeader', 'attachment', 'base64', 'image/jpeg');

        CSS_TABLE_MAIN = 'style="margin-left: auto; margin-right: auto; padding: 0; box-shadow: 0 0 10px rgba(0,0,0,.2); font-family: sans-serif; font-size: 14px; background: #FFF; border: 1px solid #ddd; width: 635px; color: #555555; line-height: 18px; border-spacing: 0; border-radius: 6px;"'
        CSS_H1_MAIN = f'style="margin: 10px 0; color: {MAIL_COLOR_TEXT}; font-size: 26px;"'
        CSS_H1_MAIN_STRONG = 'style="color:#555"'
        CSS_HR = 'style="display: block; border: none; border-top: 2px solid #f2f2f2;"'
        CSS_TABLE_SECONDARY = 'style="width: 100%; border: 1px solid #ddd; border-bottom: 0; border-spacing: 0; font-size: 12px; line-height: 16px;"'
        CSS_FOOTER = f'style="display: block; padding: 10px; margin: 0; background: {MAIL_COLOR_TEXT}; color: #FFF; text-align: center;font-size:12px;"'
        CSS_FOOTER_LINK = 'style="color: #FFF; text-decoration:none;"'
        CSS_TABLE_SECONDARY_BODY_TH = f'style="border-bottom: 1px solid #ddd; padding: 5px; background-color:{MAIL_COLOR_BACKGROUND}; text-align: left; border-right: 1px solid #ddd;"'
        CSS_TABLE_SECONDARY_BODY_TD = 'style="border-bottom: 1px solid #ddd; padding: 5px; background-color: #fff; text-align: left; border-right: 1px solid #ddd;"'

        From = WebMailContacto
        FromName = company['nomfantasia']
        asunto = subject
        AddAddress= user['email']
        body = f"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http: //www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http: //www.w3.org/1999/xhtml">
        
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <title>Email Administacion</title>
        </head>
        
        <body style="background: #f4f4f4; padding: 20px;">
            <table width="635" border="0" valign="top" {CSS_TABLE_MAIN}>
                <tbody>
                    <tr>
                    <td style="padding: 0; margin: 0; border: 0; width: 635px;">
                        <img src="cid:imgHeader" style="border-radius: 6px 6px 0 0; border-bottom:1px solid #f2f2f2">
                    </td>
                    </tr>
                    <tr>
                    <td style="display: block; padding: 5px 15px; text-align: center;">
                        <h1 {CSS_H1_MAIN}>{title} <strong {CSS_H1_MAIN_STRONG}>Usuario</strong></h1>
                    </td>
                    </tr>
        
                    <tr>
                    <td style="display: block; padding: 0 15px;"><hr {CSS_HR}></td>
                    </tr>
        
                    <tr>
                    <td style="display: block; padding: 5px 15px;">
                        <p style="font-size:12px;">Estimado Sr(a) {user['name']}, {message }</p>
                        <p style="font-size:12px;">Para iniciar sesión en nuestro panel de administración, introduce tu usuario y contraseña <a href="{URL}" target="_self">aquí</a>:</p>
                    </td>
                    </tr>
        
                    <tr>
                    <td style="display: block; padding: 5px 15px;">
                        <table width="100%" border="0" {CSS_TABLE_SECONDARY}>
                            <tbody>
                                <tr style="border-bottom: 1px solid #ddd; vertical-align: top;">
                                <th width="30%" {CSS_TABLE_SECONDARY_BODY_TH}>Usuario</th>
                                <td width="70%" {CSS_TABLE_SECONDARY_BODY_TD}>{user['username']}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #ddd; vertical-align: top;">
                                <th {CSS_TABLE_SECONDARY_BODY_TH}>Contraseña</th>
                                <td {CSS_TABLE_SECONDARY_BODY_TD}>{password}</td>
                                </tr>                                      
                            </tbody>
                        </table>
                    </td>
                    </tr>
        
                    <tr>
                    <td style="display: block; padding: 15px;"><hr {CSS_HR}></td>
                    </tr>
        
                    <tr><
                    <td style="display: block; padding: 10px; background: #f6f6f6; color:#999; margin-top: 20px; text-align: center; font-size:11px;">
                        Este correo se ha generado de forma automatica, favor no responder.
                    </td>
                    </tr>
        
                    <tr >
                    <td ' . $CSS_FOOTER . '>
                        <a href="{URL}" target="_self" {CSS_FOOTER_LINK}>{WebFecha} - {WebTitulo}</a>
                    </td>
                    </tr>
                </tbody>
            </table>
        
        </body>
        </html>"""

        # Crear el mensaje
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = From
        msg['To'] = AddAddress
        # Si quieres enviar HTML en lugar de texto plano
        msg.add_alternative(body, subtype='html')

        # Conexión al servidor SMTP de Gmail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('antoniomarfa@gmail.com', 'nrhd jfir affj tplr')
            smtp.send_message(msg)

        return