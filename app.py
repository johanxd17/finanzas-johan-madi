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
    try:
        st.image("HORU.jpeg", use_container_width=True)
        st.markdown('<style>img {border-radius: 15px;}</style>', unsafe_allow_html=True)
    except:
        st.write("🏢")

with col_titulo:
    st.markdown("<h1 style='color: #2E86C1; margin-top: 10px; font-size: 2.2em;'>🛡️ Panel de Control Financiero Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.1em; color: #808B96; margin-top: -10px;'>Gestión de Activos y Control de Riesgos | <b>Johan & Madi</b></p>", unsafe_allow_html=True)

st.divider()

# --- 2. CONFIGURACIÓN DE INGRESOS ---
MI_SUELDO = 960.00
SUELDO_MADI = 560.00
TOTAL_INGRESOS = MI_SUELDO + SUELDO_MADI 
INGRESOS_TOTALES = TOTAL_INGRESOS

# Formato: 'BANCO': [Día de Corte, Día de Pago]
FECHAS_BANCOS = {
    'BCP': [10, 5],
    'BBVA': [10, 5],
    'INTERBANK': [27, 21],
    'SCOTIABANK': [11, 8]
}

# --- 1. CONSOLA DE PAGOS EN EL SIDEBAR ---
st.sidebar.divider()
st.sidebar.subheader("✅ Confirmar Pagos realizados")
st.sidebar.write("*(Marca si ya pagaste la cuota del mes)*")
    
pagos_confirmados = {}
for banco in FECHAS_BANCOS.keys():
    pagos_confirmados[banco] = st.sidebar.checkbox(f"Pagué {banco}", key=f"pay_{banco}")

