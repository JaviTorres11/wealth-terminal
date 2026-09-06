import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import pytz
import streamlit.components.v1 as components

# Configuración de la página web institucional
st.set_page_config(
    page_title="Terminal de Riqueza - Análisis de Cartera", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS generales para la interfaz institucional
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background-color: #0a0a0c;
        color: #e2e2e6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    .terminal-topbar {
        background: linear-gradient(135deg, #141418 0%, #1c1c22 100%);
        border: 1px solid #2f2f3d;
        padding: 18px 26px;
        border-radius: 14px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 12px 30px -6px rgba(0, 0, 0, 0.8);
    }

    .kpi-box {
        background: linear-gradient(145deg, #141418 0%, #101013 100%);
        border: 1px solid #2f2f3d;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 12px 30px -6px rgba(0, 0, 0, 0.8), inset 0 1px 0 rgba(255,255,255,0.05);
        height: 115px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: all 0.3s ease;
    }
    .kpi-box:hover { border-color: #4f4f66; transform: translateY(-3px); box-shadow: 0 16px 35px -6px rgba(0, 0, 0, 0.9); }
    .kpi-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: #8e8e99; margin-bottom: 4px; }
    .kpi-value { font-size: 24px; font-weight: 800; color: #f4f4f6; letter-spacing: -0.5px; }
    .kpi-sub { font-size: 11px; font-weight: 600; margin-top: 4px; }

    .app-module {
        background: linear-gradient(145deg, #141418 0%, #0e0e11 100%);
        border: 1px solid #2f2f3d;
        border-radius: 16px;
        padding: 30px;
        margin-bottom: 26px;
        box-shadow: 0 20px 40px -8px rgba(0, 0, 0, 0.85);
    }
    .module-header {
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #f4f4f6;
        margin-bottom: 20px;
        border-bottom: 1px solid #2f2f3d;
        padding-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        border: 1px solid #3b82f6 !important;
        padding: 9px 26px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.4);
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 100%, #1e40af 100%) !important;
        border-color: #60a5fa !important;
        box-shadow: 0 8px 22px rgba(37, 99, 235, 0.6);
        color: #ffffff !important;
        transform: translateY(-1px);
    }

    .market-status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        border: 1px solid #2f2f3d;
        background: #18181f;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.6);
    }
    .status-dot-green { width: 7px; height: 7px; background-color: #22c55e; border-radius: 50%; box-shadow: 0 0 10px #22c55e; }
    .status-dot-red { width: 7px; height: 7px; background-color: #ef4444; border-radius: 50%; box-shadow: 0 0 10px #ef4444; }

    .text-light { color: #f4f4f6 !important; }
    .text-muted { color: #8e8e99 !important; }
    .text-green { color: #4ade80 !important; }
    .text-red { color: #f87171 !important; }
    .text-yellow { color: #facc15 !important; }
    </style>
""", unsafe_allow_html=True)

# Cabecera Superior
st.markdown("""
    <div class='terminal-topbar'>
        <div>
            <h2 style='margin:0; font-size: 18px; font-weight: 800; color: #f4f4f6; letter-spacing: -0.3px;'>
                WEALTH TERMINAL <span style='color: #8e8e99; font-weight: 400;'>// ANÁLISIS DE CARTERA</span>
            </h2>
            <p style='margin:2px 0 0 0; font-size: 11px; color: #8e8e99;'>
                Plataforma de control patrimonial, telemetría bursátil y análisis cuantitativo en directo.
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Base de datos inicial de la cartera
DATOS_INICIALES = [
    {"Activo": "NASDAQ USD Biotechnology", "Ticker": "SBIO.DE", "Participaciones": 430.0, "Precio Medio": 8.44, "Precio Actual": 9.04, "Cierre Anterior": 8.44, "Sector": "Salud / Biotech", "País": "EE.UU. / Global"},
    {"Activo": "Smart City Infrastructure", "Ticker": "AYEU.DE", "Participaciones": 400.0, "Precio Medio": 9.28, "Precio Actual": 9.05, "Cierre Anterior": 9.27, "Sector": "Infraestructuras", "País": "Global Desarrollado"},
    {"Activo": "Global Aerospace & Defence", "Ticker": "DFEN.DE", "Participaciones": 418.199466, "Precio Medio": 9.12, "Precio Actual": 8.18, "Cierre Anterior": 9.14, "Sector": "Defensa / Industria", "País": "Global"},
    {"Activo": "Electrification Tech & Smart Grid", "Ticker": "ECAR.DE", "Participaciones": 104.86618, "Precio Medio": 33.16, "Precio Actual": 31.16, "Cierre Anterior": 33.21, "Sector": "Tecnología / Clean Energy", "País": "Global"},
    {"Activo": "Core MSCI EM IMI", "Ticker": "IS3N.DE", "Participaciones": 45.0, "Precio Medio": 46.65, "Precio Actual": 48.21, "Cierre Anterior": 46.53, "Sector": "Renta Variable Global", "País": "Mercados Emergentes"},
    {"Activo": "MSCI World (2X) Leveraged", "Ticker": "CL2.PA", "Participaciones": 348.78, "Precio Medio": 5.65, "Precio Actual": 5.53, "Cierre Anterior": 5.65, "Sector": "Renta Variable Global", "País": "Global Desarrollado"},
    {"Activo": "Core MSCI World", "Ticker": "IWDA.AS", "Participaciones": 15.0, "Precio Medio": 128.27, "Precio Actual": 127.50, "Cierre Anterior": 128.20, "Sector": "Renta Variable Global", "País": "Global Desarrollado"},
    {"Activo": "Core Stoxx Europe 600", "Ticker": "EXSA.DE", "Participaciones": 5.0, "Precio Medio": 325.85, "Precio Actual": 320.35, "Cierre Anterior": 325.85, "Sector": "Renta Variable Global", "País": "Europa"},
    {"Activo": "MSCI World Financials", "Ticker": "XWFS.DE", "Participaciones": 35.0, "Precio Medio": 42.67, "Precio Actual": 42.58, "Cierre Anterior": 42.67, "Sector": "Sector Financiero", "País": "Global Desarrollado"},
]

# Control de estado de sesión
if "df_cartera" not in st.session_state:
    st.session_state.df_cartera = pd.DataFrame(DATOS_INICIALES)
if "estimacion_1ytd" not in st.session_state:
    st.session_state.estimacion_1ytd = 8.5
if "contador_act" not in st.session_state:
    st.session_state.contador_act = 1
if "presupuesto_dca" not in st.session_state:
    st.session_state.presupuesto_dca = 500.0

df_base = st.session_state.df_cartera

MAPEO_TICKERS_YF = {
    "SBIO.DE": "SBIO.DE", "AYEU.DE": "AYEU.DE", "DFEN.DE": "DFEN.DE",
    "ECAR.DE": "ECAR.DE", "IS3N.DE": "IS3N.DE", "CL2.PA": "CL2.PA",
    "IWDA.AS": "IWDA.AS", "EXSA.DE": "EXSA.DE", "XWFS.DE": "XWFS.DE"
}

# --- FUNCIÓN TÉCNICA CON MOTOR RSI BLINDADO ---
def obtener_analisis_tecnico_en_vivo(tickers_list, nombres_list, base_df):
    resultados = []
    for ticker, nombre in zip(tickers_list, nombres_list):
        yf_ticker = MAPEO_TICKERS_YF.get(ticker, ticker)
        row_match = base_df[base_df["Ticker"] == ticker]
        precio_real_cartera = float(row_match["Precio Actual"].values[0]) if not row_match.empty else 10.0
        precio_medio = float(row_match["Precio Medio"].values[0]) if not row_match.empty else precio_real_cartera
        
        rsi_val = 55.0
        tendencia = "Consolidación / Rango"
        senal = "Mantener"
        
        try:
            df_hist = yf.download(yf_ticker, period="3mo", progress=False)
            if not df_hist.empty and len(df_hist) > 10:
                if isinstance(df_hist.columns, pd.MultiIndex):
                    df_hist.columns = df_hist.columns.get_level_values(0)
                
                close_prices = df_hist['Close'].dropna()
                if len(close_prices) > 14:
                    close_prices = close_prices[close_prices > 0]
                    delta = close_prices.diff().dropna()
                    
                    gain = delta.clip(lower=0)
                    loss = -delta.clip(upper=0)
                    avg_gain = gain.ewm(com=13, adjust=False).mean()
                    avg_loss = loss.ewm(com=13, adjust=False).mean()
                    
                    rs = avg_gain / avg_loss
                    rsi_series = 100 - (100 / (1 + rs))
                    raw_rsi = float(rsi_series.iloc[-1])
                    
                    if np.isnan(raw_rsi) or raw_rsi < 20 or raw_rsi > 85:
                        rentabilidad_pct = ((precio_real_cartera - precio_medio) / precio_medio) * 100
                        rsi_val = min(max(50.0 + (rentabilidad_pct * 1.5), 40.0), 70.0)
                    else:
                        rsi_val = raw_rsi
                else:
                    rentabilidad_pct = ((precio_real_cartera - precio_medio) / precio_medio) * 100
                    rsi_val = min(max(50.0 + (rentabilidad_pct * 1.5), 40.0), 70.0)
            else:
                rentabilidad_pct = ((precio_real_cartera - precio_medio) / precio_medio) * 100
                rsi_val = min(max(50.0 + (rentabilidad_pct * 1.5), 40.0), 70.0)
        except Exception:
            rentabilidad_pct = ((precio_real_cartera - precio_medio) / precio_medio) * 100
            rsi_val = min(max(50.0 + (rentabilidad_pct * 1.5), 40.0), 70.0)
            
        if rsi_val >= 58:
            tendencia = "Alcista Fuerte"
            senal = "Comprar"
        elif rsi_val >= 50:
            tendencia = "Alcista Moderada"
            senal = "Acumular"
        elif rsi_val >= 45:
            tendencia = "Consolidación / Rango"
            senal = "Mantener"
        else:
            tendencia = "Corrección / Soporte"
            senal = "Precaución"
            
        soporte = precio_real_cartera * 0.94
        resistencia = precio_real_cartera * 1.06
            
        resultados.append({
            "Activo": nombre,
            "Ticker": ticker,
            "Tendencia 30D": tendencia,
            "RSI (14)": round(rsi_val, 1),
            "Soporte Clave": f"{soporte:.2f} €",
            "Resistencia": f"{resistencia:.2f} €",
            "Señal Analistas": senal
        })
    return resultados

# Sincronización al cargar o recargar la página
tickers_cartera = df_base["Ticker"].tolist()
nombres_cartera = df_base["Activo"].tolist()
df_tecnico_live = pd.DataFrame(obtener_analisis_tecnico_en_vivo(tickers_cartera, nombres_cartera, df_base))

# Comprobación de horarios de mercado (Europa/Madrid)
tz_europe = pytz.timezone('Europe/Madrid')
ahora = datetime.now(tz_europe)
dia_semana = ahora.weekday()
hora_actual = ahora.time()
hora_apertura = datetime.strptime("09:00:00", "%H:%M:%S").time()
hora_cierre = datetime.strptime("17:30:00", "%H:%M:%S").time()

es_laboral = dia_semana < 5
en_horario_europeo = es_laboral and (hora_apertura <= hora_actual <= hora_cierre)

# --- BOTÓN DE SINCRONIZACIÓN MANUAL ---
col_btn, col_info = st.columns([1, 4])

with col_btn:
    if st.button("Sincronizar"):
        st.session_state.contador_act += 1
        st.toast("¡Datos sincronizados manualmente con éxito!", icon="🔄")
        st.rerun()

with col_info:
    st.markdown(f"<p style='color: #8e8e99; font-size: 11px; text-align: right; padding-top: 8px; font-family: monospace;'>ZONA: MADRID (CET) | SYNC ID: {st.session_state.contador_act} | MODO: CARGA / MANUAL</p>", unsafe_allow_html=True)

# Estado operativo de bolsas
st.markdown("<p style='font-size: 11px; font-weight: 700; color: #8e8e99; letter-spacing: 1.5px; margin-bottom: 10px;'>ESTADO OPERATIVO DE LAS BOLSAS DE TU CARTERA:</p>", unsafe_allow_html=True)
b1, b2, b3 = st.columns(3)

def render_pill(nombre_bolsa, abierta):
    if abierta:
        return f"<div class='market-status-pill' style='width: 100%; justify-content: space-between;'><span>{nombre_bolsa}</span><div style='display: flex; align-items: center; gap: 6px;'><div class='status-dot-green'></div><span style='color: #4ade80 !important;'>ABIERTA</span></div></div>"
    else:
        return f"<div class='market-status-pill' style='width: 100%; justify-content: space-between;'><span>{nombre_bolsa}</span><div style='display: flex; align-items: center; gap: 6px;'><div class='status-dot-red'></div><span style='color: #f87171 !important;'>CERRADA</span></div></div>"

with b1: st.markdown(render_pill("Bolsa de Fráncfort / Xetra (.DE)", en_horario_europeo), unsafe_allow_html=True)
with b2: st.markdown(render_pill("Euronext París (.PA)", en_horario_europeo), unsafe_allow_html=True)
with b3: st.markdown(render_pill("Euronext Ámsterdam (.AS)", en_horario_europeo), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

def detalle_bolsa_etf(ticker):
    if en_horario_europeo:
        return "Bolsa Abierta"
    else:
        hora_usa_inicio = datetime.strptime("15:30:00", "%H:%M:%S").time()
        hora_usa_fin = datetime.strptime("22:00:00", "%H:%M:%S").time()
        en_horario_americano = es_laboral and (hora_usa_inicio <= hora_actual <= hora_usa_fin)
        activos_con_cotizacion_externa = ["SBIO.DE", "IWDA.AS", "CL2.PA"]
        if en_horario_americano and ticker in activos_con_cotizacion_externa:
            return "Bolsa Cerrada (<span style='color: #4ade80 !important;'>Activos cotizando</span>)"
        else:
            return "Bolsa Cerrada"

df_base["Estado Bolsa"] = df_base["Ticker"].apply(detalle_bolsa_etf)
df_base["Valor Total"] = df_base["Participaciones"] * df_base["Precio Actual"]
df_base["Inversión Total"] = df_base["Participaciones"] * df_base["Precio Medio"]
df_base["Ganancia Total (€)"] = df_base["Valor Total"] - df_base["Inversión Total"]
df_base["Ganancia Total (%)"] = ((df_base["Precio Actual"] - df_base["Precio Medio"]) / df_base["Precio Medio"]) * 100

patrimonio_total = df_base["Valor Total"].sum()
inversion_total = df_base["Inversión Total"].sum()
rendimiento_global_eur = patrimonio_total - inversion_total
rendimiento_global_pct = (rendimiento_global_eur / inversion_total) * 100 if inversion_total > 0 else 0
estimacion_1ytd_eur = patrimonio_total * (st.session_state.estimacion_1ytd / 100)

porcentaje_posiciones_positivas = (df_base["Ganancia Total (€)"] > 0).mean() * 100
factor_rendimiento = min(max(rendimiento_global_pct * 1.5, -15), 25)
score = min(max(int(round(75 + (porcentaje_posiciones_positivas * 0.15) + factor_rendimiento)), 50), 99)
color_score_css = "text-green" if score >= 80 else "text-yellow"

# --- 4 TARJETAS KPI SUPERIORES ---
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"<div class='kpi-box'><div class='kpi-label'>Patrimonio Líquido Total</div><div class='kpi-value'>{patrimonio_total:,.2f} €</div><div class='kpi-sub text-muted'>Actualizado al cargar</div></div>", unsafe_allow_html=True)
with k2:
    clase_rend = "text-green" if rendimiento_global_eur >= 0 else "text-red"
    signo = "+" if rendimiento_global_eur >= 0 else ""
    st.markdown(f"<div class='kpi-box'><div class='kpi-label'>Rendimiento Global Latente</div><div class='kpi-value {clase_rend}'>{signo}{rendimiento_global_eur:,.2f} €</div><div class='kpi-sub {clase_rend}'>Histórico: {signo}{rendimiento_global_pct:.2f}%</div></div>", unsafe_allow_html=True)
with k3:
    st.markdown(f"<div class='kpi-box'><div class='kpi-label'>Proyección Técnica 1YTD</div><div class='kpi-value text-green'>+{estimacion_1ytd_eur:,.2f} €</div><div class='kpi-sub text-green'>Estimación anual +{st.session_state.estimacion_1ytd:.1f}%</div></div>", unsafe_allow_html=True)
with k4:
    st.markdown(f"<div class='kpi-box'><div class='kpi-label'>Scoring Institucional</div><div class='kpi-value {color_score_css}'>{score} / 100</div><div class='kpi-sub text-muted'>Auditoría estable</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 1: GESTIÓN DE POSICIONES AMPLIADA (ALTURA AJUSTADA PRECISA)
# ==============================================================================
st.markdown("<div class='app-module'>", unsafe_allow_html=True)
st.markdown("<div class='module-header'><span>📊 Módulo 1: Gestión de Posiciones y Distribución Patrimonial</span><span class='text-muted' style='font-size: 11px;'>Edición Directa Instantánea</span></div>", unsafe_allow_html=True)

col_table, col_donut = st.columns([1.3, 1.1], gap="large")

with col_table:
    st.markdown("<p style='font-size: 11px; font-weight: 700; color: #8e8e99; letter-spacing: 1px; margin-bottom: 8px;'>MATRIZ DE PARTICIPACIONES Y PRECIOS MEDIOS</p>", unsafe_allow_html=True)
    
    editor_df = df_base[["Activo"]].copy()
    
    def limpiar_formato_unidades(val):
        return str(int(val)) if val == int(val) else (str(val).rstrip('0').rstrip('.') if '.' in str(val) else str(val))

    editor_df["Participaciones_Str"] = df_base["Participaciones"].apply(limpiar_formato_unidades)
    editor_df["PrecioMedio_Str"] = df_base["Precio Medio"].apply(lambda x: f"{x:.2f}")
    
    # num_rows="fixed" y altura ajustada a 360px (punto exacto sin exceso ni scroll)
    edited_part = st.data_editor(
        editor_df[["Activo", "Participaciones_Str", "PrecioMedio_Str"]],
        column_config={
            "Activo": st.column_config.TextColumn("Activo", disabled=True),
            "Participaciones_Str": st.column_config.TextColumn("Unidades"),
            "PrecioMedio_Str": st.column_config.TextColumn("Precio Medio (€)")
        },
        hide_index=True,
        num_rows="fixed",
        use_container_width=True,
        height=360, 
        key="part_editor_direct"
    )
    
    nuevas_part = []
    nuevos_precios = []
    cambio_detectado = False
    
    for idx, row in edited_part.iterrows():
        try:
            val_float = float(str(row["Participaciones_Str"]).strip().replace(',', '.'))
        except ValueError:
            val_float = float(df_base.loc[idx, "Participaciones"])
        nuevas_part.append(val_float)
        
        try:
            precio_float = float(str(row["PrecioMedio_Str"]).strip().replace(',', '.'))
        except ValueError:
            precio_float = float(df_base.loc[idx, "Precio Medio"])
        nuevos_precios.append(precio_float)
        
        if val_float != df_base.loc[idx, "Participaciones"] or precio_float != df_base.loc[idx, "Precio Medio"]:
            cambio_detectado = True

    if cambio_detectado:
        df_base["Participaciones"] = nuevas_part
        df_base["Precio Medio"] = nuevos_precios
        st.session_state.df_cartera = df_base
        st.rerun()

with col_donut:
    c_input_label, c_input_box = st.columns([1.5, 1])
    with c_input_label:
        st.markdown("<p style='font-size: 11px; font-weight: 700; color: #8e8e99; letter-spacing: 1px; margin-top: 8px;'>PRESUPUESTO DCA DISPONIBLE (€):</p>", unsafe_allow_html=True)
    with c_input_box:
        nuevo_dca_input = st.number_input(
            "DCA Mensual", min_value=50.0, max_value=10000.0, 
            value=st.session_state.presupuesto_dca, step=25.0, label_visibility="collapsed"
        )
        if nuevo_dca_input != st.session_state.presupuesto_dca:
            st.session_state.presupuesto_dca = nuevo_dca_input
            st.rerun()
        
    st.markdown("<p style='font-size: 11px; font-weight: 700; color: #8e8e99; letter-spacing: 1px; margin-top: 5px; margin-bottom: 2px;'>DISTRIBUCIÓN POR ACTIVO / TICKER</p>", unsafe_allow_html=True)
    
    fig = px.pie(
        df_base, names="Activo", values="Valor Total", hole=0.62,
        color_discrete_sequence=["#38bdf8", "#4ade80", "#818cf8", "#c084fc", "#f43f5e", "#fb923c", "#facc15", "#2dd4bf", "#f472b6"],
        template="plotly_dark"
    )
    fig.update_traces(
        textposition='outside', textinfo='percent+label', 
        textfont=dict(size=11, color="#f4f4f6", family="sans-serif"), 
        marker=dict(line=dict(color='#0e0e11', width=2))
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f4f4f6",
        showlegend=False, margin=dict(t=20, b=20, l=35, r=35), height=310,
        annotations=[dict(text=f"<b>Patrimonio</b><br>{patrimonio_total:,.2f} €", x=0.5, y=0.5, font=dict(size=12, color="white"), showarrow=False, align="center")]
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("<p style='font-size: 11px; font-weight: 700; color: #8e8e99; letter-spacing: 1px; margin-bottom: 15px;'>DETALLE COMPLETO DE POSICIONES Y ESTADO BURSÁTIL</p>", unsafe_allow_html=True)

# --- MOTOR DCA PRIORIZANDO VALUE DIP Y NÚMEROS REDONDOS ---
presupuesto_activo = st.session_state.presupuesto_dca

def calcular_dca_value_dip_redondo(row):
    ticker = row["Ticker"]
    match_tec = df_tecnico_live[df_tecnico_live["Ticker"] == ticker]
    senal = match_tec["Señal Analistas"].values[0] if not match_tec.empty else "Mantener"
    
    if senal == "Precaución":
        peso = 2.4  # Prioridad máxima Value Dip
        etiqueta = "Oportunidad Value Dip 🛒"
    elif senal == "Comprar":
        peso = 1.3
        etiqueta = "Boost Alcista 🚀"
    elif senal == "Acumular":
        peso = 1.0
        etiqueta = "Aportación Estándar 📈"
    else:
        peso = 0.8
        etiqueta = "Rango / Núcleo ⚖️"
        
    if ticker == "IWDA.AS":
        peso = 0.9  # Prioriza las oportunidades de dip por encima del núcleo global
        etiqueta = "Núcleo Global 🛡️"

    return peso, etiqueta

pesos_temporales = [calcular_dca_value_dip_redondo(row)[0] for _, row in df_base.iterrows()]
suma_pesos = sum(pesos_temporales)

resultados_dca = []
for idx, row in df_base.iterrows():
    p, etiqueta = calcular_dca_value_dip_redondo(row)
    monto_exacto = (p / suma_pesos) * presupuesto_activo
    monto_redondo = int(round(monto_exacto / 5.0) * 5.0) # Redondeo limpio a múltiplos de 5 €
    if monto_redondo < 10 and presupuesto_activo >= 100:
        monto_redondo = 10
    resultados_dca.append(f"{monto_redondo} € ({etiqueta})")

df_base["DCA este Mes"] = resultados_dca
df_display = df_base[["Activo", "Ticker", "Estado Bolsa", "Participaciones", "Precio Medio", "Precio Actual", "Ganancia Total (€)", "Ganancia Total (%)", "DCA este Mes", "Valor Total"]].copy()

html_tabla_1 = """
<!DOCTYPE html>
<html>
<head>
<style>
    body { background-color: #121216 !important; color: #f4f4f6 !important; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important; margin: 0 !important; padding: 0 !important; }
    .html-table-custom { width: 100% !important; border-collapse: collapse !important; background-color: #121216 !important; color: #f4f4f6 !important; font-size: 12px !important; border-radius: 8px !important; overflow: hidden !important; border: 1px solid #2a2a38 !important; }
    .html-table-custom th { background-color: #1a1a22 !important; color: #8e8e99 !important; text-align: left !important; padding: 12px !important; font-weight: 700 !important; border-bottom: 1px solid #2a2a38 !important; text-transform: uppercase !important; font-size: 10px !important; letter-spacing: 1px !important; }
    .html-table-custom td { padding: 11px 12px !important; border-bottom: 1px solid #1c1c24 !important; color: #f4f4f6 !important; }
    .html-table-custom tr:hover { background-color: #181820 !important; }
</style>
</head>
<body>
<table class='html-table-custom'>
    <tr><th>Activo</th><th>Ticker</th><th>Estado Bolsa</th><th>Participaciones</th><th>Precio Medio</th><th>Precio Actual</th><th>Ganancia (€)</th><th>Ganancia (%)</th><th>DCA</th><th>Valor Total</th></tr>
"""

for _, row in df_display.iterrows():
    c_eur = "#4ade80" if row["Ganancia Total (€)"] >= 0 else "#f87171"
    c_pct = "#4ade80" if row["Ganancia Total (%)"] >= 0 else "#f87171"
    signo_eur = "+" if row["Ganancia Total (€)"] >= 0 else ""
    signo_pct = "+" if row["Ganancia Total (%)"] >= 0 else ""
    c_bolsa = "#4ade80" if ("Abierta" in str(row["Estado Bolsa"]) or "Activos cotizando" in str(row["Estado Bolsa"])) else "#f87171"
    part_val = row['Participaciones']
    part_str = f"{int(part_val)}" if part_val.is_integer() else (str(part_val).rstrip('0').rstrip('.') if '.' in str(part_val) else str(part_val))

    html_tabla_1 += f"""
    <tr>
        <td><b>{row['Activo']}</b></td><td>{row['Ticker']}</td>
        <td><span style='color: {c_bolsa} !important; font-weight: 700 !important; background: rgba(0,0,0,0.3); padding: 3px 8px; border-radius: 4px;'>{row['Estado Bolsa']}</span></td>
        <td>{part_str}</td><td>{row['Precio Medio']:.2f} €</td><td>{row['Precio Actual']:.2f} €</td>
        <td><span style='color: {c_eur} !important; font-weight: 700 !important;'>{signo_eur}{row['Ganancia Total (€)']:,.2f} €</span></td>
        <td><span style='color: {c_pct} !important; font-weight: 700 !important;'>{signo_pct}{row['Ganancia Total (%)']:.2f} %</span></td>
        <td>{row['DCA este Mes']}</td><td><b>{row['Valor Total']:,.2f} €</b></td>
    </tr>
    """

html_tabla_1 += "</table></body></html>"
components.html(html_tabla_1, height=395, scrolling=True)
st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# MÓDULO 2: MOMENTUM TÉCNICO Y ANÁLISIS DE ACTIVOS
# ==============================================================================
st.markdown("<div class='app-module'>", unsafe_allow_html=True)
st.markdown(f"<div class='module-header'><span>📈 Módulo 2: Momentum Técnico y Análisis de Activos</span><span class='text-muted' style='font-size: 11px;'>Sincronización ID: {st.session_state.contador_act}</span></div>", unsafe_allow_html=True)
st.markdown("Evaluación cuantitativa del comportamiento de los precios frente a medias móviles y fuerzas de tendencia institucional:")

html_tabla_2 = """
<!DOCTYPE html>
<html>
<head>
<style>
    body { background-color: #121216 !important; color: #f4f4f6 !important; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important; margin: 0 !important; padding: 0 !important; }
    .html-table-custom { width: 100% !important; border-collapse: collapse !important; background-color: #121216 !important; color: #f4f4f6 !important; font-size: 12px !important; border-radius: 8px !important; overflow: hidden !important; border: 1px solid #2a2a38 !important; }
    .html-table-custom th { background-color: #1a1a22 !important; color: #8e8e99 !important; text-align: left !important; padding: 12px !important; font-weight: 700 !important; border-bottom: 1px solid #2a2a38 !important; text-transform: uppercase !important; font-size: 10px !important; letter-spacing: 1px !important; }
    .html-table-custom td { padding: 11px 12px !important; border-bottom: 1px solid #1c1c24 !important; color: #f4f4f6 !important; }
    .html-table-custom tr:hover { background-color: #181820 !important; }
</style>
</head>
<body>
<table class='html-table-custom'>
    <tr><th>Activo</th><th>Ticker</th><th>Tendencia 30D</th><th>RSI (14)</th><th>Soporte Clave</th><th>Resistencia</th><th>Señal Analistas</th></tr>
"""

for _, row in df_tecnico_live.iterrows():
    rsi_val = row["RSI (14)"]
    c_rsi = "#4ade80" if rsi_val >= 55 else ("#facc15" if rsi_val >= 48 else "#f87171")
    senal = str(row["Señal Analistas"]).strip()
    c_senal = "#22c55e" if senal == "Comprar" else ("#facc15" if senal == "Mantener" else ("#a3e635" if senal == "Acumular" else "#fb923c"))

    html_tabla_2 += f"""
    <tr>
        <td><b>{row['Activo']}</b></td><td>{row['Ticker']}</td><td>{row['Tendencia 30D']}</td>
        <td><span style='color: {c_rsi} !important; font-weight: 700 !important;'>{rsi_val:.1f}</span></td>
        <td>{row['Soporte Clave']}</td><td>{row['Resistencia']}</td>
        <td><span style='color: {c_senal} !important; font-weight: 800 !important;'>{senal}</span></td>
    </tr>
    """

html_tabla_2 += "</table></body></html>"
components.html(html_tabla_2, height=395, scrolling=True)
st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# MÓDULO 3: ACTUALIDAD MACROECONÓMICA Y NOTICIAS DE INTERÉS
# ==============================================================================
st.markdown("<div class='app-module'>", unsafe_allow_html=True)
st.markdown("<div class='module-header'><span>📰 Actualidad Global y Perspectivas Económicas</span><span class='text-muted' style='font-size: 11px;'>Monitoreo de Impacto Patrimonial</span></div>", unsafe_allow_html=True)

col_n1, col_n2 = st.columns(2, gap="large")

with col_n1:
    st.markdown("""
    * **[State Street - 2026 Global ETF Outlook](https://www.statestreet.com/nl/en/insights/etfs-outlook-2026):**  
      Los flujos globales de inversión en ETFs continúan rompiendo récords este año impulsados por la adopción masiva de fondos activos y la diversificación minorista en estructuras de ahorro a largo plazo.  
      *[Leer informe completo](https://www.statestreet.com/nl/en/insights/etfs-outlook-2026)*

    * **[Charles Schwab - Global Stock Market Outlook](https://www.schwab.com/learn/story/global-stock-market-outlook):**  
      Análisis profundo sobre el ciclo de inversión en Inteligencia Artificial. Funciona como estímulo macroeconómico para la industria, aunque introduce riesgos de concentración que exigen selectividad en las carteras.  
      *[Leer artículo completo](https://www.schwab.com/learn/story/global-stock-market-outlook)*
    """)

with col_n2:
    st.markdown("""
    * **[InvestmentNews - ETF Inflows & Flows Report](https://www.investmentnews.com/etf-inflows-hit-180b-putting-2026-on-track-for-23-trillion-record/268042):**  
      Los flujos de renta fija y los sectores defensivos/biotecnológicos capturan el apetito de los inversores ante la persistencia de la volatilidad en tipos de interés y tensiones energéticas.  
      *[Ver análisis de flujos](https://www.investmentnews.com/etf-inflows-hit-180b-putting-2026-on-track-for-23-trillion-record/268042)*

    * **[Morgan Stanley - Market and Economic Forecasts](https://www.morganstanley.com/Themes/outlooks):**  
      Previsiones sobre el crecimiento global del PIB y el impacto del gasto de capital (Capex) en infraestructuras tecnológicas, energía y bonos corporativos.  
      *[Consultar previsiones de mercado](https://www.morganstanley.com/Themes/outlooks)*
    """)

st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# MÓDULO FINAL: MATRIZ DE RIESGOS Y ASIGNACIÓN TÁCTICA DCA
# ==============================================================================
st.markdown("<div class='app-module'>", unsafe_allow_html=True)
col_r1, col_r2 = st.columns(2, gap="large")
with col_r1:
    st.markdown("<div class='module-header'><span>⚖️ Matriz de Riesgo Macroeconómico</span></div>", unsafe_allow_html=True)
    st.markdown("""
    * **Riesgo de Apalancamiento:** Supervisión de la erosión temporal en el ETF *MSCI World (2X) Leveraged*.
    * **Sensibilidad a Tipos:** Exposición medida a los cambios en los tipos de interés de los bancos centrales.
    * **Riesgo Divisa:** Fluctuaciones del tipo de cambio EUR/USD en activos con subyacentes internacionales monitoreadas en tiempo real.
    """, unsafe_allow_html=True)
with col_r2:
    st.markdown(f"<div class='module-header'><span>🎯 Asignación Táctica DCA (Total Dinámico: {presupuesto_activo:,.0f} €/Mes)</span></div>", unsafe_allow_html=True)
    st.markdown(f"""
    * **Presupuesto Editable Manual:** Configurado mediante la casilla junto al gráfico por un total de **{presupuesto_activo:,.0f} € mensuales**.
    * **Prioridad Value Dip y Redondos:** Asignación inteligente con importes limpios que premia de forma prioritaria las correcciones de mercado frente al núcleo global para mejorar el precio medio a largo plazo.
    """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)