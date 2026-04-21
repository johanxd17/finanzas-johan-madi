import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURACIÓN E INGRESOS ---
st.set_page_config(page_title="Sistema IA Financiera - Johan & Madi", layout="wide", page_icon="🏦")

# --- 1.5 CABECERA MAQUETADA Y CENTRADA ---
st.write("") 

m_izq, col_logo, col_titulo, m_der = st.columns([1, 1, 5, 1])

with col_logo:
    st.image("HORU.jpeg", use_container_width=True)
    st.markdown('<style>img {border-radius: 15px;}</style>', unsafe_allow_html=True)

with col_titulo:
    st.markdown("<h1 style='color: #2E86C1; margin-top: 10px; font-size: 2.2em;'>🛡️ Panel de Control Financiero Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.1em; color: #808B96; margin-top: -10px;'>Gestión de Activos y Control de Riesgos | <b>Johan & Madi</b></p>", unsafe_allow_html=True)

st.divider()

# --- 2. CONFIGURACIÓN DE INGRESOS ---
MI_SUELDO = 960.00
SUELDO_MADI = 560.00
AHORRO_YAPE = 107.14
TOTAL_INGRESOS = MI_SUELDO + SUELDO_MADI + AHORRO_YAPE
INGRESOS_TOTALES = TOTAL_INGRESOS

# Botón de actualización en el Sidebar
if st.sidebar.button('🔄 Sincronizar Datos'):
    st.cache_data.clear()
    st.rerun()

# --- 3. CONEXIÓN A GOOGLE SHEETS ---
SHEET_ID = "1ju4BGM20CCdDnPNLzSPv5RWjlBi01uq7XO-6x-KnsWc"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

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
    # 1. Carga de datos y limpieza de filas vacías
    df = pd.read_csv(url)
    df.columns = [c.strip() for c in df.columns]
    df = df.dropna(subset=['Concepto', 'Monto'], how='all')

    # 2. LIMPIEZA DE DATOS (Para evitar el error de comparación)
    df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
    
    # 3. NORMALIZACIÓN DE BANCOS (Pone todo en mayúsculas y quita espacios)
    if 'Banco' in df.columns:
        df['Banco'] = df['Banco'].fillna('S/B').astype(str).str.strip().str.upper()
        
        # Obtenemos la lista de bancos únicos ya limpios
        lista_bancos = sorted(df['Banco'].unique())
        
        # Filtro en el Sidebar
        bancos_seleccionados = st.sidebar.multiselect(
            "🏦 Seleccionar Bancos:",
            options=lista_bancos,
            default=lista_bancos  # Por defecto marca todos para que veas tus datos
        )
        
        # Aplicamos el filtro
        df = df[df['Banco'].isin(bancos_seleccionados)]

    # 4. Normalización de Responsables (Johan, Madi, Johan y Madi)
    if 'Responsable' in df.columns:
        df['Responsable'] = df['Responsable'].fillna('No asignado').astype(str).str.strip()

    # --- 5. CÁLCULOS Y MÉTRICAS ---
    gastos_totales = df['Monto'].sum()
    saldo_actual = INGRESOS_TOTALES - gastos_totales

    if not df.empty:
        m1, m2, m3 = st.columns(3)
        m1.metric("Ingresos Totales", f"S/ {INGRESOS_TOTALES:,.2f}")
        m2.metric("Gasto Acumulado", f"S/ {gastos_totales:,.2f}")
        m3.metric("Fondo de Maniobra", f"S/ {saldo_actual:,.2f}")
        
        st.divider()
        # AQUÍ DEBEN IR TUS GRÁFICOS (Gráfico de torta, etc.)
    else:
        st.warning("No hay datos para los bancos seleccionados. Revisa el filtro lateral.")

except Exception as e:
    st.error(f"Error en el sistema: {e}")

    # --- 4. TERMÓMETRO DE SALUD ---
    st.write("### 🌡️ Nivel de Salud Financiera")
    st.progress(min(porcentaje_gastado, 1.0))
    
    if porcentaje_gastado < 0.7:
        st.success(f"✅ ESTADO SALUDABLE: Has gastado el {porcentaje_gastado:.1%}")
    elif porcentaje_gastado < 0.9:
        st.warning(f"⚠️ PRECAUCIÓN: Has gastado el {porcentaje_gastado:.1%}")
    else:
        st.error(f"🚨 ALERTA CRÍTICA: Has gastado el {porcentaje_gastado:.1%}")

    st.divider()

    # --- 5. BLOQUE DE ANÁLISIS ---
    st.subheader("📊 Análisis de Movimientos")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.write("**💳 Gestión por Bancos**")
        fig_banco = px.pie(df, values='Monto', names='Banco', hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_banco, use_container_width=True)

    with c2:
        st.write("**👥 Johan vs Madi**")
        if 'Responsable' in df.columns:
            fig_resp = px.pie(df, values='Monto', names='Responsable', hole=0.4, color_discrete_sequence=['#2E86C1', '#F39C12'])
            st.plotly_chart(fig_resp, use_container_width=True)

    with c3:
        st.write("**🏷️ Gastos por Categoría**")
        fig_cat = px.bar(df.groupby(col_cat)['Monto'].sum().reset_index(), x=col_cat, y='Monto', color=col_cat)
        st.plotly_chart(fig_cat, use_container_width=True)

    # --- NUEVA SECCIÓN: GRÁFICO DE TENDENCIA ---
    st.divider()
    st.subheader("📈 Tendencia de Gasto en el Tiempo")
    
    if not df.empty and df['Fecha'].notnull().any():
        df_linea = df.groupby(df['Fecha'].dt.date)['Monto'].sum().reset_index()
        df_linea.columns = ['Fecha_Corta', 'Total_Gasto']
        fig_tendencia = px.line(df_linea, x='Fecha_Corta', y='Total_Gasto', 
                                title="Evolución de Salidas de Efectivo por Día",
                                markers=True)
        fig_tendencia.update_layout(xaxis_title="Día", yaxis_title="Soles Gastados")
        st.plotly_chart(fig_tendencia, use_container_width=True)
    else:
        st.info("No hay datos de fecha válidos para generar la tendencia.")

    # --- 6. ANALISTA PREDICTIVO (IA) ---
    st.divider()
    st.subheader("🤖 Oráculo IA")

    if not df.empty:
        df_variables = df[df['Monto'] < 200] 
        df_fijos = df[df['Monto'] >= 200]
    
        gastos_variables_totales = df_variables['Monto'].sum()
        gastos_fijos_totales = df_fijos['Monto'].sum()

        dias_transcurridos = (datetime.now() - df['Fecha'].min()).days + 1
        promedio_variable_diario = gastos_variables_totales / max(dias_transcurridos, 1)
        proyeccion_final = (promedio_variable_diario * 30) + gastos_fijos_totales
    
        c_ia1, c_ia2 = st.columns(2)
        with c_ia1:
            if proyeccion_final > INGRESOS_TOTALES:
                st.error(f"La IA estima un gasto de S/ {proyeccion_final:.2f} a fin de mes. ¡Cuidado con los excedentes!")
            else:
                st.success(f"Proyección: S/ {proyeccion_final:.2f}. ¡Todo bajo control, Johan!")

    # --- 7. REGISTRO MAESTRO ---
    st.subheader("📂 Registro Completo de Excel")
    df_ver = df.copy()
    df_ver['Fecha'] = df_ver['Fecha'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_ver.sort_values(by='Fecha', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Error de conexión o de datos: {e}")
