from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from supabase import create_client

# Configuración de la interfaz web
st.set_page_config(
    page_title="Control de Capacitaciones y Exámenes - Sonda",
    layout="wide",
    page_icon="📋",
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            min-width: 300px;
            max-width: 350px;
        }
        .stRadio label {
            font-size: 15px !important;
            padding: 8px 0px !important;
            font-weight: 500;
        }
        .worker-card {
            background-color: #f8f9fa;
            border-left: 5px solid #0066cc;
            padding: 12px 15px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 10px;
        }
        .worker-label {
            font-size: 11px;
            color: #6c757d;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .worker-value {
            font-size: 15px;
            color: #212529;
            font-weight: 700;
            word-break: break-word;
            margin-top: 2px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# CREDENCIALES DE SUPABASE
SUPABASE_URL = "https://axdtqchtrugogmnczpzl.supabase.co"
SUPABASE_KEY = "sb_publishable_KH18NOkoKxuXaa7_xdcsdg_x9d334hh"


@st.cache_resource
def init_supabase():
  return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_supabase()

st.title("🛡️ Sistema de Gestión de Exámenes y Cursos - Sonda")

# Menú lateral
menu = st.sidebar.radio(
    "Navegación",
    [
        "📊 Ficha de Trabajador y Documentos",
        "➕ Registrar Examen / Curso (+ Respaldo PDF)",
        "⚠️ Control de Vencimientos (Alerta 1 Mes)",
    ],
)

# -------------------------------------------------------------------
# OPCIÓN 1: FICHA DE TRABAJADOR Y SUS DOCUMENTOS
# -------------------------------------------------------------------
if menu == "📊 Ficha de Trabajador y Documentos":
  st.subheader("🔍 Búsqueda de Trabajador")

  res = (
      supabase.table("trabajadores")
      .select("*")
      .order("nombre_completo")
      .execute()
  )
  df_trabajadores = pd.DataFrame(res.data)

  if not df_trabajadores.empty:
    opcion_trabajador = st.selectbox(
        "Seleccione un Trabajador para revisar:",
        df_trabajadores["rut"] + " - " + df_trabajadores["nombre_completo"],
    )
    rut_sel = opcion_trabajador.split(" - ")[0]

    trab = df_trabajadores[df_trabajadores["rut"] == rut_sel].iloc[0]

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
      st.markdown(
          f"""
            <div class="worker-card">
                <div class="worker-label">Nombre Completo</div>
                <div class="worker-value">{trab['nombre_completo']}</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    with col2:
      st.markdown(
          f"""
            <div class="worker-card">
                <div class="worker-label">RUT</div>
                <div class="worker-value">{trab['rut']}</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    with col3:
      st.markdown(
          f"""
            <div class="worker-card">
                <div class="worker-label">Cargo</div>
                <div class="worker-value">{str(trab['cargo'])}</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    with col4:
      st.markdown(
          f"""
            <div class="worker-card">
                <div class="worker-label">División</div>
                <div class="worker-value">{str(trab['division'])}</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    st.markdown("---")
    st.subheader("📁 Historial de Exámenes, Inducciones y Capacitaciones")

    res_reg = (
        supabase.table("registros_capacitaciones")
        .select("*")
        .eq("rut_trabajador", rut_sel)
        .execute()
    )
    df_reg = pd.DataFrame(res_reg.data)

    if not df_reg.empty:
      hoy = datetime.now().date()
      for idx, item in df_reg.iterrows():
        f_venc = datetime.strptime(
            item["fecha_vencimiento"].split("T")[0], "%Y-%m-%d"
        ).date()

        # Lógica de cálculo de estado
        if f_venc < hoy:
          color_estado, estado_txt = "🔴", "Vencido"
        elif f_venc <= hoy + timedelta(days=30):
          color_estado, estado_txt = (
              "🟡",
              "Por Vencer (< 1 mes)",
          )
        else:
          color_estado, estado_txt = "🟢", "Vigente"

        with st.expander(
            f"{color_estado} {item['categoria']}: {item['nombre_curso_examen']}"
            f" (Estado: {estado_txt})"
        ):
          st.write(f"**Fecha Realización:** {item['fecha_realizacion']}")
          st.write(f"**Fecha Vencimiento:** {item['fecha_vencimiento']}")
          st.write(f"**Observaciones:** {item['observaciones']}")

          if item["url_respaldo"]:
            st.markdown(
                f"📄 [**Ver/Descargar PDF o Documento de"
                f" Respaldo**]({item['url_respaldo']})"
            )
          else:
            st.info("No hay archivo cargado como respaldo para este registro.")
    else:
      st.info(
          "El trabajador no registra cursos o exámenes ingresados en la"
          " plataforma."
      )

# -------------------------------------------------------------------
# OPCIÓN 2: REGISTRAR EXAMEN/CURSO Y SUBIR PDF
# -------------------------------------------------------------------
elif menu == "➕ Registrar Examen / Curso (+ Respaldo PDF)":
  st.subheader("📝 Nuevo Registro de Capacitación o Examen")

  res = (
      supabase.table("trabajadores")
      .select("rut, nombre_completo")
      .order("nombre_completo")
      .execute()
  )
  lista_trabajadores = [
      f"{t['rut']} - {t['nombre_completo']}" for t in res.data
  ]

  with st.form("form_registro", clear_on_submit=True):
    trabajador_sel = st.selectbox("Seleccione Trabajador", lista_trabajadores)
    categoria = st.selectbox(
        "Categoría del Registro",
        [
            "EXAMEN OCUPACIONAL / PREOCUPACIONAL",
            "CURSO OTEC - EXTERNO",
            "CURSO IST",
            "INDUCCIÓN GENERAL / MINERA",
            "INDUCCIÓN ESPECÍFICA / CONDUCCIÓN",
            "LICENCIA INTERNA / MUNICIPAL",
            "CREDENCIAL",
        ],
    )
    nombre_curso = st.text_input(
        "Nombre específico (Ej: Examen Altura Física, Mando Medio, LOTO, etc.)"
    )

    col_f1, col_f2 = st.columns(2)
    f_realizacion = col_f1.date_input("Fecha de Realización", datetime.now())
    f_vencimiento = col_f2.date_input("Fecha de Vencimiento", datetime.now())

    observaciones = st.text_area("Observaciones o Comentarios adicionales")

    archivo_adjunto = st.file_uploader(
        "Adjuntar Respaldo en PDF o Imagen", type=["pdf", "png", "jpg", "jpeg"]
    )

    submitted = st.form_submit_button("💾 Guardar Registro en la Nube")

    if submitted:
      if not nombre_curso:
        st.error(
            "Por favor ingrese el nombre del examen, curso o inducción."
        )
      else:
        rut = trabajador_sel.split(" - ")[0]
        url_pdf = None

        if archivo_adjunto is not None:
          nombre_archivo = f"{rut}_{int(datetime.now().timestamp())}_{archivo_adjunto.name}"
          bytes_data = archivo_adjunto.getvalue()

          try:
            supabase.storage.from_("respaldos-documentos").upload(
                file=bytes_data,
                path=nombre_archivo,
                file_options={"content-type": archivo_adjunto.type},
            )

            url_pdf = supabase.storage.from_(
                "respaldos-documentos"
            ).get_public_url(nombre_archivo)
          except Exception as e:
            st.error(f"Error subiendo el archivo: {e}")

        # Cálculo automático de estado considerando la ventana de 30 días
        hoy = datetime.now().date()
        if f_vencimiento < hoy:
          estado = "Vencido"
        elif f_vencimiento <= hoy + timedelta(days=30):
          estado = "Por Vencer (< 1 mes)"
        else:
          estado = "Vigente"

        registro_data = {
            "rut_trabajador": rut,
            "categoria": categoria,
            "nombre_curso_examen": nombre_curso,
            "fecha_realizacion": str(f_realizacion),
            "fecha_vencimiento": str(f_vencimiento),
            "estado": estado,
            "url_respaldo": url_pdf,
            "observaciones": observaciones,
        }

        supabase.table("registros_capacitaciones").insert(
            registro_data
        ).execute()
        st.success(
            "✅ ¡Registro guardado exitosamente en la base de datos!"
        )

# -------------------------------------------------------------------
# OPCIÓN 3: PANEL DE CONTROL DE VENCIMIENTOS (ALERTA 1 MES)
# -------------------------------------------------------------------
elif menu == "⚠️ Control de Vencimientos (Alerta 1 Mes)":
  st.subheader(
      "⚠️ Matriz de Vencimientos (Alertas de Cursos y Exámenes a 30 días)"
  )

  res = (
      supabase.table("registros_capacitaciones")
      .select("*, trabajadores(nombre_completo, cargo, division)")
      .execute()
  )
  data = res.data

  if data:
    hoy = datetime.now().date()
    filas = []
    for d in data:
      trab_info = d.get("trabajadores", {}) or {}
      f_venc_str = d["fecha_vencimiento"].split("T")[0]
      f_venc = datetime.strptime(f_venc_str, "%Y-%m-%d").date()

      # Calcular estado dinámico actualizado
      if f_venc < hoy:
        est = "Vencido"
      elif f_venc <= hoy + timedelta(days=30):
        est = "Por Vencer (< 1 mes)"
      else:
        est = "Vigente"

      filas.append({
          "RUT": d["rut_trabajador"],
          "Trabajador": trab_info.get("nombre_completo", "N/A"),
          "Categoría": d["categoria"],
          "Curso/Examen": d["nombre_curso_examen"],
          "F. Realización": d["fecha_realizacion"],
          "F. Vencimiento": f_venc_str,
          "Estado": est,
          "Documento": d["url_respaldo"],
      })

    df_venc = pd.DataFrame(filas)

    # Filtros rápidos por estado
    filtro_estado = st.multiselect(
        "Filtrar por Estado",
        ["Vigente", "Por Vencer (< 1 mes)", "Vencido"],
        default=["Por Vencer (< 1 mes)", "Vencido"],
    )
    df_filtrado = df_venc[df_venc["Estado"].isin(filtro_estado)]

    st.dataframe(df_filtrado, use_container_width=True)
  else:
    st.info("Aún no hay registros de capacitaciones cargados en el sistema.")