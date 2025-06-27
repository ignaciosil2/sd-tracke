import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

DATA_FILE = "data.json"
hoy = datetime.now().date()

# Datos iniciales de agentes
initial_data = {
    'Agente': [
        'Soldati Conecta', 'Ana Álvarez Ugarte', 'Ana Hilbert', 'Carlos Arostegui', 'Beatriz Perez Tritencio',
        'Ingrid Arostegui', 'Claudia Surin', 'Florencia Victory', 'Florencia Ezcurra', 'Jerónimo Gallardo',
        'Noel Verger', 'Gisella Maria Balderiote', 'Lucia O’connor', 'Luis Silveira', 'Marcia Blanco',
        'Maria Fernanda Hidalgo', 'Maria Noel Lorenzo', 'Natalia Silvina Macchia', 'Rafael Levy', 'Pedro Pinasco',
        'Pedro Bustillo', 'Gustavo Tossetti', 'Alejandro Milhas', 'Administración central Conecta', 'Sofia Gravenhorst',
        'Mariano Ignacio del Yerro', 'Carmen María Sturla', 'Agustina Fernandez Gradaille', 'Fernando Gago', 'Loli Tarelli',
        'Javier Miguens', 'GONZALO ESTERKIN', 'Walter Jacinto Coronel', 'Virginia Fernandez', 'Facundo Sagasta',
        'Bruno Levy', 'Santiago Capacete', 'Maria Ximena Angelillo', 'Matías Laplacette', 'Sebastián Ortiz',
        'Vilma Isabel Aldanondo', 'Cristian Javier Acosta', 'Agustina Crnich', 'Luciana Bottini', 'Marketing',
        'Yesica Cabrera', 'Nicolas Milhas', 'Daniel Cabrera', 'Estanislao Julianes', 'Fabian Pedrazzini',
        'Mateo Jose Vallega', 'Carolina Landra', 'Fabiana Rodriguez', 'Juan Maria Basombrio'
    ],
    'SD': [
        0,2,1,1,0,4,1,13,0,4,2,2,0,0,0,0,1,1,2,8,15,0,80,0,21,3,0,0,8,2,3,0,4,6,1,14,3,22,1,0,0,4,20,11,0,0,9,1,10,3,
        0,0,0,0
    ]
}

# Función para cargar datos desde archivo
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data["data"])
        df["Historial"] = df["Historial"].apply(lambda h: [(datetime.strptime(i, "%Y-%m-%d").date(), datetime.strptime(f, "%Y-%m-%d").date() if f else None) for i, f in h])
        return df
    else:
        df = pd.DataFrame(initial_data)
        df['Monto'] = 0.0
        df['Historial'] = [[] for _ in range(len(df))]
        return df

# Función para guardar datos en archivo
def guardar_datos(df):
    export_df = df.copy()
    export_df["Historial"] = export_df["Historial"].apply(lambda h: [(i.strftime("%Y-%m-%d"), f.strftime("%Y-%m-%d") if f else None) for i, f in h])
    with open(DATA_FILE, "w") as f:
        json.dump({"data": export_df.to_dict(orient="records")}, f, indent=2)

# Función para calcular monto
def calcular_monto(fechas):
    total = 0
    for inicio, fin in fechas:
        if fin is None:
            fin = hoy
        dias = (fin - inicio).days
        total += (dias / 30) * 10000
    return round(total, 2)

# Cargar datos
if 'df' not in st.session_state:
    st.session_state.df = cargar_datos()

st.title("Gestor de SD (Super Destaques)")
st.caption("Cada SD activo por 30 días = $10.000")

# Mostrar tabla editable
for i, row in st.session_state.df.iterrows():
    col1, col2, col3, col4 = st.columns([3,1,2,2])
    with col1:
        st.markdown(f"**{row['Agente']}**")
    with col2:
        if st.button("+1", key=f"plus_{i}"):
            st.session_state.df.at[i, 'SD'] += 1
            st.session_state.df.at[i, 'Historial'].append((hoy, None))
            guardar_datos(st.session_state.df)
        if st.button("-1", key=f"minus_{i}"):
            if st.session_state.df.at[i, 'SD'] > 0:
                st.session_state.df.at[i, 'SD'] -= 1
                historial = st.session_state.df.at[i, 'Historial']
                for j in reversed(range(len(historial))):
                    if historial[j][1] is None:
                        historial[j] = (historial[j][0], hoy)
                        break
                guardar_datos(st.session_state.df)
    with col3:
        st.markdown(f"SDs: **{row['SD']}**")
    with col4:
        monto = calcular_monto(st.session_state.df.at[i, 'Historial'])
        st.session_state.df.at[i, 'Monto'] = monto
        st.markdown(f"Monto: **${monto:,.2f}**")

st.markdown("---")

# Mostrar historial detallado
st.subheader("Historial de cambios por agente")
selected = st.selectbox("Selecciona un agente", st.session_state.df['Agente'])
idx = st.session_state.df[st.session_state.df['Agente'] == selected].index[0]
hist = st.session_state.df.at[idx, 'Historial']

if hist:
    hist_data = [{'Inicio': i, 'Cierre': c if c else 'Activo'} for i, c in hist]
    st.table(pd.DataFrame(hist_data))
else:
    st.info("Este agente aún no tiene historial de SD.")
