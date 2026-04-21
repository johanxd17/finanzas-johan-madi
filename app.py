import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURACIÓN E INGRESOS ---
st.set_page_config(page_title="Sistema IA Financiera - Johan & Madi", layout="wide", page_icon="🏦")

# --- 1.5 CABECERA MAQUETADA Y CENTRADA (IMAGEN PEQUEÑA) ---
st.write("") # Espacio para dar aire arriba

# CAMBIAMOS LA PROPORCIÓN DE COLUMNAS PARA REDUCIR EL LOGO
# Usamos [1, 1, 5, 1]: La columna del logo (1) es ahora la mitad de ancha 
# que antes (2), y la del título (5) es más ancha para compensar.
m_izq, col_logo, col_titulo, m_der = st.columns([1, 1, 5, 1])

with col_logo:
    st.image("HORU.jpeg", use_container_width=True)
    # Este pequeño estilo hace que los bordes de la imagen sean curvos
    st.markdown('<style>img {border-radius: 15px;}</style>', unsafe_allow_html=True)

with col_titulo:
    # Título estilizado y mensaje de bienvenida
    st.markdown("<h1 style='color: #2E86C1; margin-top: 10px; font-size: 2.2em;'>🛡️ Panel de Control Financiero Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.1em; color: #808B96; margin-top: -10px;'>Gestión de Activos y Control de Riesgos | <b>Johan & Madi</b></p>", unsafe_allow_html=True)

st.divider()

# --- 2. CONFIGURACIÓN DE INGRESOS ---
MI_SUELDO = 960.00
SUELDO_MADI = 560.00
AHORRO_YAPE = 107.14
TOTAL_INGRESOS = MI_SUELDO + SUELDO_MADI + AHORRO_YAPE

# Botón de actualización en el Sidebar
if st.sidebar.button('🔄 Sincronizar Datos'):
    st.cache_data.clear()
    st.rerun()

# --- 3. CONEXIÓN A TU GOOGLE SHEETS ---
SHEET_ID = "1ju4BGM20CCdDnPNLzSPv5RWjlBi01uq7XO-6x-KnsWc"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# --- NUEVO: FILTROS EN EL SIDEBAR ---
st.sidebar.divider()
st.sidebar.subheader("🔍 Filtros de Visualización")

# Tus ingresos reales
INGRESOS_TOTALES = 960.00 + 560.00 + 107.14

# --- 2. IA DE CLASIFICACIÓN (NLP) ---
def clasificador_ia(concepto):
    if pd.isna(concepto): return "❓ Otros"
    concepto = str(concepto).lower().strip()
    if any(word in concepto for word in ['menu', 'comida', 'ceviche', 'pizza', 'hamburguesa', 'almuerzo']):
        return "🍱 Alimentación"
    if any(word in concepto for word in ['pasaje', 'bus', 'taxi', 'gasolina', 'corredor']):
        return "🚗 Transporte"
    if any(word in concepto for word in ['cuota', 'iphone', 'prestamo', 'banco', 'interbank', 'bbva', 'scotia']):
        return "💳 Deudas/Fijos"
    if any(word in concepto for word in ['cine', 'netflix', 'juego', 'salida', 'cerveza', 'switch']):
        return "🎮 Diversión"
    return "❓ Otros"

