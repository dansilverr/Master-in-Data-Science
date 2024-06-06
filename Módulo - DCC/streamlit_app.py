import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from streamlit_option_menu import option_menu
from streamlit_calendar import calendar
from PIL import Image
import urllib.request
import requests
#import tkinter as tk
import io
from io import BytesIO
#from tkinter import Tk, filedialog
import base64
#import xlsxwriter test

with st.sidebar:
    selected = option_menu("", ["Smart Maintenance Calendar", "Status Gerais", "Previsão - Tempo Uso"],
        icons=['calendar2-range', 'house', 'clock-fill', ], menu_icon="", default_index=0)
    
@st.cache_data
def load_data():
    # Download do arquivo XLSX localmente
    url = "https://github.com/AurelioGuilherme/volvo_streamlit_sirius/raw/main/dados_preditos.xlsx"
    filename = "dados_preditos.xlsx"
    urllib.request.urlretrieve(url, filename)

    # Ler o arquivo XLSX em um DataFrame
    df = pd.read_excel(filename)
    df = df.rename({"Chassis ID": "Chassis", "Machine History Date Day": "Data","Compensated Working Hours By Day":'Horas Trabalhadas'}, axis =1)

    return df

df_dados = load_data()
df_manutencao = df_dados[df_dados['manutencao'] == 'sim']
df_forecasting = df_dados[df_dados['is_future'] == True]
df_historico = df_dados[df_dados['is_future'] == False]


all_chassis = set(df_dados["Chassis"])
resources = [{"id": chassis} for chassis in all_chassis]

def resize_image(image, new_size):
    resized_image = image.resize(new_size)
    return resized_image

# Carregar o logo da Volvo
image_url = "https://github.com/AurelioGuilherme/volvo_streamlit_sirius/blob/main/logo_volvo_nova.png?raw=true"
response = requests.get(image_url)
image = Image.open(BytesIO(response.content))
resized_image = resize_image(image, (75,75))
#st.image(resized_image, use_column_width=False)

def filtros(df_dados):
    dealer_filter = st.sidebar.selectbox("Dealer", ["Todos"] + list(df_dados["Dealer"].unique()))
    segmento_filter = st.sidebar.selectbox("Segmento", ["Todos"] + list(df_dados["Segmento"].unique()))
    modelo_filter = st.sidebar.selectbox("Modelo", ["Todos"] + list(df_dados["Modelo"].unique()))
    pais_filter = st.sidebar.selectbox("País", ["Todos"] + list(df_dados["País"].unique()))

    if dealer_filter != 'Todos' and segmento_filter != 'Todos' and modelo_filter != 'Todos':
        chassis_options = df_dados[(df_dados['Dealer'] == dealer_filter) & 
                                   (df_dados['Segmento'] == segmento_filter)& 
                                   (df_dados['Modelo'] == modelo_filter)& 
                                   (df_dados['País'] == pais_filter)]["Chassis"].unique()
    elif dealer_filter != 'Todos':
        chassis_options = df_dados[df_dados['Dealer'] == dealer_filter]["Chassis"].unique()
    elif segmento_filter != 'Todos':
        chassis_options = df_dados[df_dados['Segmento'] == segmento_filter]["Chassis"].unique()
    elif modelo_filter != 'Todos':
        chassis_options = df_dados[df_dados['Modelo'] == modelo_filter]["Chassis"].unique()
    elif pais_filter != 'Todos':
        chassis_options = df_dados[df_dados['País'] == pais_filter]["Chassis"].unique()
    else:
        chassis_options = df_dados["Chassis"].unique()
    chassis_id_filter = st.sidebar.selectbox("Chassis ID", ["Todos"] + list(chassis_options))

    date_filter = st.sidebar.date_input("Datas", [df_dados["Data"].min(), df_dados["Data"].max()], key="date_filter")

    # Converter valores do filtro de data para datetime64[ns]
    date_filter = [pd.to_datetime(date_filter[0]), pd.to_datetime(date_filter[1])]

    # Aplicar filtros ao DataFrame
    filtered_df = df_dados[
    ((df_dados["Chassis"] == chassis_id_filter) | (chassis_id_filter == "Todos")) &
    ((df_dados["Dealer"] == dealer_filter) | (dealer_filter == "Todos")) &
    ((df_dados["Segmento"] == segmento_filter) | (segmento_filter == "Todos")) &
    ((df_dados["Modelo"] == modelo_filter) | (modelo_filter == "Todos")) &
    ((df_dados["País"] == pais_filter) | (pais_filter == "Todos")) &
    ((df_dados["Data"] >= date_filter[0]) & (df_dados["Data"] <= date_filter[1]))
    ]

    return filtered_df, chassis_id_filter

def main():
    # Carregar os dados e manter em cache
    df_dados = load_data()    

  

