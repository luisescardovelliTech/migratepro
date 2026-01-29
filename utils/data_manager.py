"""
Gerenciador de dados para projetos e usuários.
Integração com Supabase para persistência na nuvem.
"""

import hashlib
from datetime import datetime, date
from typing import Optional
import streamlit as st

# Tenta importar supabase, senão usa fallback JSON
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


def get_supabase_client() -> Optional['Client']:
    """Retorna cliente Supabase ou None se não disponível."""
    if not SUPABASE_AVAILABLE:
        return None
    
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception:
        return None


def usar_supabase() -> bool:
    """Verifica se deve usar Supabase."""
    return get_supabase_client() is not None


# ============== PROJETOS ==============

def carregar_projetos() -> list:
    """Carrega todos os projetos."""
    client = get_supabase_client()
    if client:
        try:
            response = client.table('projetos').select('*').order('created_at', desc=True).execute()
            return response.data or []
        except Exception as e:
            st.error(f"Erro ao carregar projetos: {e}")
            return []
    return []


def salvar_projeto(projeto: dict) -> None:
    """Salva ou atualiza um projeto."""
    client = get_supabase_client()
    if client:
        try:
            # Remove campos que não devem ser atualizados
            dados = {k: v for k, v in projeto.items() if k != 'created_at'}
            dados['updated_at'] = datetime.now().isoformat()
            
            client.table('projetos').upsert(dados).execute()
        except Exception as e:
            st.error(f"Erro ao salvar projeto: {e}")


def gerar_id_projeto() -> str:
    """Gera um ID único para o projeto no formato MIG-YYYY-XXX."""
    projetos = carregar_projetos()
    ano = datetime.now().year
    
    # Encontra o maior número do ano atual
    max_num = 0
    prefixo = f"MIG-{ano}-"
    for p in projetos:
        if p['id'].startswith(prefixo):
            try:
                num = int(p['id'].split('-')[-1])
                max_num = max(max_num, num)
            except ValueError:
                pass
    
    return f"{prefixo}{str(max_num + 1).zfill(3)}"


def criar_projeto(dados: dict) -> dict:
    """Cria um novo projeto."""
    novo_projeto = {
        'id': gerar_id_projeto(),
        'nome': dados['nome'],
        'data_inicio': dados.get('data_inicio'),
        'data_fim': dados.get('data_fim'),
        'data_prazo': dados.get('data_prazo'),
        'dias_estimados': dados.get('dias_estimados', 30),
        'metodo_migracao': dados.get('metodo_migracao', 'Manual'),
        'backup_recebido': dados.get('backup_recebido', False),
        'dificuldades': dados.get('dificuldades', ''),
        'observacoes': dados.get('observacoes', ''),
        'status': calcular_status(dados),
        'responsaveis': dados.get('responsaveis', [])
    }
    
    client = get_supabase_client()
    if client:
        try:
            client.table('projetos').insert(novo_projeto).execute()
        except Exception as e:
            st.error(f"Erro ao criar projeto: {e}")
    
    return novo_projeto


def atualizar_projeto(id_projeto: str, dados: dict) -> Optional[dict]:
    """Atualiza um projeto existente."""
    client = get_supabase_client()
    if client:
        try:
            # Busca projeto atual
            response = client.table('projetos').select('*').eq('id', id_projeto).execute()
            if response.data:
                projeto = response.data[0]
                projeto.update(dados)
                projeto['status'] = calcular_status(projeto)
                projeto['updated_at'] = datetime.now().isoformat()
                
                client.table('projetos').update(projeto).eq('id', id_projeto).execute()
                return projeto
        except Exception as e:
            st.error(f"Erro ao atualizar projeto: {e}")
    
    return None


def excluir_projeto(id_projeto: str) -> bool:
    """Exclui um projeto."""
    client = get_supabase_client()
    if client:
        try:
            client.table('projetos').delete().eq('id', id_projeto).execute()
            return True
        except Exception as e:
            st.error(f"Erro ao excluir projeto: {e}")
    return False


