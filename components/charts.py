"""
Componentes de gráficos usando Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date


def criar_grafico_progresso(projetos: list) -> go.Figure:
    """Cria gráfico de barras de progresso dos projetos."""
    
    if not projetos:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum projeto cadastrado",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#8892b0")
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        return fig
    
    # Prepara os dados
    nomes = []
    progressos = []
    cores = []
    status_list = []
    prazos = []
    
    hoje = date.today()
    
    for p in projetos[:10]:  # Limita a 10 projetos
        nomes.append(p['nome'][:30] + '...' if len(p['nome']) > 30 else p['nome'])
        
        # Calcula progresso baseado nas datas
        if p.get('data_fim'):
            progresso = 100
        elif p.get('data_inicio') and p.get('data_prazo'):
            try:
                inicio = datetime.strptime(p['data_inicio'], '%Y-%m-%d').date()
                prazo = datetime.strptime(p['data_prazo'], '%Y-%m-%d').date()
                total_dias = (prazo - inicio).days
                dias_passados = (hoje - inicio).days
                progresso = min(100, max(0, (dias_passados / total_dias * 100) if total_dias > 0 else 0))
            except (ValueError, TypeError):
                progresso = 50
        else:
            progresso = 50
        
        progressos.append(progresso)
        
        # Define cor baseada no status
        status = p.get('status', 'Em Andamento')
        status_list.append(status)
        
        if 'Concluído' in status:
            cores.append('#64ffda')  # Verde
        elif status == 'Atrasado':
            cores.append('#ff6b6b')  # Vermelho
        else:
            cores.append('#ffd93d')  # Amarelo
        
        # Prazo
        prazo_str = p.get('data_prazo', 'N/D')
        if prazo_str and prazo_str != 'N/D':
            try:
                prazo_date = datetime.strptime(prazo_str, '%Y-%m-%d')
                prazos.append(prazo_date.strftime('%d/%m/%Y'))
            except:
                prazos.append('N/D')
        else:
            prazos.append('N/D')
    
    fig = go.Figure()
    
    # Barras de progresso
    fig.add_trace(go.Bar(
        y=nomes,
        x=progressos,
        orientation='h',
        marker=dict(
            color=cores,
            line=dict(color='rgba(255,255,255,0.3)', width=1)
        ),
        text=[f"{p:.0f}%" for p in progressos],
        textposition='inside',
        textfont=dict(color='white', size=12),
        hovertemplate="<b>%{y}</b><br>Progresso: %{x:.1f}%<br><extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text="Progresso dos Projetos",
            font=dict(size=18, color='#fff')
        ),
        xaxis=dict(
            title="Progresso (%)",
            range=[0, 105],
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            color='#8892b0'
        ),
        yaxis=dict(
            autorange="reversed",
            color='#8892b0'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=max(300, len(nomes) * 50),
        margin=dict(l=10, r=10, t=50, b=10),
        showlegend=False
    )
    
    return fig


def criar_grafico_metodos(metodos: dict) -> go.Figure:
    """Cria gráfico de rosca dos métodos de migração."""
    
    if not metodos:
        metodos = {'Sem dados': 1}
    
    cores = ['#64ffda', '#ffd93d', '#ff6b6b', '#a855f7', '#38bdf8']
    
    fig = go.Figure(data=[go.Pie(
        labels=list(metodos.keys()),
        values=list(metodos.values()),
        hole=0.6,
        marker=dict(colors=cores[:len(metodos)]),
        textinfo='percent',
        textfont=dict(size=12, color='white'),
        hovertemplate="<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>"
    )])
    
    fig.add_annotation(
        text="TOTAL",
        x=0.5, y=0.55,
        font=dict(size=14, color='#8892b0'),
        showarrow=False
    )
    fig.add_annotation(
        text=str(sum(metodos.values())),
        x=0.5, y=0.45,
        font=dict(size=24, color='#fff', family='Arial Black'),
        showarrow=False
    )
    
    fig.update_layout(
        title=dict(
            text="Métodos de Migração",
            font=dict(size=16, color='#fff')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300,
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(
            orientation='v',
            yanchor='middle',
            y=0.5,
            xanchor='left',
            x=1.05,
            font=dict(color='#8892b0')
        ),
        showlegend=True
    )
    
    return fig


def criar_grafico_dificuldades(dificuldades: dict) -> go.Figure:
    """Cria gráfico de barras horizontais das dificuldades mais comuns."""
    
    if not dificuldades:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhuma dificuldade registrada",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#8892b0")
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=200
        )
        return fig
    
    # Pega top 5 dificuldades
    top_dificuldades = dict(list(dificuldades.items())[:5])
    
    total = sum(top_dificuldades.values())
    labels = list(top_dificuldades.keys())
    valores = list(top_dificuldades.values())
    percentuais = [(v / total * 100) if total > 0 else 0 for v in valores]
    
    # Cores gradientes
    cores = ['#ff6b6b', '#ffa06b', '#ffd93d', '#98d85b', '#64ffda']
    
    fig = go.Figure()
    
    for i, (label, valor, pct) in enumerate(zip(labels, valores, percentuais)):
        fig.add_trace(go.Bar(
            y=[label[:25] + '...' if len(label) > 25 else label],
            x=[pct],
            orientation='h',
            marker=dict(color=cores[i % len(cores)]),
            text=f"{pct:.0f}%",
            textposition='inside',
            textfont=dict(color='white', size=11),
            showlegend=False,
            hovertemplate=f"<b>{label}</b><br>Ocorrências: {valor}<br>Percentual: {pct:.1f}%<extra></extra>"
        ))
    
    fig.update_layout(
        title=dict(
            text="Dificuldades Mais Comuns",
            font=dict(size=16, color='#fff')
        ),
        xaxis=dict(
            title="Percentual (%)",
            range=[0, 100],
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            color='#8892b0'
        ),
        yaxis=dict(
            autorange="reversed",
            color='#8892b0'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=max(150, len(labels) * 40),
        margin=dict(l=10, r=10, t=50, b=10),
        barmode='stack'
    )
    
    return fig


def criar_grafico_timeline(projetos: list) -> go.Figure:
    """Cria um gráfico de timeline/Gantt dos projetos."""
    
    if not projetos:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum projeto cadastrado",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#8892b0")
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        return fig
    
    # Filtra projetos com datas válidas
    projetos_validos = []
    for p in projetos:
        if p.get('data_inicio') and p.get('data_prazo'):
            projetos_validos.append(p)
    
    if not projetos_validos:
        fig = go.Figure()
        fig.add_annotation(
            text="Projetos sem datas definidas",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#8892b0")
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        return fig
    
    fig = go.Figure()
    
    cores_status = {
        'Em Andamento': '#ffd93d',
        'Concluído': '#64ffda',
        'Concluído com Atraso': '#a855f7',
        'Atrasado': '#ff6b6b'
    }
    
    for i, p in enumerate(projetos_validos[:10]):
        try:
            inicio = datetime.strptime(p['data_inicio'], '%Y-%m-%d')
            prazo = datetime.strptime(p['data_prazo'], '%Y-%m-%d')
            fim = datetime.strptime(p['data_fim'], '%Y-%m-%d') if p.get('data_fim') else None
            
            status = p.get('status', 'Em Andamento')
            cor = cores_status.get(status, '#8892b0')
            
            # Barra do projeto
            fig.add_trace(go.Bar(
                x=[(prazo - inicio).days],
                y=[p['nome'][:25]],
                base=[inicio],
                orientation='h',
                marker=dict(color=cor, opacity=0.8),
                name=status,
                showlegend=False,
                hovertemplate=f"<b>{p['nome']}</b><br>Início: {inicio.strftime('%d/%m/%Y')}<br>Prazo: {prazo.strftime('%d/%m/%Y')}<br>Status: {status}<extra></extra>"
            ))
        except (ValueError, TypeError):
            continue
    
    fig.update_layout(
        title=dict(
            text="Timeline dos Projetos",
            font=dict(size=18, color='#fff')
        ),
        xaxis=dict(
            title="Data",
            type='date',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            color='#8892b0'
        ),
        yaxis=dict(
            autorange="reversed",
            color='#8892b0'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=max(300, len(projetos_validos) * 40),
        margin=dict(l=10, r=10, t=50, b=10),
        barmode='stack'
    )
    
    return fig
