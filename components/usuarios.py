"""
CRUD de Usuários (apenas Admin).
"""

import streamlit as st
from utils.data_manager import (
    carregar_usuarios,
    criar_usuario,
    atualizar_usuario,
    excluir_usuario
)
from components.auth import pode_administrar


NIVEIS = {
    1: "Visualizador",
    2: "Editor",
    3: "Administrador"
}


def gerenciar_usuarios():
    """Página de gerenciamento de usuários."""
    
    if not pode_administrar():
        st.error("🚫 Acesso negado! Apenas administradores podem acessar esta área.")
        return
    
    st.markdown("## 👥 Gerenciamento de Usuários")
    st.markdown("<p style='color: #8892b0;'>Gerencie os usuários e seus níveis de acesso</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Lista de Usuários", "➕ Novo Usuário"])
    
    with tab1:
        listar_usuarios()
    
    with tab2:
        formulario_novo_usuario()


def listar_usuarios():
    """Lista todos os usuários."""
    
    usuarios = carregar_usuarios()
    
    # Cabeçalho da tabela
    st.markdown("""
        <div style="display: flex; background: #1e3a5f; padding: 15px; border-radius: 10px 10px 0 0; 
                    font-weight: bold; color: #fff;">
            <div style="flex: 1;">ID</div>
            <div style="flex: 2;">Usuário</div>
            <div style="flex: 2;">Nome</div>
            <div style="flex: 1;">Nível</div>
            <div style="flex: 1;">Status</div>
            <div style="flex: 1;">Ações</div>
        </div>
    """, unsafe_allow_html=True)
    
    for usuario in usuarios:
        nivel_nome = NIVEIS.get(usuario['nivel'], 'Desconhecido')
        status = "✅ Ativo" if usuario['ativo'] else "❌ Inativo"
        
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{usuario['id']}**")
            with col2:
                st.markdown(f"`{usuario['usuario']}`")
            with col3:
                st.markdown(usuario['nome'])
            with col4:
                st.markdown(nivel_nome)
            with col5:
                st.markdown(status)
            with col6:
                if usuario['usuario'] != 'admin':
                    if st.button("✏️", key=f"edit_{usuario['id']}", help="Editar"):
                        st.session_state['editar_usuario'] = usuario['id']
                        st.rerun()
                else:
                    st.markdown("🔒")
            
            st.markdown("<hr style='margin: 5px 0; border-color: #1e3a5f;'>", unsafe_allow_html=True)
    
    # Modal de edição
    if st.session_state.get('editar_usuario'):
        editar_usuario_modal(st.session_state['editar_usuario'])


def editar_usuario_modal(id_usuario: int):
    """Modal para editar usuário."""
    
    usuarios = carregar_usuarios()
    usuario = next((u for u in usuarios if u['id'] == id_usuario), None)
    
    if not usuario:
        st.session_state['editar_usuario'] = None
        return
    
    st.markdown("---")
    st.markdown(f"### ✏️ Editando: {usuario['nome']}")
    
    with st.form("form_editar_usuario"):
        nome = st.text_input("Nome", value=usuario['nome'])
        nivel = st.selectbox(
            "Nível de Acesso",
            options=[1, 2, 3],
            format_func=lambda x: NIVEIS[x],
            index=usuario['nivel'] - 1
        )
        ativo = st.checkbox("Usuário Ativo", value=usuario['ativo'])
        nova_senha = st.text_input("Nova Senha (deixe em branco para manter)", type="password")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.form_submit_button("💾 Salvar", type="primary", use_container_width=True):
                dados = {
                    'nome': nome,
                    'nivel': nivel,
                    'ativo': ativo
                }
                if nova_senha:
                    dados['senha'] = nova_senha
                
                atualizar_usuario(id_usuario, dados)
                st.session_state['editar_usuario'] = None
                st.success("✅ Usuário atualizado!")
                st.rerun()
        
        with col2:
            if st.form_submit_button("🗑️ Excluir", type="secondary", use_container_width=True):
                if excluir_usuario(id_usuario):
                    st.session_state['editar_usuario'] = None
                    st.success("🗑️ Usuário excluído!")
                    st.rerun()
                else:
                    st.error("❌ Não foi possível excluir o usuário.")
        
        with col3:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                st.session_state['editar_usuario'] = None
                st.rerun()


def formulario_novo_usuario():
    """Formulário para criar novo usuário."""
    
    st.markdown("### ➕ Criar Novo Usuário")
    
    with st.form("form_novo_usuario", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            usuario = st.text_input("👤 Nome de Usuário *", placeholder="Ex: joao.silva")
            nome = st.text_input("📝 Nome Completo *", placeholder="Ex: João da Silva")
        
        with col2:
            senha = st.text_input("🔒 Senha *", type="password")
            confirmar_senha = st.text_input("🔒 Confirmar Senha *", type="password")
        
        nivel = st.selectbox(
            "🎖️ Nível de Acesso",
            options=[1, 2, 3],
            format_func=lambda x: f"{x} - {NIVEIS[x]}",
            help="1: Apenas visualizar | 2: Visualizar e editar | 3: Acesso total"
        )
        
        st.markdown("""
            <div style="background: #1e3a5f; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <p style="color: #8892b0; margin: 0;"><strong>Níveis de Acesso:</strong></p>
                <ul style="color: #8892b0; margin: 5px 0;">
                    <li><strong>Visualizador (1):</strong> Apenas visualiza o dashboard e projetos</li>
                    <li><strong>Editor (2):</strong> Pode editar datas e observações dos projetos</li>
                    <li><strong>Administrador (3):</strong> Acesso total, incluindo criar usuários</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("✅ Criar Usuário", type="primary")
        
        if submitted:
            if not usuario or not nome or not senha:
                st.error("❌ Preencha todos os campos obrigatórios!")
            elif senha != confirmar_senha:
                st.error("❌ As senhas não coincidem!")
            elif len(senha) < 4:
                st.error("❌ A senha deve ter pelo menos 4 caracteres!")
            else:
                resultado = criar_usuario({
                    'usuario': usuario,
                    'senha': senha,
                    'nome': nome,
                    'nivel': nivel
                })
                
                if resultado:
                    st.success(f"✅ Usuário **{usuario}** criado com sucesso!")
                    st.balloons()
                else:
                    st.error("❌ Já existe um usuário com esse nome!")
