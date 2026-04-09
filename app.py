import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Johan - Control de Gastos Reales", layout="wide", page_icon="📉")

# --- CONFIGURACIÓN DE INGRESOS ---
MI_SUELDO = 1090.00
SUELDO_MADI = 570.00
AHORRO_YAPE = 107.14
TOTAL_INGRESOS = MI_SUELDO + SUELDO_MADI + AHORRO_YAPE

# --- CONEXIÓN A TU GOOGLE SHEETS ---
# Ya puse tu ID real aquí
SHEET_ID = "1ju4BGM20CCdDnPNLzSPv5RWjlBi01uq7XO-6x-KnsWc"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

st.markdown("<h1 style='text-align: center; color: #2E86C1;'>🛡️ Panel de Control Financiero</h1>", unsafe_allow_html=True)

try:
    # CARGA DE DATOS DESDE EXCEL
    df = pd.read_csv(url)
    df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
    
    total_gastos = df['Monto'].sum()
    saldo_disponible = TOTAL_INGRESOS - total_gastos

    # --- MÉTRICAS PRINCIPALES (TU DISEÑO) ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos Totales", f"S/ {TOTAL_INGRESOS:.2f}")
    c1.caption("Sueldos + Ahorro Yape")

    c2.metric("Gastos Totales", f"S/ {total_gastos:.2f}")

    color_texto = "#27AE60" if saldo_disponible > 0 else "#C0392B"
    c3.markdown(f"### Saldo para el Mes\n<h2 style='color:{color_texto};'>S/ {saldo_disponible:.2f}</h2>", unsafe_allow_html=True)

    st.divider()

    # --- INFORMACIÓN DE USO ---
    st.info("💡 **Dato de Ingeniero:** Para registrar o quitar gastos, edita directamente tu archivo 'Finanzas-Johan-Madi' en Google Sheets. Los cambios se verán aquí al refrescar.")

    # --- SECCIÓN DE VISUALIZACIÓN (TU DISEÑO) ---
    col_list, col_chart = st.columns([1.5, 1])

    with col_list:
        st.subheader("📋 Detalle de Movimientos")
        # Mostramos la tabla tal cual viene del Excel
        st.dataframe(df[['Fecha', 'Concepto', 'Monto', 'Banco']], use_container_width=True)
    
    with col_chart:
        st.subheader("📊 Gastos por Banco")
        if total_gastos > 0:
            fig = px.pie(df, values='Monto', names='Banco', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Agrega datos en el Excel para ver el gráfico.")

except Exception as e:
    st.error("⚠️ Error de conexión. Revisa que tu Google Sheets tenga datos y sea público.")
