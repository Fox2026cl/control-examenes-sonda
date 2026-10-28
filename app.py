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

# --- CONFIGURACIÓN DE USUARIOS Y ROLES ---
USUARIOS = {
    "admin": {"password": "Sond@.2026", "rol": "admin", "nombre": "Administrador"},
    "consulta": {"password": "VisorSonda2026!", "rol": "visor", "nombre": "Usuario Lectura"},
}

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
            font-size: 14px;
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

# --- GESTIÓN DE SESIÓN (LOGIN) ---
if "autenticado" not in st.session_state:
  st.session_state["autenticado"] = False
  st.session_state["usuario_actual"] = None
  st.session_state["rol"] = None


def mostrar_login():
  st.markdown("<br><br>", unsafe_allow_html=True)
  col1, col2, col3 = st.columns([1, 2, 1])

  with col2:
    st.image(
        "https://img.icons8.com/color/96/shield-protection.png", width=80
    )
    st.title("Acceso Privado - Sonda")
    st.subheader("Sistema de Control de Exámenes y Capacitaciones")

    with st.form("form_login"):
      usuario_input = st.text_input("Usuario").strip()
      password_input = st.text_input("Contraseña", type="password").strip()
      btn_login = st.form_submit_button("🔑 Iniciar Sesión")

      if btn_login:
        if (
            usuario_input in USUARIOS
            and USUARIOS[usuario_input]["password"] == password_input
        ):
          st.session_state["autenticado"] = True
          st.session_state["usuario_actual"] = USUARIOS[usuario_input]["nombre"]
          st.session_state["rol"] = USUARIOS[usuario_input]["rol"]
          st.success(f"¡Bienvenido, {USUARIOS[usuario_input]['nombre']}!")
          st.rerun()
        else:
          st.error("❌ Usuario o contraseña incorrectos.")


if not st.session_state["autenticado"]:
  mostrar_login()
  st.stop()

# -------------------------------------------------------------------
# SISTEMA PRINCIPAL Y NAVEGACIÓN SEGÚN ROL
# -------------------------------------------------------------------

st.title("🛡️ Sistema de Gestión de Exámenes y Cursos - Sonda")

st.sidebar.markdown("### 👤 Sesión Iniciada")
st.sidebar.write(f"**Usuario:** `{st.session_state['usuario_actual']}`")
st.sidebar.write(
    f"**Rol:** `{'Administrador (Edición)' if st.session_state['rol'] == 'admin' else 'Visor (Solo Lectura)'}`"
)

if st.sidebar.button("🚪 Cerrar Sesión"):
  st.session_state["autenticado"] = False
  st.session_state["usuario_actual"] = None
  st.session_state["rol"] = None
  st.rerun()

st.sidebar.markdown("---")

if st.session_state["rol"] == "admin":
  opciones_menu = [
      "📊 Ficha de Trabajador y Documentos",
      "➕ Registrar Examen / Curso",
      "✏️ Actualizar / Renovar Exámenes",
      "👥 Gestionar Trabajadores",
      "⚠️ Panel de Alertas y Vencimientos",
  ]
else:
  opciones_menu = [
      "📊 Ficha de Trabajador y Documentos",
      "⚠️ Panel de Alertas y Vencimientos",
  ]

menu = st.sidebar.radio("Navegación", opciones_menu)

