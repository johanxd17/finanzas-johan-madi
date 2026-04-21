import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURACIÓN E INGRESOS ---
st.set_page_config(page_title="Sistema IA Financiera - Johan & Madi", layout="wide", page_icon="🏦")

# --- CABECERA ---
st.write("") 
m_izq, col_logo, col_titulo, m_der = st.columns([1, 1, 5, 1])

with col_logo:
    try:
        st.image("HORU.jpeg", use_container_width=True)
        st.markdown('<style>img {border-radius: 15px;}</style>', unsafe_allow_html=True)
    except:
        st.write("🏦")

with col_titulo:
    st.markdown("<h1 style='color: #2E86C1; margin-top: 10px; font-size: 2.2em;'>🛡️ Panel de Control Financiero Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.1em; color: #808B96; margin-top: -10px;'>Gestión de Activos y Control de Riesgos | <b>Johan & Madi</b></p>", unsafe_allow_html=True)

st.divider()

# --- 2. CONFIGURACIÓN DE DINERO ---
INGRESOS_TOTALES = 960.00 + 560.00 + 107.14

# Sidebar
if st.sidebar.button('🔄 Sincronizar Datos'):
    st.cache_data.clear()
    st.rerun()

# URL de Google Sheets
SHEET_ID = "1ju4BGM20CCdDnPNLzSPv5RWjlBi01uq7XO-6x-KnsWc"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# --- IA DE CLASIFICACIÓN ---
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
    # 1. CARGA Y LIMPIEZA INICIAL
    df = pd.read_csv(url)
    df.columns = [c.strip() for c in df.columns]
    
    # Eliminar filas totalmente vacías que suelen quedar al final del Excel
    df = df.dropna(subset=['Concepto', 'Monto'], how='all')

    # 2. LIMPIEZA DE MONTOS (Crucial para evitar errores de comparación)
    df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)

    # 3. FILTRO DE BANCOS EN SIDEBAR
    if 'Banco' in df.columns:
        df['Banco'] = df['Banco'].fillna('S/B').astype(str).str.strip().str.upper()
        lista_bancos = sorted(df['Banco'].unique())
        
        bancos_seleccionados = st.sidebar.multiselect(
            "🏦 Seleccionar Bancos:",
            options=lista_bancos,
            default=lista_bancos
        )
        # Aplicamos el filtro al DataFrame principal
        df = df[df['Banco'].isin(bancos_seleccionados)]

    # 4. NORMALIZACIÓN DE OTROS DATOS
    if 'Responsable' in df.columns:
        df['Responsable'] = df['Responsable'].fillna('No asignado').astype(str).str.strip().str.capitalize()
    
    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce', dayfirst=True)
        df['Fecha'] = df['Fecha'].fillna(datetime.now())

    # 5. CATEGORÍAS
    columnas_categoria = [c for c in df.columns if 'Categor' in c]
    col_cat = columnas_categoria[0] if columnas_categoria else "Categoría"
    
    if col_cat not in df.columns:
        df[col_cat] = df['Concepto'].apply(clasificador_ia)
    else:
        df[col_cat] = df.apply(
            lambda x: clasificador_ia(x['Concepto']) 
            if pd.isna(x[col_cat]) or str(x[col_cat]).strip() == '' 
            else x[col_cat], axis=1
        )

    # --- 6. VISUALIZACIÓN: MÉTRICAS ---
    gastos_totales = df['Monto'].sum()
    saldo_actual = INGRESOS_TOTALES - gastos_totales
    porcentaje_gastado = (gastos_totales / INGRESOS_TOTALES) if INGRESOS_TOTALES > 0 else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("Ingresos Totales", f"S/ {INGRESOS_TOTALES:,.2f}")
    m2.metric("Gasto Acumulado", f"S/ {gastos_totales:,.2f}", 
              delta=f"{porcentaje_gastado:.1%}", delta_color="inverse")
    m3.metric("Fondo de Maniobra", f"S/ {saldo_actual:,.2f}")

    # --- 7. TERMÓMETRO DE SALUD ---
    st.write("### 🌡️ Nivel de Salud Financiera")
    st.progress(min(porcentaje_gastado, 1.0))
    if porcentaje_gastado < 0.7:
        st.success(f"✅ ESTADO SALUDABLE: Has gastado el {porcentaje_gastado:.1%}")
    elif porcentaje_gastado < 0.9:
        st.warning(f"⚠️ PRECAUCIÓN: Has gastado el {porcentaje_gastado:.1%}")
    else:
        st.error(f"🚨 ALERTA CRÍTICA: Has gastado el {porcentaje_gastado:.1%}")

    st.divider()

    # --- 8. ANÁLISIS GRÁFICO ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("💳 Gastos por Banco")
        fig_banco = px.pie(df, values='Monto', names='Banco', hole=0.4, 
                           color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_banco, use_container_width=True)

    with c2:
        st.subheader("👥 Johan vs Madi")
        if 'Responsable' in df.columns:
            fig_resp = px.pie(df, values='Monto', names='Responsable', hole=0.4,
                             color_discrete_sequence=['#2E86C1', '#F39C12'])
            st.plotly_chart(fig_resp, use_container_width=True)

    # --- 9. TENDENCIA Y TABLA ---
    st.divider()
    st.subheader("📈 Historial de Gastos")
    
    # Gráfico de barras por categoría
    fig_cat = px.bar(df.groupby(col_cat)['Monto'].sum().reset_index(), 
                     x=col_cat, y='Monto', color=col_cat, title="Gasto por Categoría")
    st.plotly_chart(fig_cat, use_container_width=True)

    # Tabla Maestra
    st.subheader("📂 Registro Detallado")
    df_ver = df.copy()
    df_ver['Fecha'] = df_ver['Fecha'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_ver.sort_values(by='Monto', ascending=False), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"⚠️ Error cargando datos: {e}")
    st.info("Asegúrate de que tu Excel no tenga filas con errores o formatos extraños.")