if selected == "Previsão - Tempo Uso":

    # Criar duas colunas para o titulo da pagina
    col1_1, col2_2 = st.columns([1, 3])

    # Adicionar a imagem redimensionada
    col1_1.image(resized_image, caption='', use_column_width=False)

    # Adicionar o texto de título ao logo
    col2_2.markdown('<h1 style="flex: 1; margin: 0;">Previsão do Tempo de Uso</h1>', unsafe_allow_html=True)

    # Adicionar uma linha de espaço após o título
    st.markdown("<br>", unsafe_allow_html=True)

    # Sidebar com filtros
    st.sidebar.header("Filtros")
    filtered_df_forecasting, chassis_id_filter = filtros(df_forecasting)
    
    # ID do Chassis e Média de Horas Trabalhadas lado a lado
    col3, col4 = st.columns(2)

    media_horas_trabalhadas = round(filtered_df_forecasting['Horas Trabalhadas'].mean(), 2)
    if chassis_id_filter == "Todos":    
      st.markdown("<h3 style='text-align: center;'>Selecione no Filtro um Chassi ID para ver a Média de Horas dessa Máquina</h3>", unsafe_allow_html=True)
    else:
      col3.markdown("<h3 style='text-align: center;'>Chassi ID Selecionado</h3>", unsafe_allow_html=True)
      col3.markdown(f"<p style='text-align: center; font-size: 30px;'>{filtered_df_forecasting['Chassis'].unique()}</p>", unsafe_allow_html=True)     
      col4.markdown("<h3 style='text-align: center;'>Média de Horas do Chassi</h3>", unsafe_allow_html=True)
      col4.markdown(f"<p style='text-align: center; font-size: 38px;'>{media_horas_trabalhadas}</p>", unsafe_allow_html=True)
      st.markdown("<br>", unsafe_allow_html=True)
      st.markdown('<h3 style="flex: 1; margin: 0;">Previsão das Horas Trabalhadas</h3>', unsafe_allow_html=True)
  
    # Verifica se o filtro chassis_id_filter está definido como "Todos"
    if chassis_id_filter == "Todos":
        st.markdown("<p>Por favor, selecione um Chassis ID para visualizar o gráfico</p>", unsafe_allow_html=True)
    else:   
      chart = alt.Chart(filtered_df_forecasting).mark_line().encode(x="Data:T", y="Horas Trabalhadas:Q", color="Chassis:N",
         tooltip=["Data:T", "Horas Trabalhadas:Q", "Chassis:N"]).properties(width=800, height=400)
      st.altair_chart(chart)


if selected == "Smart Maintenance Calendar":

    # Criar duas colunas para o titulo da pagina
    col1, col2 = st.columns([1, 4])

    # Adicionar a imagem redimensionada
    col1.image(resized_image, caption='', use_column_width=False)

    # Adicionar o texto de título ao logo
    col2.markdown('<h1 style="flex: 1; margin: 0; text-align: center;">Smart Maintenance Calendar</h1>', unsafe_allow_html=True)

    # Adicionar uma linha de espaço após o título
    st.markdown("<br>", unsafe_allow_html=True)

    # Adicionar um filtro para selecionar os recursos
    selected_resource = st.selectbox("Selecione o Chassis ID", ["Todos"] + list(df_dados["Chassis"].unique()))

    # Adicionar um filtro adicional para escolher recursos com manutenção
    #filtro_manutencao = st.checkbox("Chassis ID com Manutenções Próximas", value=False)

    #if filtro_manutencao == True:
       

    # Adicionar uma linha de espaço após os filtros
    st.markdown("<br>", unsafe_allow_html=True)

    # Transformar os dados do DataFrame em eventos para o calendário
    calendar_events = []
    for index, row in df_manutencao.iterrows():
        event = {
            "title": f"Manutenção - {row['Chassis']}",
            "start": row['Data'].isoformat(),
            "end": row['Data'].isoformat(),
            "resourceId": row['Chassis'],
        }
        calendar_events.append(event)

    # Filtrar eventos do calendário com base no recurso selecionado
    filtered_events = [event for event in calendar_events if selected_resource == "Todos" or event["resourceId"] == selected_resource]

    calendar_options = {
        "editable": "true",
        "selectable": "true",
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "resourceTimelineWeek,resourceTimelineMonth",
        },
   #     "slotMinTime": "06:00:00",
   #     "slotMaxTime": "18:00:00",
        "initialView": "resourceTimelineMonth",
        "resources": resources,
    }

    # Filtrar os chassis exibidos no calendário com base no recurso selecionado
    filtered_resources = [resource for resource in calendar_options["resources"] if selected_resource == "Todos" or resource["id"] == selected_resource]

    calendar_options["resources"] = filtered_resources

    custom_css="""
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            font-style: italic;
        }
        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
    """

    # Função para extrair calendário para Excel
  #  df_calendar = pd.DataFrame(calendar_events)
  #      
  #  towrite = io.BytesIO()
  #  downloaded_file = df_calendar.to_excel(towrite, encoding='utf-8', index=False, header=True)
  #  towrite.seek(0)  # reset pointer
  #  b64 = base64.b64encode(towrite.read()).decode()  # some strings
  #  linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="myfilename.xlsx">Download excel file</a>'
  #  st.markdown(linko, unsafe_allow_html=True)


    # Adicionar botão para extrair calendário para Excel
    #if st.button("Exportar Calendário para Excel"):
    #    extract_to_excel(calendar_events)
    #    st.success("Calendário exportado com sucesso para Excel!")


    calendar = calendar(events=filtered_events, options=calendar_options, custom_css=custom_css)


