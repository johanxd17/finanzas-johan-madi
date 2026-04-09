import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURACIÓN E INGRESOS ---
st.set_page_config(page_title="Sistema de Inteligencia Financiera - Johan & Madi", layout="wide", page_icon="🏦")
# --- 1.5 CABECERA MAQUETADA (IMAGEN + TÍTULO) ---

# Creamos dos columnas: una estrecha para el logo (1) y una ancha para el título (4)
col_logo, col_titulo = st.columns([1, 4])

with col_logo:
    # Subimos la imagen. use_container_width=True la ajusta al ancho de la columna 1.
    # Si quieres que sea más pequeña, usa width=150 (en píxeles) en lugar de use_container_width.
    st.image("banner.jpg", use_container_width=True) 

with col_titulo:
    # Ponemos el título al costado. Quitamos el 'text-align: center' para que alinee a la izquierda.
    st.markdown("<h1 style='color: #2E86C1; margin-top: 0px;'>🛡️ Panel de Control Financiero Pro</h1>", unsafe_allow_html=True)
    st.write("Bienvenido, Johan. Gestión de Activos y Control de Riesgos en tiempo real.")

st.divider() # Una línea divisoria para separar la cabecera de las métricas

SHEET_ID = "1ju4BGM20CCdDnPNLzSPv5RWjlBi01uq7XO-6x-KnsWc"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# Tus ingresos reales
INGRESOS_TOTALES = 1090.00 + 570.00 + 107.14

# --- 2. IA DE CLASIFICACIÓN (NLP) ---
def clasificador_ia(concepto):
    concepto = str(concepto).lower()
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
    df = pd.read_csv(url)
    df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    
    # Auto-llenado de categorías si están vacías (Tu IA interna)
    col_cat = [c for c in df.columns if 'Categor' in c][0]
    df[col_cat] = df.apply(lambda x: clasificador_ia(x['Concepto']) if pd.isna(x[col_cat]) or x[col_cat] == '' else x[col_cat], axis=1)

    # --- 3. CABECERA Y MÉTRICAS ---
    st.markdown("<h1 style='text-align: center; color: #2E86C1;'>🛡️ Panel de Control Financiero Pro</h1>", unsafe_allow_html=True)
    
    gastos_totales = df['Monto'].sum()
    saldo_actual = INGRESOS_TOTALES - gastos_totales
    porcentaje_gastado = (gastos_totales / INGRESOS_TOTALES) if INGRESOS_TOTALES > 0 else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("Ingresos Totales", f"S/ {INGRESOS_TOTALES:.2f}")
    m2.metric("Gasto Acumulado", f"S/ {gastos_totales:.2f}", delta=f"{porcentaje_gastado:.1%}", delta_color="inverse")
    m3.metric("Fondo de Maniobra", f"S/ {saldo_actual:.2f}")

    # --- 4. TERMÓMETRO DE SALUD (BRILLANTE) ---
    st.write("### 🌡️ Nivel de Salud Financiera")
    
    # La barra de progreso se mantiene para ver el avance visual
    st.progress(min(porcentaje_gastado, 1.0))
    
    # Aquí aplicamos el "Brillo" según el nivel de gasto
    if porcentaje_gastado < 0.7:
        st.success(f"✅ ESTADO SALUDABLE: Has gastado el {porcentaje_gastado:.1%}")
    elif porcentaje_gastado < 0.9:
        st.warning(f"⚠️ PRECAUCIÓN: Has gastado el {porcentaje_gastado:.1%}")
    else:
        st.error(f"🚨 ALERTA CRÍTICA: Has gastado el {porcentaje_gastado:.1%}")

    st.divider()

    # --- 5. BLOQUE DE ANÁLISIS (BANCOS, PERSONAS, CATEGORÍAS) ---
    st.subheader("📊 Análisis de Movimientos")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.write("**💳 Gestión por Bancos**")
        # Aquí controlas BCP, BBVA, Interbank y Scotia
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

    # --- NUEVA SECCIÓN: GRÁFICO DE TENDENCIA (TÉCNICO) ---
    st.divider()
    st.subheader("📈 Tendencia de Gasto en el Tiempo")
    
    # Preparación de datos para la línea
    if not df.empty and df['Fecha'].notnull().any():
        df_linea = df.groupby(df['Fecha'].dt.date)['Monto'].sum().reset_index()
        df_linea.columns = ['Fecha_Corta', 'Total_Gasto']
        
        # Creamos el gráfico de líneas (El look de terminal financiera)
        fig_tendencia = px.line(df_linea, x='Fecha_Corta', y='Total_Gasto', 
                                title="Evolución de Salidas de Efectivo por Día",
                                markers=True) # Añade puntitos en cada día
        
        # Mejoras visuales al gráfico
        fig_tendencia.update_layout(xaxis_title="Día", yaxis_title="Soles Gastados")
        
        st.plotly_chart(fig_tendencia, use_container_width=True)
    else:
        st.info("No hay datos de fecha válidos para generar la tendencia.")

    # --- 6. ANALISTA PREDICTIVO (IA) ---
    st.divider()
    st.subheader("🤖 Oráculo IA")
    if not df.empty:
        dias_mes = (datetime.now() - df['Fecha'].min()).days + 1
        proyeccion = (gastos_totales / max(dias_mes, 1)) * 30
        
        c_ia1, c_ia2 = st.columns(2)
        with c_ia1:
            if proyeccion > INGRESOS_TOTALES:
                st.error(f"La IA estima un gasto de S/ {proyeccion:.2f} a fin de mes. ¡Superarás tus ingresos!")
            else:
                st.success(f"La IA estima un gasto de S/ {proyeccion:.2f}. Vas por buen camino, Johan.")
        
        with c_ia2:
            st.info(f"Ahorro estimado si mantienes el ritmo: **S/ {max(0, INGRESOS_TOTALES - proyeccion):.2f}**")

    # --- 7. REGISTRO MAESTRO ---
    st.subheader("📂 Registro Completo de Excel")
    st.dataframe(df.sort_values(by='Fecha', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Error de conexión: {e}")
