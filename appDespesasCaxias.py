import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


st.set_page_config(layout="wide")

ARQUIVO = 'despesas_unificadas.csv'
st.title("📊 Despesas Unificadas de Duque de Caxias")
st.markdown("""
Este aplicativo foi desenvolvido por [Christian Basilio](https://www.linkedin.com/in/christianbasilioo/) para visualizar as despesas unificadas de Duque de Caxias.
**As despesas são os gastos declarados pela Prefeitura.**
""")
st.markdown("""**Ultima atualização: 24 de junho de 2025. -- Dados do Ano de 2025 até a ultima atualização -- Recomenda-se o uso no modo escuro do Streamlit para melhor visualização.**""")
st.write('No menu de navegação no lado esquerdo, selecione a página de visualização desejada.')
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



    col4, col5 = st.columns(2)
    with col4:
        # Gráfico de barras
        # Gráfico com Plotly para customização dos rótulos
        st.subheader("Despesas por Mês")
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
        st.subheader("Despesas por Função e Subfunção")
        st.markdown("""**Instruções - Interaja com o clique na area de interesse no gráfico para aprofundar os dados, para retornar basta clicar no centro do gráfico para voltar.** Acompanhe os valores pelo hover do mouse, basta passar o mouse por cima.""")
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


    # agregação por PROGRAMA
    df_programa = df_filtrado_funcao.groupby(['PROGRAMA', 'nome_secretria'])['valor_pago_liquido'].sum().reset_index()
    df_programa['valor_pago_liquido'] = df_programa['valor_pago_liquido'].round(2)
    # Ordenando o DataFrame por valor pago líquido em ordem decrescente
    df_programa = df_programa.sort_values(by='valor_pago_liquido', ascending=False)
    # Criando uma tabela com a soma dos programas em ordem decrescente
    st.subheader("Programas e Valores Pagos Líquidos")
    df_programa['percentual'] = (df_programa['valor_pago_liquido'] / valor_total * 100).round(2)
    df_programa = df_programa.rename(columns={'valor_pago_liquido': 'Valor Pago Líquido'})
    df_programa = df_programa[['PROGRAMA', 'nome_secretria', 'Valor Pago Líquido', 'percentual']]
    st.dataframe(df_programa, use_container_width=True)

    # plotando a tabela filtrada
    st.subheader("Despesas Detalhadas do Município de Duque de Caxias")
    st.dataframe(df_filtrado_funcao, use_container_width=True)

