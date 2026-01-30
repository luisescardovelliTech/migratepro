"""
CRUD de Projetos de Migração.
"""

import streamlit as st
from datetime import datetime, date
from utils.data_manager import (
    carregar_projetos,
    criar_projeto,
    atualizar_projeto,
    excluir_projeto,
    buscar_projeto,
    calcular_dificuldade,
    carregar_usuarios
)
from components.auth import pode_editar, pode_administrar


# Opções padrão
METODOS_MIGRACAO = ['Script', 'Manual', 'Manual + Script']


def formatar_data(data_str: str) -> str:
    """Converte data de YYYY-MM-DD para DD/MM/YYYY."""
    if not data_str:
        return 'N/D'
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d')
        return data.strftime('%d/%m/%Y')
    except:
        return data_str


def formulario_novo_projeto():
    """Exibe o formulário para criar novo projeto."""
    
    if not pode_editar():
        st.warning("⚠️ Você não tem permissão para criar projetos.")
        return
    
    st.markdown("## Novo Projeto de Migração")
    st.markdown("<p style='color: #8892b0;'>Cadastre um novo projeto de migração de dados</p>", unsafe_allow_html=True)
    
    with st.form("form_novo_projeto", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome do Projeto *", placeholder="Ex: Migração Servidor Alpha")
            data_inicio = st.date_input("Data de Início", value=date.today(), format="DD/MM/YYYY")
            metodo = st.selectbox("Método de Migração", METODOS_MIGRACAO)
        
        with col2:
            data_prazo = st.date_input("Prazo de Entrega", value=None, format="DD/MM/YYYY")
            dias_estimados = st.number_input(
                "Estimativa de Dias",
                min_value=1,
                max_value=365,
                value=30,
                help="Quantos dias você estima para concluir a migração?"
            )
            
            # Carregar usuários para seleção (Apenas nível >= 2 - Editores/Admins)
            usuarios = carregar_usuarios()
            editores = [u['usuario'] for u in usuarios if u['nivel'] >= 2]
            
            responsaveis = st.multiselect(
                "Responsáveis do Time",
                options=editores,
                placeholder="Selecione os membros do time..."
            )
            
            backup_recebido = st.checkbox("Backup Recebido", value=False)
        
        st.markdown("---")
        
        dificuldades = st.text_area(
            "Dificuldades Encontradas",
            placeholder="Descreva as dificuldades encontradas durante a migração...",
            height=100
        )
        
        observacoes = st.text_area(
            "Observações",
            placeholder="Notas adicionais sobre o projeto, problemas encontrados, plano de ação...",
            height=100
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            submitted = st.form_submit_button("Criar Projeto", type="primary", use_container_width=True)
        
        if submitted:
            if not nome:
                st.error("O nome do projeto é obrigatório!")
            else:
                dados = {
                    'nome': nome,
                    'data_inicio': str(data_inicio) if data_inicio else None,
                    'data_prazo': str(data_prazo) if data_prazo else None,
                    'dias_estimados': dias_estimados,
                    'metodo_migracao': metodo,
                    'backup_recebido': backup_recebido,
                    'dificuldades': dificuldades,
                    'observacoes': observacoes,
                    'responsaveis': responsaveis
                }
                
                projeto = criar_projeto(dados)
                st.success(f"Projeto **{projeto['id']}** criado com sucesso!")
                st.balloons()


def tabela_projetos():
    """Exibe a tabela de projetos com opções de edição."""
    
    st.markdown("## Todos os Projetos")
    st.markdown("<p style='color: #8892b0;'>Gerencie cronogramas, integridade de dados e observações qualitativas</p>", unsafe_allow_html=True)
    
    projetos = carregar_projetos()
    
    if not projetos:
        st.info("Nenhum projeto cadastrado ainda. Crie o primeiro projeto!")
        return
    
    # Filtros
    col_filtro1, col_filtro2, col_filtro3 = st.columns([2, 1, 1])
    
    with col_filtro1:
        busca = st.text_input("Buscar", placeholder="Buscar por nome ou ID...")
    
    with col_filtro2:
        status_filtro = st.selectbox("Status", ['Todos', 'Em Andamento', 'Concluído', 'Atrasado'])
    
    with col_filtro3:
        metodo_filtro = st.selectbox("Método", ['Todos'] + METODOS_MIGRACAO)
    
    # Aplica filtros
    projetos_filtrados = projetos.copy()
    
    if busca:
        projetos_filtrados = [
            p for p in projetos_filtrados 
            if busca.lower() in p['nome'].lower() or busca.lower() in p['id'].lower()
        ]
    
    if status_filtro != 'Todos':
        projetos_filtrados = [
            p for p in projetos_filtrados 
            if status_filtro in p.get('status', '')
        ]
    
    if metodo_filtro != 'Todos':
        projetos_filtrados = [
            p for p in projetos_filtrados 
            if p.get('metodo_migracao') == metodo_filtro
        ]
    
    st.markdown(f"<p style='color: #8892b0;'>Mostrando {len(projetos_filtrados)} de {len(projetos)} projetos</p>", unsafe_allow_html=True)
    
    # Lista de projetos
    # Lista de projetos
    for projeto in projetos_filtrados:
        dias_est = projeto.get('dias_estimados', 30)
        dif = calcular_dificuldade(dias_est)
        
        # Define ícone visual para o status (apenas visualização limpa no título)
        status_proj = projeto.get('status', 'N/D')
        
        with st.expander(f"**{projeto['nome']}** | {dif['nivel']} | {status_proj}", expanded=False):
            mostrar_detalhes_projeto(projeto)


def mostrar_detalhes_projeto(projeto: dict):
    """Mostra os detalhes de um projeto com opções de edição."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Informações")
        
        # Se pode editar, mostra campos editáveis
        if pode_editar():
            with st.form(f"form_editar_{projeto['id']}"):
                nome = st.text_input("Nome", value=projeto['nome'])
                
                # Data Início e Lógica de Início
                data_inicio_val = None
                is_iniciado = False
                
                if projeto.get('data_inicio'):
                    try:
                        data_inicio_val = datetime.strptime(projeto['data_inicio'], '%Y-%m-%d').date()
                        is_iniciado = True
                    except:
                        pass
                
                marcar_iniciado = st.checkbox("Marcar como Iniciado", value=is_iniciado, help="Ativa a data de início do projeto")
                
                data_inicio = None
                if marcar_iniciado:
                    if not data_inicio_val:
                        data_inicio_val = date.today()
                    data_inicio = st.date_input("Data Início", value=data_inicio_val, format="DD/MM/YYYY")
                else:
                    data_inicio = None
                
                data_prazo_val = None
                if projeto.get('data_prazo'):
                    try:
                        data_prazo_val = datetime.strptime(projeto['data_prazo'], '%Y-%m-%d').date()
                    except:
                        pass
                data_prazo = st.date_input("Prazo", value=data_prazo_val, format="DD/MM/YYYY")
                
                dias_estimados = st.number_input(
                    "Estimativa de Dias",
                    min_value=1,
                    max_value=365,
                    value=projeto.get('dias_estimados', 30),
                    help="Quantos dias você estima para concluir a migração?"
                )
                
                # Data Fim e Lógica de Conclusão
                data_fim_val = None
                is_concluido = False
                
                if projeto.get('data_fim'):
                    try:
                        data_fim_val = datetime.strptime(projeto['data_fim'], '%Y-%m-%d').date()
                        is_concluido = True
                    except:
                        pass
                
                marcar_concluido = st.checkbox("Marcar como Concluído", value=is_concluido, help="Ativa a data de conclusão")
                
                data_fim = None
                if marcar_concluido:
                    if not data_fim_val:
                        data_fim_val = date.today()
                    data_fim = st.date_input("Data Conclusão", value=data_fim_val, format="DD/MM/YYYY")
                else:
                    data_fim = None
                
                metodo = st.selectbox(
                    "Método de Migração",
                    METODOS_MIGRACAO,
                    index=METODOS_MIGRACAO.index(projeto.get('metodo_migracao', 'Manual')) if projeto.get('metodo_migracao') in METODOS_MIGRACAO else 0
                )
                
                backup = st.checkbox("Backup Recebido", value=projeto.get('backup_recebido', False))
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    salvar = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                with col_btn2:
                    if pode_administrar():
                        excluir = st.form_submit_button("Excluir", type="secondary", use_container_width=True)
                    else:
                        excluir = False
                
                if salvar:
                    dados = {
                        'nome': nome,
                        'data_inicio': str(data_inicio) if data_inicio else None,
                        'data_prazo': str(data_prazo) if data_prazo else None,
                        'data_fim': str(data_fim) if data_fim else None,
                        'dias_estimados': dias_estimados,
                        'metodo_migracao': metodo,
                        'backup_recebido': backup
                    }
                    atualizar_projeto(projeto['id'], dados)
                    st.success("Projeto atualizado!")
                    st.rerun()
                
                if excluir:
                    excluir_projeto(projeto['id'])
                    st.success("Projeto excluído!")
                    st.rerun()
        else:
            # Somente visualização
            st.markdown(f"**Nome:** {projeto['nome']}")
            st.markdown(f"**Data Início:** {formatar_data(projeto.get('data_inicio'))}")
            st.markdown(f"**Prazo:** {formatar_data(projeto.get('data_prazo'))}")
            st.markdown(f"**Estimativa:** {projeto.get('dias_estimados', 'N/D')} dias")
            st.markdown(f"**Data Conclusão:** {formatar_data(projeto.get('data_fim'))}")
            st.markdown(f"**Método:** {projeto.get('metodo_migracao', 'N/D')}")
            st.markdown(f"**Backup:** {'Recebido' if projeto.get('backup_recebido') else 'Não recebido'}")
    
    with col2:
        st.markdown("#### Dificuldades e Observações")
        
        if pode_editar():
            with st.form(f"form_obs_{projeto['id']}"):
                dificuldades = st.text_area(
                    "Dificuldades",
                    value=projeto.get('dificuldades', ''),
                    height=100,
                    placeholder="Descreva as dificuldades encontradas..."
                )
                
                observacoes = st.text_area(
                    "Observações",
                    value=projeto.get('observacoes', ''),
                    height=100,
                    placeholder="Descreva os problemas encontrados, plano de ação, notas importantes..."
                )
                
                # Edição de responsáveis
                usuarios = carregar_usuarios()
                editores = [u['usuario'] for u in usuarios if u['nivel'] >= 2]
                responsaveis_atuais = projeto.get('responsaveis', [])
                # Garante que é uma lista, o Supabase pode retornar None
                if not isinstance(responsaveis_atuais, list):
                    responsaveis_atuais = []
                
                # Garante que os responsáveis atuais estejam na lista de opções
                opcoes = list(set(editores + responsaveis_atuais))
                
                responsaveis = st.multiselect(
                    "Responsáveis",
                    options=opcoes,
                    default=responsaveis_atuais,
                    placeholder="Selecione os responsáveis..."
                )
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("Salvar Notas", type="primary", use_container_width=True):
                        dados = {
                            'dificuldades': dificuldades,
                            'observacoes': observacoes,
                            'responsaveis': responsaveis
                        }
                        atualizar_projeto(projeto['id'], dados)
                        st.success("Notas e responsáveis salvos!")
                        st.rerun()
        else:
            responsaveis = projeto.get('responsaveis', [])
            if responsaveis:
                st.markdown(f"**Responsáveis:** {', '.join(responsaveis)}")
                
            st.markdown(f"**Dificuldades:** {projeto.get('dificuldades', 'Nenhuma registrada')}")
            st.markdown(f"**Observações:** {projeto.get('observacoes', 'Sem observações')}")
    
    # Análise de performance
    st.markdown("---")
    st.markdown("#### Análise de Performance")
    
    dias_estimados = projeto.get('dias_estimados', 0)
    data_inicio_str = projeto.get('data_inicio')
    data_prazo_str = projeto.get('data_prazo')
    data_fim_str = projeto.get('data_fim')
    
    col_perf1, col_perf2, col_perf3, col_perf4 = st.columns(4)
    
    # Dias do prazo (prazo - início)
    dias_prazo = 0
    if data_inicio_str and data_prazo_str:
        try:
            inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            prazo = datetime.strptime(data_prazo_str, '%Y-%m-%d').date()
            dias_prazo = (prazo - inicio).days
        except:
            pass
    
    # Dias reais (fim - início) ou dias corridos
    dias_reais = 0
    if data_inicio_str:
        try:
            inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            if data_fim_str:
                fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            else:
                fim = date.today()
            dias_reais = (fim - inicio).days
        except:
            pass
    
    with col_perf1:
        st.markdown(f"""
            <div style="background: #1e3a5f; padding: 15px; border-radius: 10px; text-align: center;">
                <p style="color: #8892b0; margin: 0; font-size: 0.8rem;">📊 Estimativa</p>
                <h3 style="color: #64ffda; margin: 5px 0;">{dias_estimados} dias</h3>
            </div>
        """, unsafe_allow_html=True)
    
    with col_perf2:
        st.markdown(f"""
            <div style="background: #1e3a5f; padding: 15px; border-radius: 10px; text-align: center;">
                <p style="color: #8892b0; margin: 0; font-size: 0.8rem;">⏰ Prazo Total</p>
                <h3 style="color: #38bdf8; margin: 5px 0;">{dias_prazo} dias</h3>
            </div>
        """, unsafe_allow_html=True)
    
    with col_perf3:
        cor_dias = "#64ffda" if dias_reais <= dias_estimados else "#ffd93d" if dias_reais <= dias_prazo else "#ff6b6b"
        label_dias = "Dias Reais" if data_fim_str else "Dias Corridos"
        st.markdown(f"""
            <div style="background: #1e3a5f; padding: 15px; border-radius: 10px; text-align: center;">
                <p style="color: #8892b0; margin: 0; font-size: 0.8rem;">📅 {label_dias}</p>
                <h3 style="color: {cor_dias}; margin: 5px 0;">{dias_reais} dias</h3>
            </div>
        """, unsafe_allow_html=True)
    
    with col_perf4:
        # Margem: diferença entre prazo e dias reais
        if data_fim_str:
            margem = dias_prazo - dias_reais
            cor_margem = "#64ffda" if margem >= 0 else "#ff6b6b"
            texto_margem = f"+{margem}" if margem >= 0 else str(margem)
            label_margem = "Margem" if margem >= 0 else "Atraso"
        else:
            margem = dias_prazo - dias_reais
            cor_margem = "#64ffda" if margem >= 0 else "#ff6b6b"
            texto_margem = f"+{margem}" if margem >= 0 else str(margem)
            label_margem = "Dias Restantes"
        
        st.markdown(f"""
            <div style="background: #1e3a5f; padding: 15px; border-radius: 10px; text-align: center;">
                <p style="color: #8892b0; margin: 0; font-size: 0.8rem;">🎯 {label_margem}</p>
                <h3 style="color: {cor_margem}; margin: 5px 0;">{texto_margem} dias</h3>
            </div>
        """, unsafe_allow_html=True)
    
    # Status
    st.markdown("<br>", unsafe_allow_html=True)
    status = projeto.get('status', 'Em Andamento')
    cor_status = {
        'Em Andamento': '#ffd93d',
        'Concluído': '#64ffda',
        'Concluído com Atraso': '#a855f7',
        'Atrasado': '#ff6b6b'
    }
    
    st.markdown(f"""
        <div style="margin-top: 10px; padding: 10px; background: {cor_status.get(status, '#8892b0')}22; 
                    border-radius: 10px; border-left: 4px solid {cor_status.get(status, '#8892b0')};">
            <strong style="color: {cor_status.get(status, '#8892b0')};">Status: {status}</strong>
        </div>
    """, unsafe_allow_html=True)
