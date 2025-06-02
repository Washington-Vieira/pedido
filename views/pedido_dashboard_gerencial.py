import streamlit as st
import pandas as pd

def mostrar_dashboard_gerencial(controller):
    """
    Exibe um dashboard gerencial com totais gerais e por cliente.
    controller: instância de PedidoController
    """
    # Buscar todos os pedidos
    df_pedidos = controller.buscar_pedidos(status=None)
    if df_pedidos.empty:
        st.info("Nenhum pedido encontrado para exibir o dashboard gerencial.")
        return

    # --- TOTAIS GERAIS ---
    total_pedidos = len(df_pedidos)
    total_concluido = len(df_pedidos[df_pedidos['Status'] == 'Concluído'])
    total_processando = len(df_pedidos[df_pedidos['Status'] == 'Em Processamento'])
    total_pendente = len(df_pedidos[df_pedidos['Status'] == 'Pendente'])
    total_urgente_pendente = len(df_pedidos[(df_pedidos['Status'] == 'Pendente') & (df_pedidos['Urgente'].str.strip().str.lower() == 'sim')])

    st.markdown("""
    <style>
    .dashboard-cards {display: flex; gap: 10px; margin-bottom: 20px;}
    .dashboard-card {
        background: #fff; border-radius: 8px; padding: 18px 20px; min-width: 160px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08); text-align: center; font-size: 15px;
        font-weight: 500; border: 1px solid #eee;
    }
    .card-total {background: #2c3e50; color: #fff;}
    .card-concluido {background: #90EE90;}
    .card-processando {background: #87CEEB;}
    .card-pendente {background: #ffd700;}
    .card-urgente {background: #ff7f7f; color: #fff;}
    </style>
    <div class="dashboard-cards">
        <div class="dashboard-card card-total">TOTAL PEDIDOS<br><span style='font-size:22px'>{total_pedidos}</span></div>
        <div class="dashboard-card card-concluido">CONCLUÍDO<br><span style='font-size:22px'>{total_concluido}</span></div>
        <div class="dashboard-card card-processando">PROCESSO<br><span style='font-size:22px'>{total_processando}</span></div>
        <div class="dashboard-card card-pendente">PENDENTE<br><span style='font-size:22px'>{total_pendente}</span></div>
        <div class="dashboard-card card-urgente">URGENTE<br><span style='font-size:22px'>{total_urgente_pendente}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # --- POR CLIENTE ---
    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
    clientes = sorted(df_pedidos['Cliente'].unique())
    for cliente in clientes:
        df_cliente = df_pedidos[df_pedidos['Cliente'] == cliente]
        total_concluido = len(df_cliente[df_cliente['Status'] == 'Concluído'])
        total_processando = len(df_cliente[df_cliente['Status'] == 'Em Processamento'])
        total_pendente = len(df_cliente[df_cliente['Status'] == 'Pendente'])
        total_urgente = len(df_cliente[(df_cliente['Status'] == 'Pendente') & (df_cliente['Urgente'].str.strip().str.lower() == 'sim')])
        st.markdown(f"""
        <div style='margin-bottom: 8px; font-weight: bold; font-size: 17px;'>{cliente}</div>
        <div class="dashboard-cards">
            <div class="dashboard-card card-concluido">Concluído<br><span style='font-size:20px'>{total_concluido}</span></div>
            <div class="dashboard-card card-processando">Em Processo<br><span style='font-size:20px'>{total_processando}</span></div>
            <div class="dashboard-card card-pendente">Pendente<br><span style='font-size:20px'>{total_pendente}</span></div>
            <div class="dashboard-card card-urgente">Urgente<br><span style='font-size:20px'>{total_urgente}</span></div>
        </div>
        """, unsafe_allow_html=True) 