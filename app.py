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
MI_SUELDO = 1000.00
SUELDO_MADI = 580.00
SOBRANTE = 1113.17
INGRESOS_TOTALES = MI_SUELDO + SUELDO_MADI + SOBRANTE

FECHAS_BANCOS = {
    'BCP': [10, 5],
    'BBVA': [10, 5],
    'INTERBANK': [27, 21],
    'SCOTIABANK': [11, 8]
}

# --- SIDEBAR: CONSOLA DE PAGOS ---
st.sidebar.divider()
st.sidebar.subheader("✅ Confirmar Pagos realizados")
pagos_confirmados = {}
for banco in FECHAS_BANCOS.keys():
    pagos_confirmados[banco] = st.sidebar.checkbox(f"Pagué {banco}", key=f"pay_{banco}")

# --- FILTRO DE PRIORIDAD DE PAGOS ---
st.sidebar.divider()
st.sidebar.subheader("🎯 Enfoque de Pagos")
fase_pago = st.sidebar.radio(
    "Ver vencimientos de:",
    ["Pros (BCP/BBVA - 05 May)", "Siguiente (Interbank - 21 May)", "Futuro (Scotiabank - Jun)", "Ver Todo"]
)

# --- 3. CONEXIÓN A GOOGLE SHEETS ---
SHEET_ID = "1ju4BGM20CCdDnPNLzSPv5RWjlBi01uq7XO-6x-KnsWc"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

def clasificador_ia(concepto):
    if pd.isna(concepto): return "❓ Otros"
    concepto = str(concepto).lower().strip()
    if any(word in concepto for word in ['menu', 'comida', 'ceviche', 'pizza', 'moka']): return "🍱 Alimentación"
    if any(word in concepto for word in ['pasaje', 'bus', 'taxi', 'gasolina']): return "🚗 Transporte"
    if any(word in concepto for word in ['cuota', 'iphone', 'prestamo', 'banco']): return "💳 Deudas/Fijos"
    if any(word in concepto for word in ['cine', 'netflix', 'juego', 'switch']): return "🎮 Diversión"
    return "❓ Otros"