def buscar_projeto(id_projeto: str) -> Optional[dict]:
    """Busca um projeto pelo ID."""
    client = get_supabase_client()
    if client:
        try:
            response = client.table('projetos').select('*').eq('id', id_projeto).execute()
            if response.data:
                return response.data[0]
        except Exception as e:
            st.error(f"Erro ao buscar projeto: {e}")
    return None


def calcular_status(projeto: dict) -> str:
    """Calcula o status do projeto baseado nas datas."""
    hoje = date.today()
    
    # Se tem data_fim, está concluído
    if projeto.get('data_fim'):
        data_fim = projeto['data_fim']
        if isinstance(data_fim, str):
            try:
                data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
            except:
                return 'Concluído'
        
        data_prazo = projeto.get('data_prazo')
        if data_prazo:
            if isinstance(data_prazo, str):
                try:
                    data_prazo = datetime.strptime(data_prazo, '%Y-%m-%d').date()
                except:
                    return 'Concluído'
            
            if data_fim > data_prazo:
                return 'Concluído com Atraso'
        
        return 'Concluído'
    
    # Se não tem data_inicio, ainda não iniciou
    data_inicio = projeto.get('data_inicio')
    if not data_inicio:
        return 'Não Iniciado'
    
    # Se data_inicio é futura, ainda não iniciou
    if data_inicio:
        if isinstance(data_inicio, str):
            try:
                data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                if data_inicio > hoje:
                    return 'Não Iniciado'
            except:
                pass
    
    # Se não tem data_fim, verificar prazo
    data_prazo = projeto.get('data_prazo')
    if data_prazo:
        if isinstance(data_prazo, str):
            try:
                data_prazo = datetime.strptime(data_prazo, '%Y-%m-%d').date()
            except:
                return 'Em Andamento'
        
        if hoje > data_prazo:
            return 'Atrasado'
    
    return 'Em Andamento'


def calcular_dificuldade(dias_estimados: int) -> dict:
    """
    Calcula o nível de dificuldade baseado nos dias estimados.
    Retorna dict com nome e cor.
    """
    if dias_estimados <= 15:
        return {'nivel': 'Tranquila', 'cor': '#64ffda'}
    elif dias_estimados <= 24:
        return {'nivel': 'Moderada', 'cor': '#ffd93d'}
    else:
        return {'nivel': 'Difícil', 'cor': '#ff6b6b'}


def calcular_carga_time() -> dict:
    """
    Calcula a carga de trabalho do time.
    - Time: 4 pessoas
    - 2 pessoas por projeto
    - Capacidade: 2 projetos simultâneos
    - Projetos difíceis (25+ dias) contam como 1.5 projetos
    
    Retorna dict com status, cor e descrição.
    """
    projetos = carregar_projetos()
    
    # Filtra projetos ativos (Não Iniciados + Em Andamento)
    projetos_ativos = [
        p for p in projetos 
        if p.get('status') in ['Não Iniciado', 'Em Andamento']
    ]
    
    # Calcula peso baseado na dificuldade
    # Projetos difíceis contam como 1.5
    peso_total = 0
    projetos_dificeis = 0
    projetos_moderados = 0
    projetos_tranquilos = 0
    
    for p in projetos_ativos:
        dias = p.get('dias_estimados', 30)
        if dias >= 25:  # Difícil
            peso_total += 1.5
            projetos_dificeis += 1
        elif dias >= 16:  # Moderado
            peso_total += 1.2
            projetos_moderados += 1
        else:  # Tranquilo
            peso_total += 1
            projetos_tranquilos += 1
    
    qtd_projetos = len(projetos_ativos)
    
    # Define carga baseado no peso total
    # 2 projetos difíceis = 3 de peso = Corrido
    if peso_total <= 2:
        return {
            'status': 'Tranquilo',
            'cor': '#64ffda',
            'projetos_ativos': qtd_projetos,
            'projetos_dificeis': projetos_dificeis,
            'projetos_moderados': projetos_moderados,
            'projetos_tranquilos': projetos_tranquilos,
            'peso_total': round(peso_total, 1),
            'descricao': 'Time com folga para novos projetos'
        }
    elif peso_total <= 3:
        return {
            'status': 'Corrido',
            'cor': '#ffd93d',
            'projetos_ativos': qtd_projetos,
            'projetos_dificeis': projetos_dificeis,
            'projetos_moderados': projetos_moderados,
            'projetos_tranquilos': projetos_tranquilos,
            'peso_total': round(peso_total, 1),
            'descricao': 'Time trabalhando no limite'
        }
    else:
        return {
            'status': 'Muito Corrido',
            'cor': '#ff6b6b',
            'projetos_ativos': qtd_projetos,
            'projetos_dificeis': projetos_dificeis,
            'projetos_moderados': projetos_moderados,
            'projetos_tranquilos': projetos_tranquilos,
            'peso_total': round(peso_total, 1),
            'descricao': 'Atenção! Time sobrecarregado'
        }



