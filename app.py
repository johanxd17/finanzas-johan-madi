import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Log de Combate - Johan", layout="wide")

# --- CONFIGURACIÓN DE INGRESOS ---
MI_SUELDO = 960.00
SUELDO_MADI = 570.00
AHORRO_YAPE = 107.14
TOTAL_INGRESOS = MI_SUELDO + SUELDO_MADI + AHORRO_YAPE

st.title("💸 Registro de Gastos en Tiempo Real")
st.write(f"Ciclo: 11 Abr - 10 May | **Ingreso Total Disponible: S/ {TOTAL_INGRESOS:.2f}**")

# --- BASE DE DATOS (Sesión con TODOS los Gastos Fijos) ---
if 'mis_gastos' not in st.session_state:
    st.session_state.mis_gastos = [
        {'ID': 0, 'Fecha': '2026-04-11', 'Concepto': 'Pensión Madi', 'Monto': 690.00, 'Categoría': 'Estudios', 'Banco': 'BCP'},
        {'ID': 1, 'Fecha': '2026-04-11', 'Concepto': 'Cuota iPhone 11/12', 'Monto': 442.21, 'Categoría': 'Fijo', 'Banco': 'BCP'},
        {'ID': 2, 'Fecha': '2026-04-11', 'Concepto': 'Cuota Switch 2/12', 'Monto': 164.58, 'Categoría': 'Fijo', 'Banco': 'BCP'},
        {'ID': 3, 'Fecha': '2026-04-28', 'Concepto': 'Spotify Premium', 'Monto': 26.90, 'Categoría': 'Fijo', 'Banco': 'Interbank'},
        {'ID': 4, 'Fecha': '2026-04-11', 'Concepto': 'Préstamo BBVA', 'Monto': 174.12, 'Categoría': 'Fijo', 'Banco': 'BBVA'},
    ]

# --- PROCESAMIENTO ---
df = pd.DataFrame(st.session_state.mis_gastos)
total_gastos = df['Monto'].sum()
saldo_restante = TOTAL_INGRESOS - total_gastos
porcentaje_uso = (total_gastos / TOTAL_INGRESOS) * 100

# --- INDICADORES DE ESTADO ---
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("Gastos Totales", f"S/ {total_gastos:.2f}")
c2.metric("Saldo para el Mes", f"S/ {saldo_restante:.2f}", delta=f"{saldo_restante:.2f}")
c3.metric("Capacidad de Pago", f"{porcentaje_uso:.1f}%")

# --- ALERTA DE SEGURIDAD FINANCIERA ---
if total_gastos > TOTAL_INGRESOS:
    st.error(f"🚨 **¡SOBRECARGA!** Johan, los gastos (S/ {total_gastos:.2f}) superan tus ingresos. Faltan S/ {abs(saldo_restante):.2f}")
    st.info("🐱 **Horu dice:** 'Estamos en déficit. ¡Toca ajustar cinturones!'")
elif porcentaje_uso > 90:
    st.warning(f"⚠️ **RIESGO ALTO:** Solo quedan S/ {saldo_restante:.2f} para todo el mes.")
    st.info("🐱 **Horu dice:** 'Casi todo el sueldo ya tiene dueño. ¡Prohibido gastar en tonterías!'")

# --- FORMULARIO PARA AÑADIR ---
with st.expander("➕ REGISTRAR NUEVO GASTO"):
    with st.form("add_form"):
        col_f, col_c = st.columns(2)
        f_val = col_f.date_input("Fecha", datetime.now())
        c_val = col_c.text_input("Concepto")
        
        c_m, c_cat, c_b = st.columns(3)
        m_val = c_m.number_input("Monto (S/)", min_value=0.0)
        cat_val = c_cat.selectbox("Categoría", ["Comida", "Pasajes", "Madi", "Hogar", "Otros"])
        b_val = c_b.selectbox("Banco", ["BCP", "BBVA", "Interbank"])
        
        if st.form_submit_button("Guardar"):
            new_id = max([g['ID'] for g in st.session_state.mis_gastos]) + 1 if st.session_state.mis_gastos else 0
            st.session_state.mis_gastos.append({
                'ID': new_id, 'Fecha': str(f_val), 'Concepto': c_val, 'Monto': m_val, 'Categoría': cat_val, 'Banco': b_val
            })
            st.rerun()

# --- PANEL DE EDICIÓN Y ELIMINACIÓN ---
with st.expander("🛠️ EDITAR O ELIMINAR GASTOS"):
    st.write("Selecciona un gasto para borrarlo de la lista:")
    if st.session_state.mis_gastos:
        # Lista para el selector
        opciones_edit = {f"{g['Concepto']} - S/ {g['Monto']} ({g['Banco']})": g['ID'] for g in st.session_state.mis_gastos}
        seleccionado = st.selectbox("Gasto a eliminar:", options=list(opciones_edit.keys()))
        
        if st.button("🗑️ Eliminar permanentemente"):
            id_borrar = opciones_edit[seleccionado]
            st.session_state.mis_gastos = [g for g in st.session_state.mis_gastos if g['ID'] != id_borrar]
            st.success("Gasto eliminado. El presupuesto se ha recalculado.")
            st.rerun()

# --- VISUALIZACIÓN FINAL ---
st.divider()
col_t, col_g = st.columns([2, 1])
with col_t:
    st.subheader("📋 Resumen de Cuentas")
    st.dataframe(df.sort_values(by='Fecha')[['Fecha', 'Concepto', 'Monto', 'Banco']], use_container_width=True)
with col_g:
    st.subheader("🏢 Deuda por Entidad")
    fig = px.pie(df, values='Monto', names='Banco', 
                 color_discrete_map={'BCP':'#16335E', 'BBVA':'#004481', 'Interbank':'#00B140'})
    st.plotly_chart(fig, use_container_width=True)