try:
    df = pd.read_csv(url)
    df.columns = [c.strip() for c in df.columns]

    # --- NORMALIZACIÓN ---
    df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce').fillna(datetime.now())
    if 'Responsable' in df.columns:
        df['Responsable'] = df['Responsable'].astype(str).str.strip().str.capitalize()
    if 'Banco' in df.columns:
        df['Banco'] = df['Banco'].astype(str).str.strip().str.upper()

    # --- FILTRO HISTÓRICO ---
    st.sidebar.divider()
    st.sidebar.subheader("📅 Ver Historial")
    if 'Ciclo' in df.columns:
        meses_disponibles = df['Ciclo'].dropna().unique().tolist()
        mes_seleccionado = st.sidebar.selectbox("Seleccionar Periodo:", ["Ciclo Actual"] + meses_disponibles)
    else:
        mes_seleccionado = "Ciclo Actual"

    if mes_seleccionado != "Ciclo Actual":
        df_base = df[df['Ciclo'] == mes_seleccionado]
        fase_display = f"Histórico: {mes_seleccionado}"
    else:
        df_base = df
        fase_display = "Ciclo Actual"

    if fase_pago == "Pros (BCP/BBVA - 05 May)":
        df_filtrado = df_base[df_base['Banco'].isin(['BCP', 'BBVA'])]
    elif fase_pago == "Siguiente (Interbank - 21 May)":
        df_filtrado = df_base[df_base['Banco'] == 'INTERBANK']
    elif fase_pago == "Futuro (Scotiabank - Jun)":
        df_filtrado = df_base[df_base['Banco'] == 'SCOTIABANK']
    else:
        df_filtrado = df_base

    # --- MÉTRICAS ---
    gastos_totales_ciclo = df_base['Monto'].sum()
    gastos_vista_actual = df_filtrado['Monto'].sum()
    saldo_proyectado = INGRESOS_TOTALES - gastos_totales_ciclo
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Ingresos Totales", f"S/ {INGRESOS_TOTALES:.2f}")
    m2.metric(f"Total en Vista", f"S/ {gastos_vista_actual:.2f}")
    m3.metric("Saldo Proyectado", f"S/ {saldo_proyectado:.2f}")

    # --- METAS DE AHORRO ---
    st.divider()
    st.subheader("🎯 Metas de Ahorro")
    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        meta_obj = 2000.00
        ahorro_disp = max(0, saldo_proyectado)
        st.write(f"**Fondo de Emergencia** (Meta: S/ {meta_obj})")
        st.progress(min(ahorro_disp / meta_obj, 1.0))
        st.write(f"Proyectado: S/ {ahorro_disp:.2f}")
    with col_meta2:
        if (gastos_vista_actual/INGRESOS_TOTALES) > 0.9: st.warning("⚠️ Margen crítico.")
        else: st.success("✨ Gestión bajo control.")

    # --- RECORDATORIOS DE BANCOS ---
    st.subheader("🔔 Recordatorios de Facturación")
    hoy = datetime.now().day
    columnas_alertas = st.columns(len(FECHAS_BANCOS))
    for i, (banco, fechas) in enumerate(FECHAS_BANCOS.items()):
        dia_corte, dia_pago = fechas
        with columnas_alertas[i]:
            if pagos_confirmados.get(banco): st.success(f"**{banco}**\n\n✅ Pagado")
            elif hoy <= dia_pago:
                faltan = dia_pago - hoy
                if faltan <= 5: st.error(f"**{banco}**\n\n🚨 {faltan} días")
                else: st.info(f"**{banco}**\n\n{faltan} días")
            else: st.warning(f"**{banco}**\n\nCorte: {dia_corte}")

    # --- ANÁLISIS GRÁFICO ---
    st.divider()
    st.subheader("📊 Análisis de Movimientos")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.write("**💳 Gestión por Bancos**")
        st.plotly_chart(px.pie(df_filtrado, values='Monto', names='Banco', hole=0.4), use_container_width=True)
    with c2:
        st.write("**👥 Johan vs Madi**")
        if 'Responsable' in df_filtrado.columns:
            st.plotly_chart(px.pie(df_filtrado, values='Monto', names='Responsable', hole=0.4), use_container_width=True)
    with c3:
        st.write("**🏷️ Gastos por Categoría**")
        df_filtrado['Cat'] = df_filtrado['Concepto'].apply(clasificador_ia)
        df_cat_graf = df_filtrado.groupby('Cat')['Monto'].sum().reset_index()
        fig_cat = px.bar(df_cat_graf, x='Cat', y='Monto', color='Cat')
        fig_cat.update_layout(showlegend=False)
        st.plotly_chart(fig_cat, use_container_width=True)

    # --- CONTROL DE COMPROMISOS (FORMATO CORREGIDO) ---
    st.divider()
    st.subheader("🎯 Control de Compromisos")
    cuotas_list = [
        {"Compromiso": "PRÉSTAMO BBVA (CANCELACIÓN TOTAL)", "Monto": 322.58, "Vence": "05-May", "Estado": "POR LIQUIDAR 🏁"},
        {"Compromiso": "Nintendo Switch 2", "Monto": 164.58, "Vence": "05-May", "Estado": "Falta pagar"},
        {"Compromiso": "Powerpay (iPhones)", "Monto": 442.21, "Vence": "11-May", "Estado": "Falta pagar"}
    ]
    # Formateamos el monto para evitar ceros extras
    df_cuotas = pd.DataFrame(cuotas_list)
    df_cuotas['Monto'] = df_cuotas['Monto'].map('{:,.2f}'.format)
    st.table(df_cuotas)

    # --- ORÁCULO IA (SIN ERROR DE DeltaGenerator) ---
    st.divider()
    st.subheader("🤖 Oráculo IA")
    proy = (gastos_totales_ciclo / datetime.now().day) * 30 if datetime.now().day > 0 else 0
    if proy <= INGRESOS_TOTALES:
        st.success(f"Proyección: S/ {proy:.2f}")
    else:
        st.error(f"Proyección: S/ {proy:.2f}")

    st.subheader("📂 Registro Maestro")
    st.dataframe(df_filtrado, use_container_width=True)

except Exception as e:
    st.error(f"Error técnico: {e}")