try:
    # 1. Carga de datos
    df = pd.read_csv(url)
    
    # 2. Limpieza de nombres de columnas (Quita espacios invisibles)
    df.columns = [c.strip() for c in df.columns]

    # --- 🛡️ LIMPIEZA MAESTRA DE DATOS (ELIMINA EL ERROR DE STR VS FLOAT) ---
    # Buscamos la columna de Monto sin importar si es "Monto", "monto" o " Monto "
    col_monto = next((c for c in df.columns if 'monto' in c.lower()), 'Monto')
    
    if col_monto in df.columns:
        # Convertimos a texto, quitamos "S/", comas y espacios, y luego a número
        df[col_monto] = df[col_monto].astype(str).str.replace('S/', '', regex=False).str.replace(',', '', regex=False).str.strip()
        df[col_monto] = pd.to_numeric(df[col_monto], errors='coerce').fillna(0)
        # Renombramos a "Monto" exacto para que el resto del código no falle
        df = df.rename(columns={col_monto: 'Monto'})

    # Buscamos la columna de Fecha (por si acaso en el Excel sale como "ha")
    col_fecha = next((c for c in df.columns if 'fecha' in c.lower() or 'ha' == c.lower()), 'Fecha')
    if col_fecha in df.columns:
        df['Fecha'] = pd.to_datetime(df[col_fecha], errors='coerce', dayfirst=True)
        df['Fecha'] = df['Fecha'].fillna(datetime.now())
        if col_fecha != 'Fecha':
            df = df.drop(columns=[col_fecha])

    # 3. Filtro de Bancos (Ahora con datos limpios)
    if 'Banco' in df.columns:
        bancos_disponibles = sorted(df['Banco'].unique().astype(str))
        banco_selec = st.sidebar.multiselect("Seleccionar Bancos:", options=bancos_disponibles, default=bancos_disponibles)
        df = df[df['Banco'].isin(banco_selec)]
        df['Banco'] = df['Banco'].astype(str).str.strip().str.upper()
    
    if 'Responsable' in df.columns:
        df['Responsable'] = df['Responsable'].astype(str).str.strip().str.capitalize()

    # 4. Auto-llenado de categorías
    columnas_categoria = [c for c in df.columns if 'Categor' in c]
    col_cat = columnas_categoria[0] if columnas_categoria else "Categoría"
    if col_cat not in df.columns: df[col_cat] = ""
    
    df[col_cat] = df.apply(
        lambda x: clasificador_ia(x['Concepto']) 
        if pd.isna(x[col_cat]) or str(x[col_cat]).strip() == '' 
        else x[col_cat], axis=1
    )

    # --- 📊 VISUALIZACIÓN DE MÉTRICAS ---
    gastos_totales = df['Monto'].sum()
    saldo_actual = INGRESOS_TOTALES - gastos_totales
    porcentaje_gastado = (gastos_totales / INGRESOS_TOTALES) if INGRESOS_TOTALES > 0 else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("Ingresos Totales", f"S/ {INGRESOS_TOTALES:.2f}")
    m2.metric("Gasto Acumulado", f"S/ {gastos_totales:.2f}", delta=f"{porcentaje_gastado:.1%}", delta_color="inverse")
    m3.metric("Fondo de Maniobra", f"S/ {saldo_actual:.2f}")

    st.write("### 🌡️ Nivel de Salud Financiera")
    st.progress(min(porcentaje_gastado, 1.0))
    
    # Mensajes de salud
    if porcentaje_gastado < 0.7:
        st.success(f"✅ ESTADO SALUDABLE: Todo bajo control en Organa")
    elif porcentaje_gastado < 0.9:
        st.warning(f"⚠️ PRECAUCIÓN: Vigila los gastos hormiga")
    else:
        st.error(f"🚨 ALERTA CRÍTICA: Has superado el límite sugerido")

    st.divider()

    # --- 📈 ANÁLISIS DE MOVIMIENTOS ---
    st.subheader("📊 Análisis de Movimientos")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(px.pie(df, values='Monto', names='Banco', hole=0.4, title="Bancos"), use_container_width=True)
    with c2:
        if 'Responsable' in df.columns:
            st.plotly_chart(px.pie(df, values='Monto', names='Responsable', hole=0.4, title="Johan vs Madi"), use_container_width=True)
    with c3:
        st.plotly_chart(px.bar(df.groupby(col_cat)['Monto'].sum().reset_index(), x=col_cat, y='Monto', title="Categorías"), use_container_width=True)

    # --- 📉 TENDENCIA Y TOP 5 ---
    st.divider()
    if not df.empty:
        st.subheader("📈 Tendencia de Gasto")
        df_linea = df.groupby(df['Fecha'].dt.date)['Monto'].sum().reset_index()
        st.plotly_chart(px.line(df_linea, x='Fecha', y='Monto', markers=True), use_container_width=True)

        st.subheader("🔝 Los 5 gastos más fuertes")
        top_5 = df.nlargest(5, 'Monto')[['Fecha', 'Concepto', 'Monto', 'Banco']]
        top_5['Fecha'] = top_5['Fecha'].dt.strftime('%d/%m/%Y')
        st.table(top_5)

    # --- 🤖 ORÁCULO IA ---
    st.divider()
    st.subheader("🤖 Oráculo IA")
    # Filtramos montos variables (menores a 200) y fijos (como el iPhone)
    df_var = df[df['Monto'] < 200]
    df_fij = df[df['Monto'] >= 200]
    
    dias = max(((datetime.now() - df['Fecha'].min()).days + 1), 1)
    promedio_diario = df_var['Monto'].sum() / dias
    proyeccion = (promedio_diario * 30) + df_fij['Monto'].sum()
    
    c_ia1, c_ia2 = st.columns(2)
    with c_ia1:
        if proyeccion > INGRESOS_TOTALES:
            st.error(f"La IA estima S/ {proyeccion:.2f} a fin de mes. ¡Atención!")
        else:
            st.success(f"La IA estima S/ {proyeccion:.2f}. ¡Van por buen camino!")
    with c_ia2:
        st.info(f"Ahorro proyectado: **S/ {max(0, INGRESOS_TOTALES - proyeccion):.2f}**")

    # --- 📂 REGISTRO MAESTRO ---
    st.subheader("📂 Registro Maestro")
    df_ver = df.copy()
    df_ver['Fecha'] = df_ver['Fecha'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_ver.sort_values(by='Monto', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Error detectado: {e}")
