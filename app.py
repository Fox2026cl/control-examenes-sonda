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

# Menú lateral ampliado
menu = st.sidebar.radio(
    "Navegación",
    [
        "📊 Ficha de Trabajador y Documentos",
        "➕ Registrar Examen / Curso",
        "✏️ Actualizar / Renovar Exámenes",
        "👥 Gestionar Trabajadores",
        "⚠️ Panel de Alertas y Vencimientos",
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
# OPCIÓN 2: REGISTRAR EXAMEN / CURSO
# -------------------------------------------------------------------
elif menu == "➕ Registrar Examen / Curso":
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
# OPCIÓN 3: ACTUALIZAR / RENOVACIÓN DE EXÁMENES Y CURSOS
# -------------------------------------------------------------------
elif menu == "✏️ Actualizar / Renovar Exámenes":
  st.subheader(
      "✏️ Modificar o Renovar Fechas de Exámenes, Cursos e Inducciones"
  )

  res_t = (
      supabase.table("trabajadores")
      .select("rut, nombre_completo")
      .order("nombre_completo")
      .execute()
  )
  lista_t = [f"{t['rut']} - {t['nombre_completo']}" for t in res_t.data]

  if lista_t:
    t_sel = st.selectbox("Seleccione el Trabajador a Gestionar", lista_t)
    rut_sel = t_sel.split(" - ")[0]

    res_reg = (
        supabase.table("registros_capacitaciones")
        .select("*")
        .eq("rut_trabajador", rut_sel)
        .execute()
    )
    registros = res_reg.data

    if registros:
      reg_opciones = {
          f"{r['categoria']} - {r['nombre_curso_examen']} (Vence: {r['fecha_vencimiento']})": r[
              "id"
          ]
          for r in registros
      }
      reg_sel_label = st.selectbox(
          "Seleccione el Curso o Examen a Modificar", list(reg_opciones.keys())
      )
      reg_id = reg_opciones[reg_sel_label]

      # Buscar el registro actual
      actual = next(r for r in registros if r["id"] == reg_id)

      with st.form("form_actualizar"):
        st.write(
            f"**Editando:** {actual['nombre_curso_examen']} ({actual['categoria']})"
        )

        nueva_categoria = st.selectbox(
            "Categoría",
            [
                "EXAMEN OCUPACIONAL / PREOCUPACIONAL",
                "CURSO OTEC - EXTERNO",
                "CURSO IST",
                "INDUCCIÓN GENERAL / MINERA",
                "INDUCCIÓN ESPECÍFICA / CONDUCCIÓN",
                "LICENCIA INTERNA / MUNICIPAL",
                "CREDENCIAL",
            ],
            index=(
                [
                    "EXAMEN OCUPACIONAL / PREOCUPACIONAL",
                    "CURSO OTEC - EXTERNO",
                    "CURSO IST",
                    "INDUCCIÓN GENERAL / MINERA",
                    "INDUCCIÓN ESPECÍFICA / CONDUCCIÓN",
                    "LICENCIA INTERNA / MUNICIPAL",
                    "CREDENCIAL",
                ].index(actual["categoria"])
                if actual["categoria"]
                in [
                    "EXAMEN OCUPACIONAL / PREOCUPACIONAL",
                    "CURSO OTEC - EXTERNO",
                    "CURSO IST",
                    "INDUCCIÓN GENERAL / MINERA",
                    "INDUCCIÓN ESPECÍFICA / CONDUCCIÓN",
                    "LICENCIA INTERNA / MUNICIPAL",
                    "CREDENCIAL",
                ]
                else 0
            ),
        )

        nuevo_nombre = st.text_input(
            "Nombre del Curso / Examen", value=actual["nombre_curso_examen"]
        )

        f_real_actual = datetime.strptime(
            actual["fecha_realizacion"].split("T")[0], "%Y-%m-%d"
        ).date()
        f_venc_actual = datetime.strptime(
            actual["fecha_vencimiento"].split("T")[0], "%Y-%m-%d"
        ).date()

        col_a1, col_a2 = st.columns(2)
        nueva_realizacion = col_a1.date_input(
            "Nueva Fecha Realización", value=f_real_actual
        )
        nuevo_vencimiento = col_a2.date_input(
            "Nueva Fecha Vencimiento", value=f_venc_actual
        )

        nuevas_obs = st.text_area(
            "Observaciones",
            value=actual["observaciones"]
            if actual["observaciones"]
            else "",
        )

        nuevo_archivo = st.file_uploader(
            "Actualizar Respaldo PDF (Opcional)",
            type=["pdf", "png", "jpg", "jpeg"],
        )

        col_btn1, col_btn2 = st.columns(2)
        actualizar = col_btn1.form_submit_button("💾 Guardar Cambios")
        eliminar_reg = col_btn2.form_submit_button(
            "🗑️ Eliminar este Registro"
        )

        if actualizar:
          url_pdf = actual["url_respaldo"]
          if nuevo_archivo is not None:
            nombre_archivo = f"{rut_sel}_{int(datetime.now().timestamp())}_{nuevo_archivo.name}"
            bytes_data = nuevo_archivo.getvalue()
            supabase.storage.from_("respaldos-documentos").upload(
                file=bytes_data,
                path=nombre_archivo,
                file_options={"content-type": nuevo_archivo.type},
            )
            url_pdf = supabase.storage.from_(
                "respaldos-documentos"
            ).get_public_url(nombre_archivo)

          hoy = datetime.now().date()
          if nuevo_vencimiento < hoy:
            est = "Vencido"
          elif nuevo_vencimiento <= hoy + timedelta(days=30):
            est = "Por Vencer (< 1 mes)"
          else:
            est = "Vigente"

          supabase.table("registros_capacitaciones").update({
              "categoria": nueva_categoria,
              "nombre_curso_examen": nuevo_nombre,
              "fecha_realizacion": str(nueva_realizacion),
              "fecha_vencimiento": str(nuevo_vencimiento),
              "estado": est,
              "url_respaldo": url_pdf,
              "observaciones": nuevas_obs,
          }).eq("id", reg_id).execute()

          st.success("✅ ¡Registro actualizado correctamente!")
          st.rerun()

        if eliminar_reg:
          supabase.table("registros_capacitaciones").delete().eq(
              "id", reg_id
          ).execute()
          st.warning("🗑️ ¡Registro eliminado del sistema!")
          st.rerun()
    else:
      st.info("Este trabajador no tiene cursos ni exámenes registrados.")
  else:
    st.info("No hay trabajadores registrados en la base de datos.")

# -------------------------------------------------------------------
# OPCIÓN 4: GESTIONAR TRABAJADORES (AGREGAR, MODIFICAR, ELIMINAR)
# -------------------------------------------------------------------
elif menu == "👥 Gestionar Trabajadores":
  st.subheader("👥 Administración del Personal (Agregar, Editar y Eliminar)")

  accion_trab = st.radio(
      "Seleccione Acción",
      [
          "➕ Agregar Nuevo Trabajador",
          "✏️ Modificar o Eliminar Trabajador Existente",
      ],
      horizontal=True,
  )

  if accion_trab == "➕ Agregar Nuevo Trabajador":
    with st.form("form_nuevo_trabajador", clear_on_submit=True):
      st.write("### Ingresar Datos del Nuevo Trabajador")
      c_rut = st.text_input("RUT (Ej: 12345678-9)")
      c_nombres = st.text_input("Nombres")
      c_ap1 = st.text_input("Primer Apellido")
      c_ap2 = st.text_input("Segundo Apellido")

      col_t1, col_t2 = st.columns(2)
      c_div = col_t1.text_input(
          "División (Ej: División Chuquicamata (DCH))"
      )
      c_cargo = col_t2.text_input("Cargo")

      col_t3, col_t4 = st.columns(2)
      c_turno = col_t3.text_input("Turno (Ej: C, 4x4, etc.)")
      c_fono = col_t4.text_input("N° Celular")

      c_correo = st.text_input("Correo Electrónico")
      c_ingreso = st.date_input("Fecha de Ingreso", datetime.now())

      btn_guardar_trab = st.form_submit_button("💾 Guardar Trabajador")

      if btn_guardar_trab:
        if not c_rut or not c_nombres:
          st.error("El RUT y el Nombre son obligatorios.")
        else:
          nombre_completo_val = (
              f"{c_nombres} {c_ap1} {c_ap2}".strip().upper()
          )
          nuevo_t_data = {
              "rut": c_rut.strip(),
              "nombre": c_nombres.strip(),
              "apellido1": c_ap1.strip(),
              "apellido2": c_ap2.strip(),
              "nombre_completo": nombre_completo_val,
              "division": c_div.strip(),
              "cargo": c_cargo.strip(),
              "turno": c_turno.strip(),
              "correo_laboral": c_correo.strip(),
              "telefono": c_fono.strip(),
              "fecha_ingreso": str(c_ingreso),
          }

          supabase.table("trabajadores").upsert(nuevo_t_data).execute()
          st.success(
              f"✅ ¡Trabajador {nombre_completo_val} agregado correctamente!"
          )

  else:  # Modificar o Eliminar trabajador existente
    res_all = (
        supabase.table("trabajadores")
        .select("*")
        .order("nombre_completo")
        .execute()
    )
    df_all = pd.DataFrame(res_all.data)

    if not df_all.empty:
      sel_t_edit = st.selectbox(
          "Seleccione el Trabajador a Editar o Dar de Baja",
          df_all["rut"] + " - " + df_all["nombre_completo"],
      )
      rut_edit = sel_t_edit.split(" - ")[0]
      datos_act = df_all[df_all["rut"] == rut_edit].iloc[0]

      with st.form("form_editar_trabajador"):
        st.write(f"### Editando información de: {datos_act['nombre_completo']}")

        e_nombres = st.text_input(
            "Nombres",
            value=datos_act["nombre"] if datos_act["nombre"] else "",
        )
        e_ap1 = st.text_input(
            "Primer Apellido",
            value=datos_act["apellido1"] if datos_act["apellido1"] else "",
        )
        e_ap2 = st.text_input(
            "Segundo Apellido",
            value=datos_act["apellido2"] if datos_act["apellido2"] else "",
        )

        col_e1, col_e2 = st.columns(2)
        e_div = col_e1.text_input(
            "División",
            value=datos_act["division"] if datos_act["division"] else "",
        )
        e_cargo = col_e2.text_input(
            "Cargo", value=datos_act["cargo"] if datos_act["cargo"] else ""
        )

        col_e3, col_e4 = st.columns(2)
        e_turno = col_e3.text_input(
            "Turno", value=datos_act["turno"] if datos_act["turno"] else ""
        )
        e_fono = col_e4.text_input(
            "Teléfono",
            value=datos_act["telefono"] if datos_act["telefono"] else "",
        )

        e_correo = st.text_input(
            "Correo Laboral",
            value=datos_act["correo_laboral"]
            if datos_act["correo_laboral"]
            else "",
        )

        col_b1, col_b2 = st.columns(2)
        btn_act_t = col_b1.form_submit_button("💾 Actualizar Datos")
        btn_del_t = col_b2.form_submit_button(
            "🗑️ Eliminar Trabajador (y sus registros)"
        )

        if btn_act_t:
          nc_val = f"{e_nombres} {e_ap1} {e_ap2}".strip().upper()
          supabase.table("trabajadores").update({
              "nombre": e_nombres.strip(),
              "apellido1": e_ap1.strip(),
              "apellido2": e_ap2.strip(),
              "nombre_completo": nc_val,
              "division": e_div.strip(),
              "cargo": e_cargo.strip(),
              "turno": e_turno.strip(),
              "correo_laboral": e_correo.strip(),
              "telefono": e_fono.strip(),
          }).eq("rut", rut_edit).execute()
          st.success("✅ ¡Datos del trabajador actualizados con éxito!")
          st.rerun()

        if btn_del_t:
          supabase.table("trabajadores").delete().eq(
              "rut", rut_edit
          ).execute()
          st.warning(
              "🗑️ Trabajador y todos sus registros asociados eliminados."
          )
          st.rerun()
    else:
      st.info("No hay trabajadores en la base de datos.")

# -------------------------------------------------------------------
# OPCIÓN 5: PANEL DE ALERTAS Y VENCIMIENTOS
# -------------------------------------------------------------------
elif menu == "⚠️ Panel de Alertas y Vencimientos":
  st.subheader(
      "⚠️ Panel General de Alertas (Exámenes y Cursos Próximos a Vencer o"
      " Vencidos)"
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
    vencidos_count = 0
    por_vencer_count = 0

    for d in data:
      trab_info = d.get("trabajadores", {}) or {}
      f_venc_str = d["fecha_vencimiento"].split("T")[0]
      f_venc = datetime.strptime(f_venc_str, "%Y-%m-%d").date()

      if f_venc < hoy:
        est = "Vencido"
        vencidos_count += 1
      elif f_venc <= hoy + timedelta(days=30):
        est = "Por Vencer (< 1 mes)"
        por_vencer_count += 1
      else:
        est = "Vigente"

      filas.append({
          "RUT": d["rut_trabajador"],
          "Trabajador": trab_info.get("nombre_completo", "N/A"),
          "Cargo": trab_info.get("cargo", "N/A"),
          "División": trab_info.get("division", "N/A"),
          "Categoría": d["categoria"],
          "Curso/Examen": d["nombre_curso_examen"],
          "F. Vencimiento": f_venc_str,
          "Estado": est,
      })

    df_venc = pd.DataFrame(filas)

    col_m1, col_m2 = st.columns(2)
    col_m1.metric("🔴 Total Vencidos", vencidos_count)
    col_m2.metric("🟡 Por Vencer (Menos de 30 días)", por_vencer_count)

    st.markdown("---")

    filtro_estado = st.multiselect(
        "Filtrar Alertas por Estado",
        ["Vigente", "Por Vencer (< 1 mes)", "Vencido"],
        default=["Por Vencer (< 1 mes)", "Vencido"],
    )

    df_filtrado = df_venc[df_venc["Estado"].isin(filtro_estado)]

    if not df_filtrado.empty:
      st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    else:
      st.success(
          "🎉 ¡Excelente noticia! No hay registros en los estados seleccionados."
      )
  else:
    st.info("Aún no hay registros de capacitaciones cargados en el sistema.")