# ============== USUÁRIOS ==============

def _hash_senha(senha: str) -> str:
    """Gera hash SHA256 da senha."""
    return hashlib.sha256(senha.encode()).hexdigest()


def carregar_usuarios() -> list:
    """Carrega todos os usuários."""
    client = get_supabase_client()
    if client:
        try:
            response = client.table('usuarios').select('*').execute()
            return response.data or []
        except Exception as e:
            st.error(f"Erro ao carregar usuários: {e}")
            return []
    return []


def autenticar_usuario(usuario: str, senha: str) -> Optional[dict]:
    """Autentica um usuário e retorna seus dados se válido."""
    client = get_supabase_client()
    
    if not client:
        return None
    
    try:
        senha_hash = _hash_senha(senha)
        response = client.table('usuarios').select('*').eq('usuario', usuario).eq('senha', senha_hash).eq('ativo', True).execute()
        
        if response.data:
            u = response.data[0]
            return {
                'id': u['id'],
                'usuario': u['usuario'],
                'nome': u['nome'],
                'nivel': u['nivel']
            }
    except Exception:
        pass
    
    return None


def criar_usuario(dados: dict) -> Optional[dict]:
    """Cria um novo usuário."""
    client = get_supabase_client()
    if client:
        try:
            # Verifica se usuário já existe
            response = client.table('usuarios').select('id').eq('usuario', dados['usuario']).execute()
            if response.data:
                return None  # Usuário já existe
            
            novo_usuario = {
                'usuario': dados['usuario'],
                'senha': _hash_senha(dados['senha']),
                'nome': dados['nome'],
                'nivel': dados.get('nivel', 1),
                'ativo': True
            }
            
            response = client.table('usuarios').insert(novo_usuario).execute()
            if response.data:
                return response.data[0]
        except Exception as e:
            st.error(f"Erro ao criar usuário: {e}")
    
    return None


def atualizar_usuario(id_usuario: int, dados: dict) -> Optional[dict]:
    """Atualiza um usuário existente."""
    client = get_supabase_client()
    if client:
        try:
            # Busca usuário atual
            response = client.table('usuarios').select('*').eq('id', id_usuario).execute()
            if response.data:
                usuario = response.data[0]
                
                # Não permite alterar o nome de usuário 'luis.silva'
                if usuario['usuario'] == 'luis.silva' and dados.get('usuario') != 'luis.silva':
                    return None
                
                usuario['nome'] = dados.get('nome', usuario['nome'])
                usuario['nivel'] = dados.get('nivel', usuario['nivel'])
                usuario['ativo'] = dados.get('ativo', usuario['ativo'])
                
                # Se senha foi fornecida, atualiza
                if dados.get('senha'):
                    usuario['senha'] = _hash_senha(dados['senha'])
                
                client.table('usuarios').update(usuario).eq('id', id_usuario).execute()
                return usuario
        except Exception as e:
            st.error(f"Erro ao atualizar usuário: {e}")
    
    return None


