"""
MigratePro - Dashboard de Migração de Dados
Aplicação principal Streamlit
"""

import streamlit as st
import os
import sys

# Adiciona o diretório raiz ao path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from components.auth import (
    verificar_autenticacao,
    mostrar_tela_login,
    mostrar_info_usuario,
    pode_visualizar,
    pode_editar,
    pode_administrar
)
from components.dashboard import mostrar_dashboard
from components.crud import formulario_novo_projeto, tabela_projetos
from components.usuarios import gerenciar_usuarios


# Configuração da página
st.set_page_config(
    page_title="MigratePro - Dashboard de Migração",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado para tema escuro premium
st.markdown("""
<style>
    /* Tema escuro base */
    .stApp {
        background: linear-gradient(135deg, #0a192f 0%, #112240 50%, #0a192f 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1b2a 0%, #1b2838 100%);
        border-right: 1px solid rgba(100, 255, 218, 0.1);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #8892b0;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ccd6f6 !important;
    }
    
    h1 {
        background: linear-gradient(90deg, #64ffda, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Cards e containers */
    .stExpander {
        background: rgba(17, 34, 64, 0.8);
        border: 1px solid rgba(100, 255, 218, 0.1);
        border-radius: 15px;
    }
    
    .stExpander > div > div > div > div {
        color: #8892b0;
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background: rgba(17, 34, 64, 0.8) !important;
        border: 1px solid rgba(100, 255, 218, 0.2) !important;
        color: #ccd6f6 !important;
        border-radius: 10px;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #64ffda !important;
        box-shadow: 0 0 10px rgba(100, 255, 218, 0.2);
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #64ffda 0%, #38bdf8 100%);
        color: #0a192f;
        border: none;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(100, 255, 218, 0.3);
    }
    
    .stButton > button[kind="secondary"] {
        background: transparent;
        border: 2px solid #64ffda;
        color: #64ffda;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(17, 34, 64, 0.5);
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #8892b0;
        border-radius: 8px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #64ffda 0%, #38bdf8 100%);
        color: #0a192f;
    }
    
    /* Checkbox */
    .stCheckbox > label > div {
        color: #8892b0;
    }
    
    /* Dividers */
    hr {
        border-color: rgba(100, 255, 218, 0.1);
    }
    
    /* Mensagens */
    .stSuccess {
        background: rgba(100, 255, 218, 0.1);
        border: 1px solid #64ffda;
    }
    
    .stError {
        background: rgba(255, 107, 107, 0.1);
        border: 1px solid #ff6b6b;
    }
    
    .stWarning {
        background: rgba(255, 217, 61, 0.1);
        border: 1px solid #ffd93d;
    }
    
    .stInfo {
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid #38bdf8;
    }
    
    /* Date input */
    .stDateInput > div > div > input {
        background: rgba(17, 34, 64, 0.8) !important;
        border: 1px solid rgba(100, 255, 218, 0.2) !important;
        color: #ccd6f6 !important;
        border-radius: 10px;
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        background: rgba(17, 34, 64, 0.8) !important;
        border: 1px solid rgba(100, 255, 218, 0.2) !important;
        border-radius: 10px;
    }
    
    .stMultiSelect span {
        background: #64ffda !important;
        color: #0a192f !important;
    }
    
    /* Forms */
    [data-testid="stForm"] {
        background: rgba(17, 34, 64, 0.5);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(100, 255, 218, 0.1);
    }
    
    /* Plotly charts background */
    .js-plotly-plot .plotly .bg {
        fill: transparent !important;
    }
    
    /* Menu navigation styling */
    .nav-link {
        display: flex;
        align-items: center;
        padding: 12px 20px;
        margin: 5px 0;
        border-radius: 10px;
        color: #8892b0;
        text-decoration: none;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .nav-link:hover {
        background: rgba(100, 255, 218, 0.1);
        color: #64ffda;
    }
    
    .nav-link.active {
        background: linear-gradient(135deg, rgba(100, 255, 218, 0.2) 0%, rgba(56, 189, 248, 0.2) 100%);
        color: #64ffda;
        border-left: 3px solid #64ffda;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Função principal da aplicação."""
    
    # Verifica se está autenticado
    if not verificar_autenticacao():
        mostrar_tela_login()
        return
    
    # Sidebar com navegação
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 20px 0;">
                <h1 style="font-size: 1.8rem; margin: 0;">🔄 MigratePro</h1>
                <p style="color: #8892b0; font-size: 0.9rem;">Dashboard de Migração</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Menu de navegação
        menu_options = ["📊 Visão Geral", "📋 Todos os Projetos"]
        
        if pode_editar():
            menu_options.append("➕ Novo Projeto")
        
        if pode_administrar():
            menu_options.append("👥 Usuários")
        
        pagina = st.radio(
            "Navegação",
            menu_options,
            label_visibility="collapsed"
        )
        
        # Info do usuário no final da sidebar
        mostrar_info_usuario()
    
    # Conteúdo principal baseado na página selecionada
    if pagina == "📊 Visão Geral":
        mostrar_dashboard()
    
    elif pagina == "📋 Todos os Projetos":
        tabela_projetos()
    
    elif pagina == "➕ Novo Projeto":
        formulario_novo_projeto()
    
    elif pagina == "👥 Usuários":
        gerenciar_usuarios()


if __name__ == "__main__":
    main()
