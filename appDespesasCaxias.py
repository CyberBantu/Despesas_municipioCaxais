import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


st.set_page_config(layout="wide")

ARQUIVO = 'despesas_unificadas.csv'
st.title("📊 Despesas Unificadas de Duque de Caxias")
df = pd.read_csv(ARQUIVO)
# criando uma segunda pagina
st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Selecione a página:", ["Dashboard", "Fonte e Destinação", 'Favorecido'])

if pagina == "Dashboard":
    # Carregando os dados e Tratando err

    # adicionando filtro de Mes
    # mundando os nomes dos meses para nome completo e com primeira letra maiúscula

    col1, col2, col3 = st.columns(3)

    with col1:
        meses = df['mes'].unique()
        mes = st.selectbox("Selecione o mês:", ["Todos"] + list(meses))
        if mes == "Todos":
            df_filtrado = df
        else:
            df_filtrado = df[df['mes'] == mes]

    with col2:
        funcoes = df_filtrado['funcao'].unique()
        funcao = st.selectbox("Selecione a função:", ["Todas"] + list(funcoes))
        if funcao == "Todas":
            df_filtrado_funcao = df_filtrado
        else:
            df_filtrado_funcao = df_filtrado[df_filtrado['funcao'] == funcao]

    with col3:
        # Card com o valor total pago líquido
        valor_total = df_filtrado_funcao['valor_pago_liquido'].sum()
        valor_formatado = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        st.metric("Valor Pago Líquido Total", valor_formatado)

    # Grafico por mes -----------------------------------------

    # Criando uma linha de separação
    st.markdown("---")
    # Ordem correta dos meses
    ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    # Agrupamento
    df_gastos_mes = df_filtrado_funcao.groupby('mes')['valor_pago_liquido'].sum().reset_index()
    df_gastos_mes['valor_pago_liquido'] = df_gastos_mes['valor_pago_liquido'].round(2)

    # Transformando a coluna "mes" em categórica com ordem definida
    df_gastos_mes['mes'] = pd.Categorical(df_gastos_mes['mes'], categories=ordem_meses, ordered=True)

    # Ordenando corretamente
    df_gastos_mes = df_gastos_mes.sort_values('mes')

    import plotly.express as px

    col4, col5 = st.columns(2)
    with col4:
        # Gráfico de barras
        # Gráfico com Plotly para customização dos rótulos
        st.subheader("Gráfico de Gastos por Mês")
        fig = px.bar(
            df_gastos_mes,
            x='mes',
            y='valor_pago_liquido',
            labels={'valor_pago_liquido': 'Valor Pago Líquido (R$)'},
            text_auto='.2s'
        )
        fig.update_traces(
            texttemplate='R$ %{y:,.0f}',
            hovertemplate='Mês: %{x}<br>Valor: R$ %{y:,.0f}<extra></extra>'
        )
        fig.update_yaxes(tickformat=',.0f')
        st.plotly_chart(fig, use_container_width=True)

    with col5:
        st.subheader("Gráfico de Despesas por Função e Subfunção")
        fig = px.sunburst(
            data_frame=df_filtrado_funcao,
            path=['nome_secretria', 'subfuncao', 'funcao'],
            values='valor_pago_liquido',
            width=700,
            height=700
        )
        fig.update_traces(
            hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.0f}<extra></extra>',
            texttemplate='%{label}<br>R$ %{value:,.0f}'
        )
        st.plotly_chart(fig, use_container_width=True)



    # plotando a tabela filtrada
    st.subheader("Tabela de Despesas Detalhadas do Município de Duque de Caxias")
    st.dataframe(df_filtrado_funcao, use_container_width=True)

if pagina == "Fonte e Destinação":
    
    

    # Filtro para selecionar a função desejada
    funcoes_disponiveis = df['nome_secretria'].unique().tolist()
    funcao_selecionada = st.selectbox("Selecione a função:", ["Todas"] + funcoes_disponiveis)

    if funcao_selecionada == "Todas":
        df_filtrado_fonte = df
    else:
        df_filtrado_fonte = df[df['nome_secretria'] == funcao_selecionada]

    # Agrupa os dados filtrados por fonte e função
    df_grouped = df_filtrado_fonte.groupby(['fonte', 'nome_secretria'])['valor_pago_liquido'].sum().reset_index()

    # Cria lista única de nós
    labels = pd.unique(df_grouped[['fonte', 'nome_secretria']].values.ravel()).tolist()
    label_indices = {label: i for i, label in enumerate(labels)}

    # Lista de conexões
    fundo = df_grouped['fonte'].map(label_indices).tolist()
    objetivo = df_grouped['nome_secretria'].map(label_indices).tolist()
    value = df_grouped['valor_pago_liquido'].tolist()



    # Gráfico Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(label=labels,
                          color=['red'],
                          pad=15,
                          thickness=20),
        link=dict(source=fundo, target=objetivo, value=value,
                      color=["rgba(33, 220, 243, 0.8)" for _ in value]  # azul translúcido
)
    )])

    # Layout do gráfico
    fig.update_layout(
        width=2000,
        height=1200,
        title_text="💸 Fluxo de Recursos: Fonte → Função",
        font=dict(size=14))
    # Exibe no Streamlit

    # colocando o valor total pago líquido
    valor_total_pago = df_filtrado_fonte['valor_pago_liquido'].sum()
    valor_formatado_total = f"R$ {valor_total_pago:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.subheader("Valor Total Pago Líquido")
    st.metric("Valor Total Pago Líquido", valor_formatado_total)
    
    st.plotly_chart(fig, use_container_width=True)


if pagina == "Favorecido":
    # agregação dscrição do favorecido, junto com função e valor pago líquido
    df_favorecido = df.groupby(['CPF_CNPJ_FORMATADA','descricao_favorecido', 'funcao', 'nome_secretria', 'modalidade_licitacao'])['valor_pago_liquido'].sum().reset_index()
    # colocando um filtro de função
    funcoes_disponiveis = df_favorecido['funcao'].unique().tolist()
    funcao_selecionada = st.selectbox("Selecione a função:", ["Todas"] + funcoes_disponiveis)

    # criando uma tabela com a soma dos favorecidos em ordem decrescente
    st.subheader("Tabela de Favorecidos")
    if funcao_selecionada == "Todas":
        df_favorecido_filtrado = df_favorecido
    else:
        df_favorecido_filtrado = df_favorecido[df_favorecido['funcao'] == funcao_selecionada]
    total_pago_filtrado = df_favorecido_filtrado['valor_pago_liquido'].sum()
    df_favorecido_filtrado['percentual'] = (df_favorecido_filtrado['valor_pago_liquido'] / total_pago_filtrado * 100).round(2)
    df_favorecido_filtrado = df_favorecido_filtrado.sort_values(by='valor_pago_liquido', ascending=False)
    df_favorecido_filtrado['valor_pago_liquido'] = df_favorecido_filtrado['valor_pago_liquido'].round(2)
    df_favorecido_filtrado['valor_pago_liquido'] = df_favorecido_filtrado['valor_pago_liquido'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.dataframe(df_favorecido_filtrado, use_container_width=True)
    