def excluir_usuario(id_usuario: int) -> bool:
    """Exclui um usuário (não permite excluir admin luis.silva)."""
    client = get_supabase_client()
    if client:
        try:
            # Verifica se é o admin principal
            response = client.table('usuarios').select('usuario').eq('id', id_usuario).execute()
            if response.data and response.data[0]['usuario'] == 'luis.silva':
                return False  # Não pode excluir admin principal
            
            client.table('usuarios').delete().eq('id', id_usuario).execute()
            return True
        except Exception as e:
            st.error(f"Erro ao excluir usuário: {e}")
    return False


def buscar_usuario(id_usuario: int) -> Optional[dict]:
    """Busca um usuário pelo ID."""
    client = get_supabase_client()
    if client:
        try:
            response = client.table('usuarios').select('*').eq('id', id_usuario).execute()
            if response.data:
                return response.data[0]
        except Exception as e:
            st.error(f"Erro ao buscar usuário: {e}")
    return None


# ============== ESTATÍSTICAS ==============

def obter_estatisticas() -> dict:
    """Retorna estatísticas gerais dos projetos."""
    projetos = carregar_projetos()
    
    total = len(projetos)
    concluidos = len([p for p in projetos if 'Concluído' in p.get('status', '')])
    atrasados = len([p for p in projetos if p.get('status') == 'Atrasado'])
    em_andamento = len([p for p in projetos if p.get('status') == 'Em Andamento'])
    nao_iniciados = len([p for p in projetos if p.get('status') == 'Não Iniciado'])
    
    # Média de dias para concluir e Eficiência
    dias_totais = []
    eficiencias = []
    
    for p in projetos:
        if p.get('data_fim') and p.get('data_inicio'):
            try:
                inicio = datetime.strptime(p['data_inicio'], '%Y-%m-%d').date()
                fim = datetime.strptime(p['data_fim'], '%Y-%m-%d').date()
                dias_reais = (fim - inicio).days
                if dias_reais < 1: dias_reais = 1
                
                dias_totais.append(dias_reais)
                
                # Cálculo de eficiência
                # Se dias_reais <= dias_estimados, eficiência >= 100%
                # Se dias_reais > dias_estimados, eficiência < 100%
                dias_estimados = p.get('dias_estimados', 30)
                eficiencia = (dias_estimados / dias_reais) * 100
                eficiencias.append(eficiencia)
                
            except (ValueError, TypeError):
                pass
    
    media_dias = sum(dias_totais) / len(dias_totais) if dias_totais else 0
    media_eficiencia = sum(eficiencias) / len(eficiencias) if eficiencias else 100.0
    
    # Métodos de migração
    metodos = {}
    for p in projetos:
        metodo = p.get('metodo_migracao', 'Não definido')
        metodos[metodo] = metodos.get(metodo, 0) + 1
    
    # Dificuldades mais comuns
    dificuldades = {}
    for p in projetos:
        dif = p.get('dificuldades', '') or ''
        dif = dif.strip()
        if dif:
            # Conta cada dificuldade como uma entrada
            dificuldades[dif[:50]] = dificuldades.get(dif[:50], 0) + 1
    
    return {
        'total': total,
        'concluidos': concluidos,
        'atrasados': atrasados,
        'em_andamento': em_andamento,
        'nao_iniciados': nao_iniciados,
        'media_dias': round(media_dias, 1),
        'eficiencia_media': round(media_eficiencia, 1),
        'percentual_concluido': round((concluidos / total * 100) if total > 0 else 0, 1),
        'metodos': metodos,
        'dificuldades': dict(sorted(dificuldades.items(), key=lambda x: x[1], reverse=True)[:5])
    }

