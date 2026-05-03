import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURACIÓN E INGRESOS ---
st.set_page_config(page_title="Sistema IA Financiera - Johan & Madi", layout="wide", page_icon="🏦")

# --- 1.5 CABECERA ---
st.write("") 

m_izq, col_logo, col_titulo, m_der = st.columns([1, 1, 5, 1])

with col_logo:
    try:
        st.image("HORU.jpeg", use_container_width=True)
    except:
        st.write("🏢")

with col_titulo:
    st.markdown("<h1 style='color: #2E86C1; margin-top: 10px; font-size: 2.2em;'>🛡️ Panel de Control Financiero Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.1em; color: #808B96; margin-top: -10px;'>Gestión de Activos y Control de Riesgos | <b>Johan & Madi</b></p>", unsafe_allow_html=True)

st.divider()

# --- 2. CONFIGURACIÓN DE INGRESOS (Ajustado a tus montos actuales) ---
MI_SUELDO = 1068.29
SUELDO_MADI = 602.00
AHORRO_YAPE = 68.00
APOYO_MAMA = 500.00 # El extra que te envió tu mamá
INGRESOS_TOTALES = MI_SUELDO + SUELDO_MADI + AHORRO_YAPE + APOYO_MAMA

FECHAS_BANCOS = {
    'BCP': [10, 5],
    'BBVA': [10, 5],
    'INTERBANK': [27, 21],
    'SCOTIABANK': [11, 8]
}

# --- SIDEBAR: PAGOS Y FILTROS ---
st.sidebar.subheader("✅ Confirmar Pagos")
pagos_confirmados = {}
for banco in FECHAS_BANCOS.keys():
    pagos_confirmados[banco] = st.sidebar.checkbox(f"Pagué {banco}", key=f"pay_{banco}")

st.sidebar.divider()
st.sidebar.subheader("🎯 Enfoque de Pagos")
fase_pago = st.sidebar.radio(
    "Ver vencimientos de:",
    ["Próximos (BCP/BBVA - 05 May)", "Siguiente (Interbank - 21 May)", "Futuro (Scotiabank - Jun)", "Ver Todo"]
)

# --- 3. CONEXIÓN A DATOS ---
SHEET_ID = "1ju4BGM20CCdDnPNLzSPv5RWjlBi01uq7XO-6x-KnsWc"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

def clasificador_ia(concepto):
    if pd.isna(concepto): return "❓ Otros"
    concepto = str(concepto).lower().strip()
    if any(word in concepto for word in ['menu', 'comida', 'almuerzo', 'moka']): return "🍱 Alimentación/Mascota"
    if any(word in concepto for word in ['pasaje', 'bus', 'taxi']): return "🚗 Transporte"
    if any(word in concepto for word in ['cuota', 'prestamo', 'banco', 'iphone']): return "💳 Deudas/Fijos"
    if any(word in concepto for word in ['cine', 'juego', 'switch']): return "🎮 Diversión"
    return "❓ Otros"

try:
    df = pd.read_csv(url)
    df.columns = [c.strip() for c in df.columns]

    # --- NORMALIZACIÓN CRÍTICA (Antes de filtrar) ---
    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
        df['Fecha'] = df['Fecha'].fillna(datetime.now())
    
    if 'Monto' in df.columns:
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)

    # --- FILTRO HISTÓRICO POR COLUMNA "CICLO" ---
    st.sidebar.divider()
    st.sidebar.subheader("📅 Ver Historial")
    
    # Usamos la columna 'Ciclo' que creaste en Excel
    if 'Ciclo' in df.columns:
        ciclos_disponibles = df['Ciclo'].dropna().unique().tolist()
        mes_seleccionado = st.sidebar.selectbox("Seleccionar Ciclo:", ["Ciclo Actual"] + ciclos_disponibles)
    else:
        mes_seleccionado = "Ciclo Actual"
        st.sidebar.warning("No se encontró la columna 'Ciclo' en el Excel.")

    # Lógica de filtrado
    if mes_seleccionado != "Ciclo Actual":
        df_filtrado = df[df['Ciclo'] == mes_seleccionado]
        fase_pago_display = f"Histórico: {mes_seleccionado}"
    else:
        # Filtro por bancos (Tu lógica original)
        if fase_pago == "Próximos (BCP/BBVA - 05 May)":
            df_filtrado = df[df['Banco'].isin(['BCP', 'BBVA'])]
        elif fase_pago == "Siguiente (Interbank - 21 May)":
            df_filtrado = df[df['Banco'] == 'INTERBANK']
        elif fase_pago == "Futuro (Scotiabank - Jun)":
            df_filtrado = df[df['Banco'] == 'SCOTIABANK']
        else:
            df_filtrado = df
        fase_pago_display = fase_pago

    # --- MÉTRICAS ---
    gastos_fase = df_filtrado['Monto'].sum()
    saldo_proyectado = INGRESOS_TOTALES - gastos_fase
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Ingresos Totales", f"S/ {INGRESOS_TOTALES:.2f}")
    m2.metric(f"Total {fase_pago_display.split(' ')[0]}", f"S/ {gastos_fase:.2f}")
    m3.metric("Saldo Disponible", f"S/ {saldo_proyectado:.2f}")

    # --- CATEGORÍAS ---
    col_cat = "Categoría"
    df_filtrado[col_cat] = df_filtrado['Concepto'].apply(clasificador_ia)

    # --- GRÁFICOS ---
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.write("**💳 Gastos por Banco**")
        fig_banco = px.pie(df_filtrado, values='Monto', names='Banco', hole=0.4)
        st.plotly_chart(fig_banco, use_container_width=True)
    with c2:
        st.write("**🏷️ Gastos por Categoría**")
        df_cat = df_filtrado.groupby(col_cat)['Monto'].sum().reset_index()
        fig_cat = px.bar(df_cat, x=col_cat, y='Monto', color=col_cat)
        st.plotly_chart(fig_cat, use_container_width=True)

    # --- REGISTRO ---
    st.subheader("📂 Detalle de Movimientos")
    st.dataframe(df_filtrado, use_container_width=True)

except Exception as e:
    st.error(f"Se encontró un detalle técnico: {e}")
