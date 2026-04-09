import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Johan & Madi - Live", layout="wide")

# 1. TU ID DE EXCEL
SHEET_ID = "1ju4BGM20CCdDnPNLzSPv5RWjlBi01uq7XO-6x-KnsWc" 

# 2. TUS INGRESOS
TOTAL_INGRESOS = 1090.00 + 570.00 + 107.14

# --- LÍNEA CORREGIDA AQUÍ ---
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

st.title("🛡️ Panel de Control Financiero")

try:
    # Carga de datos
    df = pd.read_csv(url)
    df['Monto'] = pd.to_numeric(df['Monto'])
    
    total_gastos = df['Monto'].sum()
    saldo = TOTAL_INGRESOS - total_gastos

    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos", f"S/ {TOTAL_INGRESOS:.2f}")
    c2.metric("Gastos", f"S/ {total_gastos:.2f}")
    
    # Color dinámico para el saldo
    st.sidebar.markdown(f"### Saldo Actual: S/ {saldo:.2f}")
    
    c3.metric("Saldo Restante", f"S/ {saldo:.2f}", delta=f"{saldo:.2f}")

    st.divider()

    # Visualización
    col_a, col_b = st.columns([1.5, 1])
    with col_a:
        st.subheader("📋 Movimientos (Edita en Google Sheets)")
        st.dataframe(df, use_container_width=True)
    
    with col_b:
        st.subheader("📊 Distribución")
        fig = px.pie(df, values='Monto', names='Banco', hole=0.4, 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.warning("⚠️ Esperando conexión con Google Sheets...")
    st.info("Asegúrate de que en el Excel hayas dado a 'Compartir' -> 'Cualquier persona con el enlace' (Lector).")