# --- FILTRO DE PRIORIDAD DE PAGOS ---
st.sidebar.divider()
st.sidebar.subheader("🎯 Enfoque de Pagos")
fase_pago = st.sidebar.radio(
    "Ver vencimientos de:",
    ["Próximos (BCP/BBVA - 05 May)", "Siguiente (Interbank - 21 May)", "Futuro (Scotiabank - Jun)", "Ver Todo"]
)

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
    # 1. Carga de datos
    df = pd.read_csv(url)
    df.columns = [c.strip() for c in df.columns]

    # 3. Normalización
    if 'Banco' in df.columns:
        df['Banco'] = df['Banco'].astype(str).str.strip().str.upper()
    if 'Responsable' in df.columns:
        df['Responsable'] = df['Responsable'].astype(str).str.strip().str.capitalize()

    df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)

    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce', dayfirst=True)
        df['Fecha'] = df['Fecha'].fillna(datetime.now())

    # 6. Auto-llenado de categorías
    columnas_categoria = [c for c in df.columns if 'Categor' in c]
    if columnas_categoria:
        col_cat = columnas_categoria[0]
        df[col_cat] = df.apply(lambda x: clasificador_ia(x['Concepto']) if pd.isna(x[col_cat]) or str(x[col_cat]).strip() == '' else x[col_cat], axis=1)
    else:
        col_cat = "Categoría"
        df[col_cat] = df['Concepto'].apply(clasificador_ia)

    # --- 3. MÉTRICAS DINÁMICAS (ARREGLADO) ---
    gastos_totales_reales = df['Monto'].sum() # Para el termómetro
    porcentaje_gastado = (gastos_totales_reales / INGRESOS_TOTALES) if INGRESOS_TOTALES > 0 else 0

    if fase_pago == "Próximos (BCP/BBVA - 05 May)":
        df_filtrado = df[df['Banco'].isin(['BCP', 'BBVA'])]
    elif fase_pago == "Siguiente (Interbank - 21 May)":
        df_filtrado = df[df['Banco'] == 'INTERBANK']
    elif fase_pago == "Futuro (Scotiabank - Jun)":
        df_filtrado = df[df['Banco'] == 'SCOTIABANK']
    else:
        df_filtrado = df

    gastos_fase = df_filtrado['Monto'].sum()
    saldo_proyectado = INGRESOS_TOTALES - gastos_fase
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Ingresos Totales", f"S/ {INGRESOS_TOTALES:.2f}")
    m2.metric(f"Total {fase_pago.split(' ')[0]}", f"S/ {gastos_fase:.2f}")
    m3.metric("Saldo tras estos pagos", f"S/ {saldo_proyectado:.2f}")
    
    # --- SECCIÓN FUTURA: METAS DE AHORRO ---
    st.divider()
    st.subheader("🎯 Metas de Ahorro")

    col_meta1, col_meta2 = st.columns(2)

    with col_meta1:
        meta_objetivo = 2000.00  # Ejemplo: Fondo de Emergencia
        ahorro_actual = saldo_actual if saldo_actual > 0 else 0
        progreso = min(ahorro_actual / meta_objetivo, 1.0)
    
        st.write(f"**Fondo de Emergencia** (Meta: S/ {meta_objetivo})")
        st.progress(progreso)
        st.write(f"Faltan: S/ {meta_objetivo - ahorro_actual:.2f}")

     with col_meta2:
         # Aquí podrías poner consejos basados en tu gasto
         if porcentaje_gastado > 0.9:
             st.warning("Este mes el ahorro es difícil. Prioriza cubrir deudas.")
         else:
             st.success("¡Buen ritmo! Podrías destinar el sobrante a tu meta.")
    
    # --- 4. RECORDATORIOS DE FACTURACIÓN ---
    st.subheader("🔔 Recordatorios de Facturación")
    hoy = datetime.now()
    dia_actual = hoy.day
    columnas_alertas = st.columns(len(FECHAS_BANCOS))
    
    for i, (banco, fechas) in enumerate(FECHAS_BANCOS.items()):
        dia_corte, dia_pago = fechas
        with columnas_alertas[i]:
            if pagos_confirmados.get(banco):
                st.success(f"**{banco}**\n\n✅ Pago Confirmado")
            else:
                if dia_actual <= dia_pago:
                    dias_faltantes = dia_pago - dia_actual
                    if dias_faltantes <= 5:
                        st.error(f"**{banco}**\n\n¡Pagar en {dias_faltantes} días!")
                    else:
                        st.info(f"**{banco}**\n\nFaltan {dias_faltantes} días.")
                else:
                    st.warning(f"**{banco}**\n\nCierre el día {dia_corte}")

    # --- 5. TERMÓMETRO DE SALUD ---
    st.write("### 🌡️ Nivel de Salud Financiera")
    st.progress(min(porcentaje_gastado, 1.0))
    if porcentaje_gastado < 0.7:
        st.success(f"✅ ESTADO SALUDABLE: Has gastado el {porcentaje_gastado:.1%}")
    elif porcentaje_gastado < 0.9:
        st.warning(f"⚠️ PRECAUCIÓN: Has gastado el {porcentaje_gastado:.1%}")
    else:
        st.error(f"🚨 ALERTA CRÍTICA: Has gastado el {porcentaje_gastado:.1%}")

    st.divider()

    # --- 6. BLOQUE DE ANÁLISIS ---
    st.subheader("📊 Análisis de Movimientos")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.write("**💳 Gestión por Bancos**")
        fig_banco = px.pie(df_filtrado, values='Monto', names='Banco', hole=0.4)
        st.plotly_chart(fig_banco, use_container_width=True)
    with c2:
        st.write("**👥 Johan vs Madi**")
        if 'Responsable' in df_filtrado.columns:
            fig_resp = px.pie(df_filtrado, values='Monto', names='Responsable', hole=0.4)
            st.plotly_chart(fig_resp, use_container_width=True)
    with c3:
        st.write("**🏷️ Gastos por Categoría**")
        # Agrupamos y reseteamos el índice para Plotly
        df_cat_grafico = df_filtrado.groupby(col_cat)['Monto'].sum().reset_index()
        
        # Creamos el gráfico indicando que el color dependa de la categoría
        fig_cat = px.bar(
            df_cat_grafico, 
            x=col_cat, 
            y='Monto', 
            color=col_cat,  # Esto asigna un color diferente a cada barra
            color_discrete_sequence=px.colors.qualitative.Pastel # Paleta colorida y profesional
        )
        
        # Quitamos la leyenda lateral para que no ocupe espacio innecesario
        fig_cat.update_layout(showlegend=False)
        st.plotly_chart(fig_cat, use_container_width=True)

    # --- 7. GRÁFICO DE TENDENCIA ---
    st.divider()
    st.subheader("📈 Tendencia de Gasto en el Tiempo")
    if not df.empty and df['Fecha'].notnull().any():
        df_linea = df.groupby(df['Fecha'].dt.date)['Monto'].sum().reset_index()
        df_linea.columns = ['Fecha_Corta', 'Total_Gasto']
        fig_tendencia = px.line(df_linea, x='Fecha_Corta', y='Total_Gasto', markers=True)
        st.plotly_chart(fig_tendencia, use_container_width=True)

    # --- 8. ANALISTA PREDICTIVO (IA) ---
    st.divider()
    st.subheader("🤖 Oráculo IA")
    if not df.empty:
        df_variables = df[df['Monto'] < 200] 
        df_fijos = df[df['Monto'] >= 200]
        gastos_variables_totales = df_variables['Monto'].sum()
        gastos_fijos_totales = df_fijos['Monto'].sum()
        dias_transcurridos = (datetime.now() - df['Fecha'].min()).days + 1
        promedio_diario = gastos_variables_totales / max(dias_transcurridos, 1)
        proyeccion_final = (promedio_diario * 30) + gastos_fijos_totales
        if proyeccion_final > INGRESOS_TOTALES:
            st.error(f"La IA estima S/ {proyeccion_final:.2f} a fin de mes. ¡Cuidado!")
        else:
            st.success(f"Proyección: S/ {proyeccion_final:.2f}. Todo bajo control.")

    # --- 9. REGISTRO MAESTRO ---
    st.subheader("📂 Registro Completo de Excel")
    df_ver = df.copy()
    df_ver['Fecha'] = df_ver['Fecha'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_ver.sort_values(by='Fecha', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
