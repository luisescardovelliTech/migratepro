"""
Componente de autenticação e login.
"""

import streamlit as st
from utils.data_manager import autenticar_usuario, carregar_usuarios


def verificar_autenticacao():
    """Verifica se o usuário está autenticado. Retorna True se sim."""
    return st.session_state.get('autenticado', False)


def obter_usuario_logado():
    """Retorna os dados do usuário logado."""
    return st.session_state.get('usuario', None)


def obter_nivel_usuario():
    """Retorna o nível do usuário logado (1, 2 ou 3)."""
    usuario = obter_usuario_logado()
    return usuario.get('nivel', 1) if usuario else 0


def pode_visualizar():
    """Verifica se o usuário pode visualizar (nível >= 1)."""
    return obter_nivel_usuario() >= 1


def pode_editar():
    """Verifica se o usuário pode editar (nível >= 2)."""
    return obter_nivel_usuario() >= 2


def pode_administrar():
    """Verifica se o usuário é admin (nível == 3)."""
    return obter_nivel_usuario() == 3


def fazer_logout():
    """Realiza o logout do usuário."""
    st.session_state['autenticado'] = False
    st.session_state['usuario'] = None
    st.rerun()


def mostrar_tela_login():
    """Exibe a tela de login."""
    
    # CSS para estilizar o login
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }
        .login-title {
            text-align: center;
            font-size: 2rem;
            color: #fff;
            margin-bottom: 30px;
        }
        .login-subtitle {
            text-align: center;
            color: #8892b0;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; color: #64ffda;'>🔄 MigratePro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8892b0; margin-bottom: 30px;'>Dashboard de Migração de Dados</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
            senha = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                submitted = st.form_submit_button("Entrar", use_container_width=True, type="primary")
            
            if submitted:
                if usuario and senha:
                    user_data = autenticar_usuario(usuario, senha)
                    if user_data:
                        st.session_state['autenticado'] = True
                        st.session_state['usuario'] = user_data
                        st.success(f"Bem-vindo, {user_data['nome']}!")
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha inválidos!")
                else:
                    st.warning("⚠️ Preencha todos os campos!")
        
        st.markdown("---")


def mostrar_info_usuario():
    """Mostra informações do usuário logado na sidebar."""
    usuario = obter_usuario_logado()
    if usuario:
        nivel_nome = {1: "Visualizador", 2: "Editor", 3: "Administrador"}
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"👤 **{usuario['nome']}**")
        st.sidebar.markdown(f"🏷️ {nivel_nome.get(usuario['nivel'], 'Desconhecido')}")
        
        if st.sidebar.button("🚪 Sair", use_container_width=True, type="primary"):
            fazer_logout()
