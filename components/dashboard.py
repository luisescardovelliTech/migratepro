"""
Componentes do Dashboard principal.
"""

import streamlit as st
from utils.data_manager import obter_estatisticas, carregar_projetos, calcular_carga_time
from utils.icons import get_svg
from components.charts import (
    criar_grafico_progresso,
    criar_grafico_metodos,
    criar_grafico_dificuldades,
    criar_grafico_timeline
)


def mostrar_carga_time():
    """Exibe o indicador de carga do time."""
    carga = calcular_carga_time()
    
    # Define ícone baseado no status
    icon_name = 'activity'
    if carga['status'] == 'Tranquilo':
        icon_name = 'check_circle'
    elif carga['status'] == 'Corrido':
        icon_name = 'alert_triangle'
    else:
        icon_name = 'zap'
        
    icon_svg = get_svg(icon_name, carga['cor'], 32)
    
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%); 
                    padding: 25px; border-radius: 15px; text-align: center;
                    border: 2px solid {carga['cor']}; margin-bottom: 20px;">
            <p style="color: #8892b0; margin: 0; font-size: 1rem; display: flex; align-items: center; justify-content: center; gap: 8px;">
                {get_svg('users', '#8892b0', 18)} Carga do Time
            </p>
            <h1 style="color: {carga['cor']}; margin: 15px 0; font-size: 2.5rem; display: flex; align-items: center; justify-content: center; gap: 15px;">
                {icon_svg} {carga['status']}
            </h1>
            <p style="color: {carga['cor']}; margin: 0; font-size: 1rem;">
                {carga['projetos_ativos']} projetos ativos (Não Iniciados + Em Andamento)
            </p>
            <p style="color: #8892b0; margin: 10px 0 0 0; font-size: 0.9rem;">
                {carga['descricao']}
            </p>
        </div>
    """, unsafe_allow_html=True)


def mostrar_metricas():
    """Exibe os cards com métricas resumidas."""
    stats = obter_estatisticas()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%); 
                        padding: 20px; border-radius: 15px; text-align: center;
                        border: 1px solid rgba(100, 255, 218, 0.2);">
                <p style="color: #8892b0; margin: 0; font-size: 0.9rem; display: flex; align-items: center; justify-content: center; gap: 5px;">
                    {get_svg('clock', '#8892b0', 16)} Média de Dias
                </p>
                <h2 style="color: #64ffda; margin: 5px 0;">{stats['media_dias']} <small style="font-size: 0.5em;">dias</small></h2>
                <div style="background: rgba(100, 255, 218, 0.1); border-radius: 8px; padding: 2px 8px; display: inline-block; margin-top: 5px;">
                    <span style="color: #64ffda; font-size: 0.8rem; display: flex; align-items: center; gap: 4px;">
                        {get_svg('zap', '#64ffda', 12)} Eficiência: {stats.get('eficiencia_media', 0)}%
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        cor_atrasados = "#ff6b6b" if stats['atrasados'] > 0 else "#64ffda"
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%); 
                        padding: 20px; border-radius: 15px; text-align: center;
                        border: 1px solid rgba(255, 107, 107, 0.2);">
                <p style="color: #8892b0; margin: 0; font-size: 0.9rem; display: flex; align-items: center; justify-content: center; gap: 5px;">
                    {get_svg('alert_triangle', '#8892b0', 16)} Projetos Atrasados
                </p>
                <h2 style="color: {cor_atrasados}; margin: 10px 0;">{stats['atrasados']} <small style="font-size: 0.5em;">projetos</small></h2>
                <p style="color: {'#ff6b6b' if stats['atrasados'] > 0 else '#64ffda'}; margin: 0; font-size: 0.8rem;">
                    {'Atenção Crítica' if stats['atrasados'] > 0 else 'Tudo em dia'}
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%); 
                        padding: 20px; border-radius: 15px; text-align: center;
                        border: 1px solid rgba(100, 255, 218, 0.2);">
                <p style="color: #8892b0; margin: 0; font-size: 0.9rem; display: flex; align-items: center; justify-content: center; gap: 5px;">
                    {get_svg('check_circle', '#8892b0', 16)} Total Concluído
                </p>
                <h2 style="color: #64ffda; margin: 10px 0;">{stats['concluidos']}<small style="font-size: 0.5em; color: #8892b0;">/{stats['total']}</small></h2>
                <p style="color: #38bdf8; margin: 0; font-size: 0.8rem;">{stats['percentual_concluido']}% concluído</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%); 
                        padding: 20px; border-radius: 15px; text-align: center;
                        border: 1px solid rgba(255, 217, 61, 0.2);">
                <p style="color: #8892b0; margin: 0; font-size: 0.9rem; display: flex; align-items: center; justify-content: center; gap: 5px;">
                    {get_svg('refresh_cw', '#8892b0', 16)} Em Andamento
                </p>
                <h2 style="color: #ffd93d; margin: 10px 0;">{stats['em_andamento']} <small style="font-size: 0.5em;">projetos</small></h2>
                <p style="color: #ffd93d; margin: 0; font-size: 0.8rem;">ativos agora</p>
            </div>
        """, unsafe_allow_html=True)


def mostrar_progresso_projetos():
    """Exibe a seção de progresso dos projetos."""
    projetos = carregar_projetos()
    
    st.markdown("### 📈 Progresso da Migração")
    st.markdown("<p style='color: #8892b0;'>Progresso real vs compromissos de prazo</p>", unsafe_allow_html=True)
    
    fig = criar_grafico_progresso(projetos)
    st.plotly_chart(fig, key="chart_progresso", config={'displayModeBar': False})


def mostrar_insights():
    """Exibe o painel de insights."""
    stats = obter_estatisticas()
    
    st.markdown("### 💡 Insights da Migração")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_metodos = criar_grafico_metodos(stats['metodos'])
        st.plotly_chart(fig_metodos, key="chart_metodos", config={'displayModeBar': False})
    
    with col2:
        fig_dificuldades = criar_grafico_dificuldades(stats['dificuldades'])
        st.plotly_chart(fig_dificuldades, key="chart_dificuldades", config={'displayModeBar': False})


def mostrar_timeline():
    """Exibe o gráfico de timeline."""
    projetos = carregar_projetos()
    
    st.markdown("### 📅 Timeline dos Projetos")
    
    fig = criar_grafico_timeline(projetos)
    st.plotly_chart(fig, key="chart_timeline", config={'displayModeBar': False})


def mostrar_dashboard():
    """Exibe o dashboard completo."""
    st.markdown("## 📊 Dashboard de Insights de Migração")
    st.markdown("<p style='color: #8892b0;'>Acompanhamento em tempo real e análise estratégica de migrações</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Indicador de Carga do Time (NOVO!)
    mostrar_carga_time()
    
    # Métricas
    mostrar_metricas()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Progresso e Insights lado a lado
    col1, col2 = st.columns([2, 1])
    
    with col1:
        mostrar_progresso_projetos()
    
    with col2:
        mostrar_insights()
    
    st.markdown("---")
    
    # Timeline
    mostrar_timeline()
