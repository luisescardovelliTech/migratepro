"""
Componente de autenticação e login.
Usa Supabase para armazenar sessões de usuários.
Funciona corretamente com múltiplos usuários no Streamlit Cloud.
"""

import streamlit as st
from utils.data_manager import autenticar_usuario, carregar_usuarios, get_supabase_client
import datetime
import uuid


# Configurações
SESSION_EXPIRY_DAYS = 7
SESSION_PARAM_NAME = 'session'


def _criar_sessao(usuario_id: int, usuario: str, senha: str) -> str:
    """Cria uma nova sessão no Supabase e retorna o token."""
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        token = str(uuid.uuid4())
        expira = (datetime.datetime.now() + datetime.timedelta(days=SESSION_EXPIRY_DAYS)).isoformat()
        
        # Insere ou atualiza sessão
        client.table('sessoes').upsert({
            'token': token,
            'usuario_id': usuario_id,
            'usuario': usuario,
            'senha': senha,
            'expira_em': expira
        }).execute()
        
        return token
    except Exception as e:
        # Se a tabela não existir, cria ela
        try:
            client.rpc('create_sessoes_table').execute()
        except:
            pass
        return None


def _validar_sessao(token: str) -> dict:
    """Valida uma sessão pelo token e retorna dados do usuário."""
    if not token:
        return None
    
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        response = client.table('sessoes').select('*').eq('token', token).execute()
        
        if response.data:
            sessao = response.data[0]
            
            # Verifica se não expirou
            expira = datetime.datetime.fromisoformat(sessao['expira_em'].replace('Z', '+00:00').replace('+00:00', ''))
            if datetime.datetime.now() > expira:
                _remover_sessao(token)
                return None
            
            # Autentica usuário para obter dados atualizados
            user_data = autenticar_usuario(sessao['usuario'], sessao['senha'])
            return user_data
    except Exception as e:
        pass
    
    return None


def _remover_sessao(token: str):
    """Remove uma sessão do Supabase."""
    if not token:
        return
    
    client = get_supabase_client()
    if not client:
        return
    
    try:
        client.table('sessoes').delete().eq('token', token).execute()
    except:
        pass


def verificar_autenticacao():
    """Verifica se o usuário está autenticado. Retorna True se sim."""
    # Se já está autenticado na sessão atual, retorna True
    if st.session_state.get('autenticado', False):
        return True
    
    # Verifica se há token de sessão na URL
    token = st.query_params.get(SESSION_PARAM_NAME)
    
    if token:
        user_data = _validar_sessao(token)
        if user_data:
            st.session_state['autenticado'] = True
            st.session_state['usuario'] = user_data
            st.session_state['session_token'] = token
            return True
        else:
            # Token inválido, limpa query params
            st.query_params.clear()
    
    return False


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
    # Remove sessão do banco
    token = st.session_state.get('session_token')
    if token:
        _remover_sessao(token)
    
    st.session_state['autenticado'] = False
    st.session_state['usuario'] = None
    st.session_state['session_token'] = None
    st.query_params.clear()
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
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; color: #64ffda;'>🔄 MigratePro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8892b0; margin-bottom: 30px;'>Dashboard de Migração de Dados</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
            senha = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha")
            manter_conectado = st.checkbox("Manter conectado")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                submitted = st.form_submit_button("Entrar", use_container_width=True, type="primary")
            
            if submitted:
                if usuario and senha:
                    user_data = autenticar_usuario(usuario, senha)
                    if user_data:
                        st.session_state['autenticado'] = True
                        st.session_state['usuario'] = user_data
                        
                        if manter_conectado:
                            # Cria sessão no Supabase
                            token = _criar_sessao(user_data['id'], usuario, senha)
                            if token:
                                st.session_state['session_token'] = token
                                st.query_params[SESSION_PARAM_NAME] = token
                            
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

