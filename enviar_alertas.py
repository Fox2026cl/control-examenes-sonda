import email.mime.multipart
import email.mime.text
import os
import smtplib
import sys
from datetime import datetime, timedelta
from supabase import create_client

# Cargar credenciales desde las variables de entorno de GitHub
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# Verificar que existan las credenciales
faltantes = []
if not SUPABASE_URL:
  faltantes.append("SUPABASE_URL")
if not SUPABASE_KEY:
  faltantes.append("SUPABASE_KEY")
if not EMAIL_SENDER:
  faltantes.append("EMAIL_SENDER")
if not EMAIL_PASSWORD:
  faltantes.append("EMAIL_PASSWORD")

if faltantes:
  print(
      f"❌ ERROR CRÍTICO: Faltan las siguientes variables en GitHub Secrets:"
      f" {', '.join(faltantes)}"
  )
  sys.exit(1)

# Destinatarios del reporte
DESTINATARIOS = ["miguel.alquinta@gmail.com"]


def generar_reporte_y_enviar():
  print("🔄 Conectando a Supabase...")
  try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    res = (
        supabase.table("registros_capacitaciones")
        .select("*, trabajadores(nombre_completo, cargo, division)")
        .execute()
    )
    data = res.data
  except Exception as e:
    print(f"❌ Error al consultar Supabase: {e}")
    sys.exit(1)

  if not data:
    print("ℹ️ No hay registros en la base de datos.")
    return

  hoy = datetime.now().date()
  vencidos = []
  por_vencer = []

  for d in data:
    trab_info = d.get("trabajadores", {}) or {}
    f_venc_str = d["fecha_vencimiento"].split("T")[0]
    f_venc = datetime.strptime(f_venc_str, "%Y-%m-%d").date()

    item = {
        "rut": d["rut_trabajador"],
        "nombre": trab_info.get("nombre_completo", "N/A"),
        "cargo": trab_info.get("cargo", "N/A"),
        "categoria": d["categoria"],
        "curso": d["nombre_curso_examen"],
        "vencimiento": f_venc_str,
    }

    if f_venc < hoy:
      vencidos.append(item)
    elif f_venc <= hoy + timedelta(days=30):
      por_vencer.append(item)

  print(
      f"📊 Registros encontrados -> Vencidos: {len(vencidos)} | Por Vencer:"
      f" {len(por_vencer)}"
  )

  if not vencidos and not por_vencer:
    print(
        "🎉 No hay exámenes vencidos ni por vencer en el periodo de 30 días."
    )
    return

  def armar_tabla_html(lista, color_header):
    if not lista:
      return (
          "<p style='color: #28a745;'><i>Sin registros en esta"
          " categoría.</i></p>"
      )

    html = f"""
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; font-size: 13px;">
            <tr style="background-color: {color_header}; color: white;">
                <th>RUT</th>
                <th>Trabajador</th>
                <th>Cargo</th>
                <th>Curso / Examen</th>
                <th>Fecha Vencimiento</th>
            </tr>
        """
    for x in lista:
      html += f"""
            <tr>
                <td>{x['rut']}</td>
                <td><b>{x['nombre']}</b></td>
                <td>{x['cargo']}</td>
                <td>{x['curso']} ({x['categoria']})</td>
                <td><b>{x['vencimiento']}</b></td>
            </tr>
            """
    html += "</table>"
    return html

  html_vencidos = armar_tabla_html(vencidos, "#dc3545")
  html_por_vencer = armar_tabla_html(por_vencer, "#ffc107")

  msg = email.mime.multipart.MIMEMultipart("alternative")
  msg["Subject"] = (
      f"🚨 REPORTE SEMANAL: Alerta de Exámenes y Cursos ({hoy.strftime('%d/%m/%Y')})"
  )
  msg["From"] = EMAIL_SENDER
  msg["To"] = ", ".join(DESTINATARIOS)

  cuerpo_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.5;">
        <h2 style="color: #0066cc;">🛡️ Sistema de Control de Capacitaciones - Sonda</h2>
        <p>Estimado Equipo,</p>
        <p>A continuación se detalla el consolidado automático de documentación crítica:</p>
        
        <h3 style="color: #dc3545;">🔴 EXÁMENES / CURSOS VENCIDOS ({len(vencidos)})</h3>
        {html_vencidos}
        <br>
        <h3 style="color: #d39e00;">🟡 EXÁMENES / CURSOS POR VENCER EN 30 DÍAS ({len(por_vencer)})</h3>
        {html_por_vencer}
        
        <br><hr>
        <p style="font-size: 11px; color: #777;">Reporte generado automáticamente por la plataforma web Sonda.</p>
      </body>
    </html>
    """

  msg.attach(email.mime.text.MIMEText(cuerpo_html, "html"))

  print("📧 Conectando al servidor SMTP seguro (Puerto 465)...")
  try:
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.sendmail(EMAIL_SENDER, DESTINATARIOS, msg.as_string())
    server.quit()
    print("✅ ¡Correo de alerta semanal enviado con éxito!")
  except Exception as e:
    print(f"❌ Error al enviar el correo: {e}")
    sys.exit(1)


if __name__ == "__main__":
  generar_reporte_y_enviar()