if pagina == "Fonte e Destinação":
    # Filtro para selecionar a secretaria e valor total na mesma linha
    col1, col2 = st.columns([2, 1])
    with col1:
        funcoes_disponiveis = df['nome_secretria'].dropna().unique().tolist()
        funcao_selecionada = st.selectbox("**Selecione a secretaria:**", ["Todas"] + funcoes_disponiveis)
    with col2:
        if funcao_selecionada == "Todas":
            valor_total_pago = df['valor_pago_liquido'].sum()
        else:
            valor_total_pago = df[df['nome_secretria'] == funcao_selecionada]['valor_pago_liquido'].sum()
        valor_formatado_total = f"R$ {valor_total_pago:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        st.metric("Valor Total Pago Líquido", valor_formatado_total)

    if funcao_selecionada == "Todas":
        df_filtrado_fonte = df.copy()
    else:
        df_filtrado_fonte = df[df['nome_secretria'] == funcao_selecionada]

    # Agrupa os dados por fonte e secretaria
    df_grouped = df_filtrado_fonte.groupby(['fonte', 'nome_secretria'])['valor_pago_liquido'].sum().reset_index()

    # Cria lista única de nós
    labels = pd.unique(df_grouped[['fonte', 'nome_secretria']].values.ravel()).tolist()
    label_indices = {label: i for i, label in enumerate(labels)}

    # Mapeia os índices
    fundo = df_grouped['fonte'].map(label_indices).tolist()
    objetivo = df_grouped['nome_secretria'].map(label_indices).tolist()
    value = df_grouped['valor_pago_liquido'].tolist()

    # Detecta o tema do Streamlit
    modo_escuro = st.get_option("theme.base") == "dark"
    cor_texto = "white" if modo_escuro else "black"
    cor_fundo = "#1E1E1E" if modo_escuro else "white"

    # Cores dos nós (verde para fontes, azul para secretarias)
    node_colors = ["#4CAF50" if i < len(df_grouped['fonte'].unique()) else "#2196F3" for i in range(len(labels))]

    # Gráfico Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            label=labels,
            color=node_colors,
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5)
        ),
        link=dict(
            source=fundo,
            target=objetivo,
            value=value,
            color=["rgba(33, 150, 243, 0.5)" for _ in value]
        )
    )])

    # Layout do gráfico
    fig.update_layout(
        width=1400,
        height=1400,
        title_text="💸 Fluxo de Recursos: Fonte → Secretaria",
        font=dict(size=16, color=cor_texto),
        paper_bgcolor=cor_fundo,
        plot_bgcolor=cor_fundo,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    # Explicação
    st.markdown("""
    ### 📊 Explicação sobre o Gráfico
    O gráfico Sankey ilustra o fluxo de recursos financeiros, mostrando como as **fontes de financiamento** se conectam às **secretarias municipais**.

    As setas representam a quantidade de recursos transferidos de cada fonte para cada secretaria, e o **tamanho das conexões é proporcional ao valor** transferido.

    Isso permite identificar visualmente quais fontes financiam mais cada área do governo.
    """)

    # Exibe o gráfico
    st.plotly_chart(fig, use_container_width=True)

if pagina == "Favorecido":
    # Agregação: favorecido, função e valor
    df_favorecido = df.groupby([
        'CPF_CNPJ_FORMATADA', 'descricao_favorecido', 'funcao', 'nome_secretria','descricao_elemento_despesa', 'modalidade_licitacao', 
    ])['valor_pago_liquido'].sum().reset_index()

    # Filtros em colunas lado a lado
    col1, col2, col3 = st.columns(3)
    with col1:
        funcoes_disponiveis = df_favorecido['funcao'].unique().tolist()
        funcao_selecionada = st.selectbox("Selecione a função:", ["Todas"] + funcoes_disponiveis)
    with col2:
        favorecidos_disponiveis = df_favorecido['descricao_favorecido'].unique().tolist()
        favorecido_selecionado = st.selectbox("Selecione o favorecido:", ["Todos"] + favorecidos_disponiveis)
    with col3:
        modalidades_disponiveis = df_favorecido['modalidade_licitacao'].unique().tolist()
        modalidade_selecionada = st.selectbox("Selecione a modalidade de licitação:", ["Todas"] + modalidades_disponiveis)

    # Aplicar filtros
    df_favorecido_filtrado = df_favorecido.copy()
    if funcao_selecionada != "Todas":
        df_favorecido_filtrado = df_favorecido_filtrado[df_favorecido_filtrado['funcao'] == funcao_selecionada]
    if favorecido_selecionado != "Todos":
        df_favorecido_filtrado = df_favorecido_filtrado[df_favorecido_filtrado['descricao_favorecido'] == favorecido_selecionado]
    if modalidade_selecionada != "Todas":
        df_favorecido_filtrado = df_favorecido_filtrado[df_favorecido_filtrado['modalidade_licitacao'] == modalidade_selecionada]

    # Valor total após filtros
    total_pago_filtrado = df_favorecido_filtrado['valor_pago_liquido'].sum()
    valor_total_formatado = f"R$ {total_pago_filtrado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.metric("Valor Pago Líquido Total (após filtros)", valor_total_formatado)

    # Cálculo de percentual
    df_favorecido_filtrado['percentual'] = (df_favorecido_filtrado['valor_pago_liquido'] / total_pago_filtrado * 100).round(2)

    # Ordena e formata valores
    df_favorecido_filtrado = df_favorecido_filtrado.sort_values(by='valor_pago_liquido', ascending=False)
    df_favorecido_filtrado['valor_pago_liquido_formatado'] = df_favorecido_filtrado['valor_pago_liquido'].round(2)
    df_favorecido_filtrado['valor_pago_liquido_formatado'] = df_favorecido_filtrado['valor_pago_liquido_formatado'].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    st.subheader("Tabela Detalhada de Favorecidos")
    st.dataframe(df_favorecido_filtrado.drop(columns='valor_pago_liquido'), use_container_width=True)

    st.subheader("Totais por Elemento de Despesa")
    df_elemento = df_favorecido_filtrado.groupby('descricao_elemento_despesa')['valor_pago_liquido'].sum().reset_index()
    df_elemento = df_elemento.sort_values(by='valor_pago_liquido', ascending=False)
    total_elemento = df_elemento['valor_pago_liquido'].sum()
    df_elemento['percentual'] = (df_elemento['valor_pago_liquido'] / total_elemento * 100).round(2)
    df_elemento['valor_pago_liquido'] = df_elemento['valor_pago_liquido'].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    df_elemento = df_elemento.rename(columns={
        'descricao_elemento_despesa': 'Elemento de Despesa',
        'valor_pago_liquido': 'Valor Pago Líquido',
        'percentual': 'Percentual (%)'
    })
    st.dataframe(df_elemento, use_container_width=True)

    st.subheader("Top 10 Favorecidos por Valor Pago Líquido")
    df_top10_favorecidos = df_favorecido_filtrado.nlargest(10, 'valor_pago_liquido')
    fig = go.Figure(data=[go.Bar(
        x=df_top10_favorecidos['descricao_favorecido'],
        y=df_top10_favorecidos['valor_pago_liquido'],
        text=[f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") for v in df_top10_favorecidos['valor_pago_liquido']],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Valor Pago Líquido: R$ %{y:,.2f}<extra></extra>',
    )])
    fig.update_layout(
        title_text="Top 10 Favorecidos por Valor Pago Líquido",
        xaxis_title="Favorecido",
        yaxis_title="Valor Pago Líquido",
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)