if selected == "Status Gerais":

    # Criar duas colunas para o titulo da pagina
    col1_1, col2_2 = st.columns([1, 3])

    # Adicionar a imagem redimensionada
    col1_1.image(resized_image, caption='', use_column_width=False)

    # Adicionar o texto de título ao logo
    col2_2.markdown('<h1 style="flex: 1; margin: 0;">Status das Máquinas</h1>', unsafe_allow_html=True)

    # Adicionar uma linha de espaço após o título
    st.markdown("<br>", unsafe_allow_html=True)

    # Sidebar com filtros
    st.sidebar.header("Filtros")
    filtered_df, chassis_id_filter = filtros(df_historico)

    # Qtd de Chassis ID e Média de Horas Trabalhadas lado a lado
    col3, col4 = st.columns(2)

    # Qtd de Chassis ID
    if chassis_id_filter == "Todos":    
      col3.markdown("<h3 style='text-align: center;'>Quantidade de Chassis ID</h3>", unsafe_allow_html=True)
      col3.markdown(f"<p style='text-align: center; font-size: 30px;'>{len(filtered_df['Chassis'].unique())}</p>", unsafe_allow_html=True)
    else:
      col3.markdown("<h3 style='text-align: center;'>Chassi ID Selecionado</h3>", unsafe_allow_html=True)
      col3.markdown(f"<p style='text-align: center; font-size: 30px;'>{filtered_df['Chassis'].unique()}</p>", unsafe_allow_html=True)
    
    
    # Média de Horas Trabalhadas
    media_horas_trabalhadas = round(filtered_df['Horas Trabalhadas'].mean(), 2)
    col4.markdown("<h3 style='text-align: center;'>Média das Horas Trabalhadas</h3>", unsafe_allow_html=True)
    col4.markdown(f"<p style='text-align: center; font-size: 30px;'>{media_horas_trabalhadas}</p>", unsafe_allow_html=True)

    # Mapa com posições dos Chassis ID
    st.markdown("<h3>Localização das Máquinas</h3>", unsafe_allow_html=True)
    st.markdown("<p>(Altere os filtros para redirecionar a visualização do mapa)</p>", unsafe_allow_html=True)
    st.map(filtered_df)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<h3 style="flex: 1; margin: 0;">Histórico das Horas Trabalhadas</h3>', unsafe_allow_html=True)
    # Verifica se o filtro chassis_id_filter está definido como "Todos"
    if chassis_id_filter == "Todos":
      st.markdown("<p>Por favor, selecione um Chassis ID para visualizar o gráfico</p>", unsafe_allow_html=True)
    else:
    # Gráfico de evolução das Horas Trabalhadas dia a dia
      chart = alt.Chart(filtered_df).mark_line().encode(x="Data:T", y="Horas Trabalhadas:Q", color="Chassis:N",
         tooltip=["Data:T", "Horas Trabalhadas:Q", "Chassis:N"]).properties(width=800, height=400)
      st.altair_chart(chart)

    # Adicionar uma linha de espaço após o título
    st.markdown("<hr>", unsafe_allow_html=True)

    # Adicionar o texto de título ao logo
    st.markdown('<h3 style="flex: 1; margin: 0;">Tabela das Máquinas</h3>', unsafe_allow_html=True)

    # Adicionar uma linha de espaço após o título
    st.markdown("<br>", unsafe_allow_html=True)

    # Função para criar tabela com média por chassi ID
    def create_summary_table(filtered_df):
            summary_df = filtered_df.groupby('Chassis').agg({'País': 'first', 'Estado': 'first', 'Dealer': 'first', 'Segmento': 'first', 'Modelo': 'first', 'Horas Trabalhadas': 'mean'}).reset_index()
            summary_df['Horas Trabalhadas'] = round(summary_df['Horas Trabalhadas'], 2)  # Arredondar para 2 casas decimais
            return summary_df.set_index('Chassis')  # Definir 'chassi ID' como índice

    # Criar tabela com média por chassi ID
    summary_table = create_summary_table(filtered_df)
    st.dataframe(summary_table)
    
if __name__ == "__main__":
    main()