# -------------------------------------------------------------------
# OPCIÓN 1: FICHA DETALLADA DE TRABAJADOR
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
        "Seleccione un Trabajador para revisar su Ficha Completa:",
        df_trabajadores["rut"] + " - " + df_trabajadores["nombre_completo"],
    )
    rut_sel = opcion_trabajador.split(" - ")[0]
    trab = df_trabajadores[df_trabajadores["rut"] == rut_sel].iloc[0]

    st.markdown("---")

    # Resumen Superior
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        f'<div class="worker-card"><div'
        ' class="worker-label">Nombre</div><div'
        f' class="worker-value">{trab.get("nombre_completo", "N/A")}</div></div>',
        unsafe_allow_html=True,
    )
    c2.markdown(
        f'<div class="worker-card"><div class="worker-label">RUT</div><div'
        f' class="worker-value">{trab.get("rut", "N/A")}</div></div>',
        unsafe_allow_html=True,
    )
    c3.markdown(
        f'<div class="worker-card"><div class="worker-label">Cargo'
        ' Sonda</div><div'
        f' class="worker-value">{trab.get("cargo_sonda") or trab.get("cargo") or "N/A"}</div></div>',
        unsafe_allow_html=True,
    )
    c4.markdown(
        f'<div class="worker-card"><div'
        ' class="worker-label">División</div><div'
        f' class="worker-value">{trab.get("division", "N/A")}</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Pestañas de Ficha Expandida
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Información General y Contrato",
        "👤 Datos Personales y Contacto",
        "🚗 Licencia y Conducción",
        "🦺 Salud y Riesgo Ocupacional (GES)",
    ])

    with tab1:
      col_a, col_b = st.columns(2)
      with col_a:
        st.write(
            f"**Número de Contrato:** {trab.get('numero_contrato') or 'N/A'}"
        )
        st.write(
            f"**Cargo Codelco:** {trab.get('cargo_codelco') or 'N/A'}"
        )
        st.write(f"**Cargo Sonda:** {trab.get('cargo_sonda') or 'N/A'}")
        st.write(f"**Fecha Ingreso:** {trab.get('fecha_ingreso') or 'N/A'}")
      with col_b:
        st.write(
            f"**Jornada Laboral:** {trab.get('jornada_laboral') or 'N/A'}"
        )
        st.write(f"**Turno:** {trab.get('turno') or 'N/A'}")
        st.write(
            f"**Experiencia en Minería:**"
            f" {trab.get('experiencia_mineria') or 'N/A'}"
        )
        st.write(
            f"**Experiencia en el Cargo:**"
            f" {trab.get('experiencia_cargo') or 'N/A'}"
        )
        st.write(
            f"**Obligación de Informar (ODI):**"
            f" {trab.get('obligacion_informar') or 'N/A'}"
        )

    with tab2:
      col_c, col_d = st.columns(2)
      with col_c:
        st.write(
            f"**Fecha Nacimiento:** {trab.get('fecha_nacimiento') or 'N/A'}"
        )
        st.write(f"**Edad:** {trab.get('edad') or 'N/A'}")
        st.write(f"**Sexo:** {trab.get('sexo') or 'N/A'}")
        st.write(f"**Estado Civil:** {trab.get('estado_civil') or 'N/A'}")
        st.write(f"**Nacionalidad:** {trab.get('nacionalidad') or 'N/A'}")
        st.write(f"**Dirección:** {trab.get('direccion') or 'N/A'}")
      with col_d:
        st.write(
            f"**Celular Empresa:** {trab.get('celular_empresa') or 'N/A'}"
        )
        st.write(
            f"**Celular Personal:** {trab.get('celular_personal') or 'N/A'}"
        )
        st.write(
            f"**Correo Laboral:** {trab.get('correo_laboral') or 'N/A'}"
        )
        st.write(
            f"**Correo Personal:** {trab.get('correo_personal') or 'N/A'}"
        )

    with tab3:
      col_e, col_f = st.columns(2)
      with col_e:
        st.write(
            f"**Licencia Municipal:**"
            f" {trab.get('licencia_municipal') or 'N/A'}"
        )
        st.write(
            f"**Clase Licencia:**"
            f" {trab.get('clase_licencia_municipal') or 'N/A'}"
        )
        st.write(
            f"**Municipalidad:** {trab.get('municipalidad') or 'N/A'}"
        )
      with col_f:
        st.write(f"**Restricciones:** {trab.get('restriccion') or 'N/A'}")
        st.write(
            f"**Hoja de Vida Conductor:**"
            f" {trab.get('hoja_vida_conductor') or 'N/A'}"
        )

    with tab4:
      col_g, col_h = st.columns(2)
      with col_g:
        st.write(
            f"**Grupo Sanguíneo:**"
            f" `{trab.get('grupo_sanguineo') or 'N/A'}`"
        )
        st.write(
            f"**Grupo Exposición Similar (GES):**"
            f" {trab.get('grupo_exposicion_similar') or 'N/A'}"
        )
        st.write(f"**Nivel GES:** {trab.get('nivel_ges') or 'N/A'}")
      with col_h:
        st.write(
            f"**HID Credencial:** {trab.get('hid_credencial') or 'N/A'}"
        )
        st.write(f"**TAG:** {trab.get('tag') or 'N/A'}")

    st.markdown("---")
    st.subheader("📁 Cursos, Inducciones y Exámenes Ocupacionales")

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
          color_estado, estado_txt = "🟡", "Por Vencer (< 1 mes)"
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
# OPCIÓN 2: REGISTRAR EXAMEN / CURSO (SOLO ADMIN)
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
# OPCIÓN 3: ACTUALIZAR / RENOVACIÓN (SOLO ADMIN)
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
# OPCIÓN 4: GESTIONAR TRABAJADORES (CON FECHA DE INGRESO INCLUIDA)
# -------------------------------------------------------------------
elif menu == "👥 Gestionar Trabajadores":
  st.subheader("👥 Administración del Personal (Ficha Completa)")

  accion_trab = st.radio(
      "Seleccione Acción",
      [
          "➕ Agregar Nuevo Trabajador",
          "✏️ Modificar / Eliminar Trabajador Existente",
      ],
      horizontal=True,
  )

  if accion_trab == "➕ Agregar Nuevo Trabajador":
    with st.form("form_nuevo_trabajador", clear_on_submit=True):
      st.write("### 1. Datos Principales y Contrato")
      c_rut = st.text_input("RUT (Ej: 12345678-9)")
      c_nombres = st.text_input("Nombres")
      c_ap1 = st.text_input("Primer Apellido")
      c_ap2 = st.text_input("Segundo Apellido")

      col_t1, col_t2, col_t3 = st.columns(3)
      c_div = col_t1.text_input("División (Ej: DCH)")
      c_cargo_sonda = col_t2.text_input("Cargo Sonda")
      c_cargo_codelco = col_t3.text_input("Cargo Codelco")

      col_t4, col_t5, col_t6 = st.columns(3)
      c_num_contrato = col_t4.text_input("Número Contrato")
      c_fingreso = col_t5.date_input("Fecha de Ingreso", value=datetime.now())
      c_jornada = col_t6.text_input("Jornada Laboral")

      col_t7, col_t8, col_t9 = st.columns(3)
      c_turno = col_t7.text_input("Turno")
      c_exp_mineria = col_t8.text_input("Experiencia Minería")
      c_exp_cargo = col_t9.text_input("Experiencia Cargo")

      c_odi = st.text_input("Obligación de Informar (ODI)")

      st.markdown("---")
      st.write("### 2. Datos Personales y Contacto")
      col_p1, col_p2, col_p3 = st.columns(3)
      c_fnac = col_p1.date_input(
          "Fecha Nacimiento", value=datetime(1990, 1, 1)
      )
      c_edad = col_p2.number_input("Edad", min_value=18, max_value=80, value=30)
      c_sexo = col_p3.selectbox("Sexo", ["Masculino", "Femenino", "Otro"])

      col_p4, col_p5, col_p6 = st.columns(3)
      c_ecivil = col_p4.text_input("Estado Civil")
      c_nacionalidad = col_p5.text_input("Nacionalidad", value="Chilena")
      c_direccion = col_p6.text_input("Dirección")

      col_c1, col_c2 = st.columns(2)
      c_cel_emp = col_c1.text_input("Celular Empresa")
      c_cel_per = col_c2.text_input("Celular Personal")

      col_c3, col_c4 = st.columns(2)
      c_mail_lab = col_c3.text_input("Correo Laboral")
      c_mail_per = col_c4.text_input("Correo Personal")

      st.markdown("---")
      st.write("### 3. Licencias y Conducción")
      col_l1, col_l2, col_l3 = st.columns(3)
      c_lic_muni = col_l1.text_input("Licencia Municipal")
      c_clase_muni = col_l2.text_input("Clase Licencia Municipal")
      c_muni = col_l3.text_input("Municipalidad")

      col_l4, col_l5 = st.columns(2)
      c_restriccion = col_l4.text_input("Restricción")
      c_hoja_vida = col_l5.text_input("Hoja de Vida Conductor")

      st.markdown("---")
      st.write("### 4. Salud, GES y Credenciales")
      col_s1, col_s2, col_s3 = st.columns(3)
      c_sangre = col_s1.text_input("Grupo Sanguíneo (Ej: O RH(+), A II NEG)")
      c_ges = col_s2.text_input("Grupo Exposición Similar (GES)")
      c_nivel_ges = col_s3.text_input("Nivel GES")

      col_s4, col_s5 = st.columns(2)
      c_hid = col_s4.text_input("HID Credencial")
      c_tag = col_s5.text_input("TAG")

      btn_guardar_trab = st.form_submit_button("💾 Guardar Trabajador Completo")

      if btn_guardar_trab:
        if not c_rut or not c_nombres:
          st.error("El RUT y el Nombres son obligatorios.")
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
              "cargo": c_cargo_sonda.strip(),
              "cargo_sonda": c_cargo_sonda.strip(),
              "cargo_codelco": c_cargo_codelco.strip(),
              "numero_contrato": c_num_contrato.strip(),
              "fecha_ingreso": str(c_fingreso),
              "jornada_laboral": c_jornada.strip(),
              "turno": c_turno.strip(),
              "experiencia_mineria": c_exp_mineria.strip(),
              "experiencia_cargo": c_exp_cargo.strip(),
              "obligacion_informar": c_odi.strip(),
              "fecha_nacimiento": str(c_fnac),
              "edad": int(c_edad),
              "sexo": c_sexo,
              "estado_civil": c_ecivil.strip(),
              "nacionalidad": c_nacionalidad.strip(),
              "direccion": c_direccion.strip(),
              "celular_empresa": c_cel_emp.strip(),
              "celular_personal": c_cel_per.strip(),
              "correo_laboral": c_mail_lab.strip(),
              "correo_personal": c_mail_per.strip(),
              "licencia_municipal": c_lic_muni.strip(),
              "clase_licencia_municipal": c_clase_muni.strip(),
              "municipalidad": c_muni.strip(),
              "restriccion": c_restriccion.strip(),
              "hoja_vida_conductor": c_hoja_vida.strip(),
              "grupo_sanguineo": c_sangre.strip(),
              "grupo_exposicion_similar": c_ges.strip(),
              "nivel_ges": c_nivel_ges.strip(),
              "hid_credencial": c_hid.strip(),
              "tag": c_tag.strip(),
          }

          supabase.table("trabajadores").upsert(nuevo_t_data).execute()
          st.success(
              f"✅ ¡Trabajador {nombre_completo_val} guardado con éxito!"
          )

  else:
    res_all = (
        supabase.table("trabajadores")
        .select("*")
        .order("nombre_completo")
        .execute()
    )
    df_all = pd.DataFrame(res_all.data)

    if not df_all.empty:
      sel_t_edit = st.selectbox(
          "Seleccione el Trabajador a Editar o Eliminar",
          df_all["rut"] + " - " + df_all["nombre_completo"],
      )
      rut_edit = sel_t_edit.split(" - ")[0]
      d_act = df_all[df_all["rut"] == rut_edit].iloc[0]

      with st.form("form_editar_trabajador"):
        st.write(
            f"### ✏️ Editando Ficha Completa de: {d_act['nombre_completo']}"
        )

        e_nombres = st.text_input("Nombres", value=d_act.get("nombre") or "")
        e_ap1 = st.text_input(
            "Primer Apellido", value=d_act.get("apellido1") or ""
        )
        e_ap2 = st.text_input(
            "Segundo Apellido", value=d_act.get("apellido2") or ""
        )

        col_e1, col_e2, col_e3 = st.columns(3)
        e_div = col_e1.text_input(
            "División", value=d_act.get("division") or ""
        )
        e_cargo_sonda = col_e2.text_input(
            "Cargo Sonda", value=d_act.get("cargo_sonda") or ""
        )
        e_cargo_codelco = col_e3.text_input(
            "Cargo Codelco", value=d_act.get("cargo_codelco") or ""
        )

        col_e4, col_e5, col_e6 = st.columns(3)
        e_contrato = col_e4.text_input(
            "N° Contrato", value=d_act.get("numero_contrato") or ""
        )

        # Parse fecha ingreso
        try:
          f_ing_val = datetime.strptime(
              str(d_act.get("fecha_ingreso")).split("T")[0], "%Y-%m-%d"
          ).date()
        except:
          f_ing_val = datetime.now().date()

        e_fingreso = col_e5.date_input("Fecha Ingreso", value=f_ing_val)
        e_jornada = col_e6.text_input(
            "Jornada Laboral", value=d_act.get("jornada_laboral") or ""
        )

        col_e7, col_e8, col_e9 = st.columns(3)
        e_turno = col_e7.text_input("Turno", value=d_act.get("turno") or "")
        e_exp_min = col_e8.text_input(
            "Experiencia Minería",
            value=d_act.get("experiencia_mineria") or "",
        )
        e_exp_car = col_e9.text_input(
            "Experiencia Cargo", value=d_act.get("experiencia_cargo") or ""
        )

        e_odi = st.text_input(
            "ODI", value=d_act.get("obligacion_informar") or ""
        )

        st.markdown("#### Contacto y Datos Personales")
        col_ep1, col_ep2, col_ep3 = st.columns(3)
        try:
          f_nac_val = datetime.strptime(
              str(d_act.get("fecha_nacimiento")).split("T")[0], "%Y-%m-%d"
          ).date()
        except:
          f_nac_val = datetime(1990, 1, 1).date()

        e_fnac = col_ep1.date_input("Fecha Nacimiento", value=f_nac_val)
        e_edad = col_ep2.number_input(
            "Edad",
            min_value=18,
            max_value=80,
            value=int(d_act.get("edad")) if pd.notna(d_act.get("edad")) else 30,
        )
        e_sexo = col_ep3.selectbox(
            "Sexo",
            ["Masculino", "Femenino", "Otro"],
            index=0
            if str(d_act.get("sexo")) == "Masculino"
            else (1 if str(d_act.get("sexo")) == "Femenino" else 0),
        )

        col_ep4, col_ep5, col_ep6 = st.columns(3)
        e_ecivil = col_ep4.text_input(
            "Estado Civil", value=d_act.get("estado_civil") or ""
        )
        e_naci = col_ep5.text_input(
            "Nacionalidad", value=d_act.get("nacionalidad") or ""
        )
        e_dir = col_ep6.text_input(
            "Dirección", value=d_act.get("direccion") or ""
        )

        col_ec1, col_ec2, col_ec3, col_ec4 = st.columns(4)
        e_cel_emp = col_ec1.text_input(
            "Celular Empresa", value=d_act.get("celular_empresa") or ""
        )
        e_cel_per = col_ec2.text_input(
            "Celular Personal", value=d_act.get("celular_personal") or ""
        )
        e_mail_lab = col_ec3.text_input(
            "Correo Laboral", value=d_act.get("correo_laboral") or ""
        )
        e_mail_per = col_ec4.text_input(
            "Correo Personal", value=d_act.get("correo_personal") or ""
        )

        st.markdown("#### Licencias y Conducción")
        col_el1, col_el2, col_el3, col_el4, col_el5 = st.columns(5)
        e_lic_mun = col_el1.text_input(
            "Licencia Municipal", value=d_act.get("licencia_municipal") or ""
        )
        e_clase = col_el2.text_input(
            "Clase Licencia",
            value=d_act.get("clase_licencia_municipal") or "",
        )
        e_muni = col_el3.text_input(
            "Municipalidad", value=d_act.get("municipalidad") or ""
        )
        e_rest = col_el4.text_input(
            "Restricción", value=d_act.get("restriccion") or ""
        )
        e_hvc = col_el5.text_input(
            "Hoja Vida Conductor",
            value=d_act.get("hoja_vida_conductor") or "",
        )

        st.markdown("#### Salud y GES")
        col_es1, col_es2, col_es3, col_es4, col_es5 = st.columns(5)
        e_sangre = col_es1.text_input(
            "Grupo Sanguíneo", value=d_act.get("grupo_sanguineo") or ""
        )
        e_ges = col_es2.text_input(
            "GES", value=d_act.get("grupo_exposicion_similar") or ""
        )
        e_nges = col_es3.text_input(
            "Nivel GES", value=d_act.get("nivel_ges") or ""
        )
        e_hid = col_es4.text_input(
            "HID Credencial", value=d_act.get("hid_credencial") or ""
        )
        e_tag = col_es5.text_input("TAG", value=d_act.get("tag") or "")

        col_b1, col_b2 = st.columns(2)
        btn_act_t = col_b1.form_submit_button("💾 Actualizar Ficha Completa")
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
              "cargo": e_cargo_sonda.strip(),
              "cargo_sonda": e_cargo_sonda.strip(),
              "cargo_codelco": e_cargo_codelco.strip(),
              "numero_contrato": e_contrato.strip(),
              "fecha_ingreso": str(e_fingreso),
              "jornada_laboral": e_jornada.strip(),
              "turno": e_turno.strip(),
              "experiencia_mineria": e_exp_min.strip(),
              "experiencia_cargo": e_exp_car.strip(),
              "obligacion_informar": e_odi.strip(),
              "fecha_nacimiento": str(e_fnac),
              "edad": int(e_edad),
              "sexo": e_sexo,
              "estado_civil": e_ecivil.strip(),
              "nacionalidad": e_naci.strip(),
              "direccion": e_dir.strip(),
              "celular_empresa": e_cel_emp.strip(),
              "celular_personal": e_cel_per.strip(),
              "correo_laboral": e_mail_lab.strip(),
              "correo_personal": e_mail_per.strip(),
              "licencia_municipal": e_lic_mun.strip(),
              "clase_licencia_municipal": e_clase.strip(),
              "municipalidad": e_muni.strip(),
              "restriccion": e_rest.strip(),
              "hoja_vida_conductor": e_hvc.strip(),
              "grupo_sanguineo": e_sangre.strip(),
              "grupo_exposicion_similar": e_ges.strip(),
              "nivel_ges": e_nges.strip(),
              "hid_credencial": e_hid.strip(),
              "tag": e_tag.strip(),
          }).eq("rut", rut_edit).execute()
          st.success("✅ ¡Ficha completa actualizada con éxito!")
          st.rerun()

        if btn_del_t:
          supabase.table("trabajadores").delete().eq(
              "rut", rut_edit
          ).execute()
          st.warning("🗑️ Trabajador eliminado del sistema.")
          st.rerun()
    else:
      st.info("No hay trabajadores en la base de datos.")

# -------------------------------------------------------------------
# OPCIÓN 5: PANEL DE ALERTAS
# -------------------------------------------------------------------
elif menu == "⚠️ Panel de Alertas y Vencimientos":
  st.subheader("⚠️ Panel General de Alertas (Exámenes y Cursos)")

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
      st.success("🎉 ¡No hay registros en los estados seleccionados!")
  else:
    st.info("Aún no hay registros cargados en el sistema.")
