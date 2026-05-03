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

# --- 2. CONFIGURACIÓN DE INGRESOS ---
MI_SUELDO = 1068.29
SUELDO_MADI = 602.00
AHORRO_YAPE = 68.00
APOYO_MAMA = 500.00
INGRESOS_TOTALES = MI_SUELDO + SUELDO_MADI + AHORRO_YAPE + APOYO_MAMA

FECHAS_BANCOS = {
    'BCP': [10, 5],
    'BBVA': [10, 5],
    'INTERBANK': [27, 21],
    'SCOTIABANK': [11, 8]
}

# --- SIDEBAR ---
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
    if any(word in concepto for word in ['menu', 'comida', 'moka']): return "🍱 Alimentación"
    if any(word in concepto for word in ['pasaje', 'bus', 'taxi']): return "🚗 Transporte"
    if any(word in concepto for word in ['cuota', 'prestamo', 'banco', 'iphone']): return "💳 Deudas/Fijos"
    if any(word in concepto for word in ['juego', 'switch']): return "🎮 Diversión"
    return "❓ Otros"

try:
    df = pd.read_csv(url)
    df.columns = [c.strip() for c in df.columns]

    # --- NORMALIZACIÓN DE FECHAS ---
    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
        df['Fecha'] = df['Fecha'].fillna(datetime.now())
    
    if 'Monto' in df.columns:
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
    
    if 'Responsable' in df.columns:
        df['Responsable'] = df['Responsable'].astype(str).str.strip().str.capitalize()

    # --- FILTRO POR CICLO (HISTORIAL) ---
    st.sidebar.divider()
    st.sidebar.subheader("📅 Ver Historial")
    if 'Ciclo' in df.columns:
        ciclos_disponibles = df['Ciclo'].dropna().unique().tolist()
        mes_seleccionado = st.sidebar.selectbox("Seleccionar Ciclo:", ["Ciclo Actual"] + ciclos_disponibles)
    else:
        mes_seleccionado = "Ciclo Actual"

    if mes_seleccionado != "Ciclo Actual":
        df_filtrado = df[df['Ciclo'] == mes_seleccionado]
        fase_pago_display = f"Ciclo: {mes_seleccionado}"
    else:
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

    # --- GRÁFICOS ANALÍTICOS (AQUÍ ESTÁ TODO) ---
    st.divider()
    st.subheader("📊 Análisis de Movimientos")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.write("**💳 Gestión por Bancos**")
        fig_banco = px.pie(df_filtrado, values='Monto', names='Banco', hole=0.4)
        st.plotly_chart(fig_banco, use_container_width=True)
    
    with c2:
        st.write("**👥 Johan vs Madi**") # <--- TU GRÁFICO REINTEGRADO
        if 'Responsable' in df_filtrado.columns:
            fig_resp = px.pie(df_filtrado, values='Monto', names='Responsable', hole=0.4)
            st.plotly_chart(fig_resp, use_container_width=True)
    
    with c3:
        st.write("**🏷️ Por Categoría**")
        df_filtrado['Categoría'] = df_filtrado['Concepto'].apply(clasificador_ia)
        df_cat = df_filtrado.groupby('Categoría')['Monto'].sum().reset_index()
        fig_cat = px.bar(df_cat, x='Categoría', y='Monto', color='Categoría')
        fig_cat.update_layout(showlegend=False)
        st.plotly_chart(fig_cat, use_container_width=True)

    # --- ORÁCULO IA ---
    st.divider()
    st.subheader("🤖 Oráculo IA")
    promedio_diario = (df_filtrado['Monto'].sum() / datetime.now().day) if datetime.now().day > 0 else 0
    proyeccion = promedio_diario * 30
    if proyeccion > INGRESOS_TOTALES:
        st.error(f"¡Cuidado! Proyección: S/ {proyeccion:.2f}. Supera tus ingresos.")
    else:
        st.success(f"Todo bajo control. Proyección fin de mes: S/ {proyeccion:.2f}")

    # --- REGISTRO MAESTRO ---
    st.subheader("📂 Registro Completo")
    st.dataframe(df_filtrado, use_container_width=True)

except Exception as e:
    st.error(f"Error técnico: {e}")
