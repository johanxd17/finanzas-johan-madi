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

# --- SIDEBAR: CONFIRMACIÓN Y FILTROS ---
st.sidebar.subheader("✅ Confirmar Pagos")
pagos_confirmados = {}
for banco in FECHAS_BANCOS.keys():
    pagos_confirmados[banco] = st.sidebar.checkbox(f"Pagué {banco}", key=f"pay_{banco}")

st.sidebar.divider()
st.sidebar.subheader("🎯 Enfoque de Pagos") # <--- FILTRO RESTAURADO
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

    # NORMALIZACIÓN
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce').fillna(datetime.now())
    df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
    if 'Responsable' in df.columns:
        df['Responsable'] = df['Responsable'].astype(str).str.strip().str.capitalize()
    if 'Banco' in df.columns:
        df['Banco'] = df['Banco'].astype(str).str.strip().str.upper()

    # FILTRO POR CICLO (HISTORIAL)
    st.sidebar.divider()
    st.sidebar.subheader("📅 Ver Historial")
    ciclos_disponibles = df['Ciclo'].dropna().unique().tolist() if 'Ciclo' in df.columns else []
    mes_seleccionado = st.sidebar.selectbox("Seleccionar Ciclo:", ["Ciclo Actual"] + ciclos_disponibles)

    # --- LÓGICA DE FILTRADO COMBINADA ---
    if mes_seleccionado != "Ciclo Actual":
        df_filtrado = df[df['Ciclo'] == mes_seleccionado]
        fase_display = f"Historial: {mes_seleccionado}"
    else:
        if fase_pago == "Próximos (BCP/BBVA - 05 May)":
            df_filtrado = df[df['Banco'].isin(['BCP', 'BBVA'])]
        elif fase_pago == "Siguiente (Interbank - 21 May)":
            df_filtrado = df[df['Banco'] == 'INTERBANK']
        elif fase_pago == "Futuro (Scotiabank - Jun)":
            df_filtrado = df[df['Banco'] == 'SCOTIABANK']
        else:
            df_filtrado = df
        fase_display = fase_pago

    # --- MÉTRICAS ---
    gastos_fase = df_filtrado['Monto'].sum()
    saldo_proyectado = INGRESOS_TOTALES - gastos_fase
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Ingresos Totales", f"S/ {INGRESOS_TOTALES:.2f}")
    m2.metric(f"Total {fase_display.split(' ')[0]}", f"S/ {gastos_fase:.2f}")
    m3.metric("Saldo Disponible", f"S/ {saldo_proyectado:.2f}")

    # --- BLOQUE: ALERTAS DE BANCOS ---
    st.subheader("🔔 Alertas de Pago")
    hoy = datetime.now().day
    columnas_alertas = st.columns(len(FECHAS_BANCOS))
    for i, (banco, fechas) in enumerate(FECHAS_BANCOS.items()):
        dia_corte, dia_pago = fechas
        with columnas_alertas[i]:
            if pagos_confirmados.get(banco):
                st.success(f"**{banco}**\n\n✅ Pagado")
            elif hoy <= dia_pago:
                faltan = dia_pago - hoy
                if faltan <= 3: st.error(f"**{banco}**\n\n🚨 {faltan} días")
                else: st.info(f"**{banco}**\n\n{faltan} días")
            else:
                st.warning(f"**{banco}**\n\nCorte: {dia_corte}")

    # --- BLOQUE: CONTROL DE CUOTAS Y AHORRO ---
    st.divider()
    col_c, col_a = st.columns(2)
    with col_c:
        st.subheader("🎯 Control de Cuotas")
        st.table([
            {"Compromiso": "Préstamo BBVA", "Monto": 174.12, "Vence": "05-May"},
            {"Compromiso": "Nintendo Switch", "Monto": 164.58, "Vence": "05-May"},
            {"Compromiso": "Powerpay (iPhones)", "Monto": 442.21, "Vence": "11-May"}
        ])
    with col_a:
        st.subheader("💰 Fondo de Emergencia")
        meta = 2000.0
        progreso = min(max(0, saldo_proyectado) / meta, 1.0)
        st.progress(progreso)
        st.write(f"S/ {max(0, saldo_proyectado):.2f} de S/ {meta:.2f}")

    # --- BLOQUE: ANÁLISIS GRÁFICO ---
    st.divider()
    st.subheader("📊 Análisis de Movimientos")
    g1, g2, g3 = st.columns(3)
    with g1:
        st.write("**💳 Por Banco**")
        st.plotly_chart(px.pie(df_filtrado, values='Monto', names='Banco', hole=0.4), use_container_width=True)
    with g2:
        st.write("**👥 Johan vs Madi**")
        if 'Responsable' in df_filtrado.columns:
            st.plotly_chart(px.pie(df_filtrado, values='Monto', names='Responsable', hole=0.4), use_container_width=True)
    with g3:
        st.write("**🏷️ Por Categoría**")
        df_filtrado['Categoría'] = df_filtrado['Concepto'].apply(clasificador_ia)
        df_cat = df_filtrado.groupby('Categoría')['Monto'].sum().reset_index()
        st.plotly_chart(px.bar(df_cat, x='Categoría', y='Monto', color='Categoría'), use_container_width=True)

    # --- ORÁCULO E HISTORIAL ---
    st.divider()
    st.subheader("🤖 Oráculo IA")
    proy = (df_filtrado['Monto'].sum() / datetime.now().day) * 30 if datetime.now().day > 0 else 0
    st.success(f"Proyección: S/ {proy:.2f}") if proy <= INGRESOS_TOTALES else st.error(f"Proyección: S/ {proy:.2f}")

    st.subheader("📂 Registro Completo")
    st.dataframe(df_filtrado, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
