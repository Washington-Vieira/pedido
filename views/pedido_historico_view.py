import streamlit as st
from controllers.pedido_controller import PedidoController
from datetime import datetime
import pandas as pd
import os
import tempfile
import time
from fpdf import FPDF
from utils.print_manager import PrintManager
import shutil

class PedidoHistoricoView:
    def __init__(self, controller: PedidoController):
        self.controller = controller
        self._aplicar_estilos()

    def _aplicar_estilos(self):
        """Aplica estilos CSS personalizados"""
        st.markdown("""
        <style>
            /* Status tags */
            .status-pendente {
                background-color: #ffd700;
                color: black;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            
            .status-concluido {
                background-color: #90EE90;
                color: black;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            
            .status-processando {
                background-color: #87CEEB;
                color: black;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 14px;
            }

            /* Dashboard cards */
            .dashboard-container {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-bottom: 20px;
            }
            
            .metric-card {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                min-width: 180px;
                flex: 1;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
                position: relative;
                overflow: hidden;
            }
            
            .metric-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(255,255,255,0.1);
                transform: translateY(100%);
                transition: transform 0.2s ease-out;
            }
            
            .metric-card:hover::before {
                transform: translateY(0);
            }
            
            .metric-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            
            .metric-card.active {
                border: 2px solid #1e88e5;
                box-shadow: 0 0 0 2px rgba(30,136,229,0.3);
            }
            
            .metric-card.total {
                background-color: #2c3e50;
                color: white;
            }
            
            .metric-card.concluido {
                background-color: #90EE90;
            }
            
            .metric-card.processando {
                background-color: #87CEEB;
            }
            
            .metric-card.pendente {
                background-color: #ffd700;
            }
            
            .metric-card.urgente {
                background-color: #ff7f7f;
                color: white;
            }
            
            .metric-value {
                font-size: 24px;
                font-weight: bold;
                margin: 5px 0;
            }
            
            .metric-label {
                font-size: 14px;
                opacity: 0.9;
            }

            /* Cliente dashboard */
            .cliente-dashboard {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .cliente-dashboard:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            
            .cliente-titulo {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #2c3e50;
            }
            
            .cliente-metricas {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            
            .cliente-metrica {
                flex: 1;
                min-width: 150px;
                padding: 10px;
                border-radius: 4px;
                text-align: center;
                cursor: pointer;
                transition: all 0.2s ease;
                position: relative;
                overflow: hidden;
            }
            
            .cliente-metrica::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(255,255,255,0.1);
                transform: translateY(100%);
                transition: transform 0.2s ease-out;
            }
            
            .cliente-metrica:hover::before {
                transform: translateY(0);
            }
            
            .cliente-metrica:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            
            .cliente-metrica.active {
                border: 2px solid #1e88e5;
                box-shadow: 0 0 0 2px rgba(30,136,229,0.3);
            }

            /* Filtros ativos */
            .filtros-ativos {
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
                margin: 10px 0;
            }
            
            .filtro-tag {
                background-color: #e3f2fd;
                color: #1e88e5;
                padding: 4px 12px;
                border-radius: 16px;
                font-size: 12px;
                display: flex;
                align-items: center;
                gap: 4px;
            }
            
            .filtro-tag .remove {
                cursor: pointer;
                opacity: 0.7;
                transition: opacity 0.2s;
            }
            
            .filtro-tag .remove:hover {
                opacity: 1;
            }

            /* Tabela responsiva com hover states melhorados */
            .tabela-pedidos {
                width: 100%;
                max-width: 100%;
                overflow-x: auto;
                display: block;
                white-space: nowrap;
                border-collapse: collapse;
                margin: 0.5rem 0;
                background: white;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }

            .tabela-pedidos table {
                width: 100%;
                border-collapse: collapse;
            }

            .tabela-pedidos th {
                background-color: #f8f9fa;
                padding: 12px 15px;
                text-align: left;
                font-weight: 600;
                color: #2c3e50;
                border-bottom: 2px solid #e9ecef;
                position: sticky;
                top: 0;
                z-index: 1;
            }

            .tabela-pedidos td {
                padding: 10px 15px;
                border-bottom: 1px solid #e9ecef;
                color: #2c3e50;
            }

            .tabela-pedidos tr:hover {
                background-color: #f8f9fa;
            }

            .tabela-pedidos tr:last-child td {
                border-bottom: none;
            }

            /* Ajustes responsivos */
            @media screen and (max-width: 768px) {
                .metric-card {
                    min-width: 140px;
                }
                
                .cliente-metrica {
                    min-width: 120px;
                }
                
                .tabela-pedidos td, 
                .tabela-pedidos th {
                    padding: 8px 10px;
                    font-size: 13px;
                }
            }
        </style>
        
        <script>
            function filterDashboard(status, cliente) {
                // Create a custom event with the filter parameters
                const event = new CustomEvent('dashboardFilter', {
                    detail: { status: status, cliente: cliente }
                });
                window.dispatchEvent(event);
                
                // Update Streamlit
                window.parent.postMessage({
                    type: "streamlit:setComponentValue",
                    value: JSON.stringify({ status: status, cliente: cliente })
                }, "*");
            }
        </script>
        """, unsafe_allow_html=True)

    def _mostrar_dashboard(self, df_pedidos: pd.DataFrame):
        """Mostra o dashboard gerencial com métricas"""
        if df_pedidos.empty:
            return

        # Inicializar estado do filtro se não existir
        if 'dashboard_filter' not in st.session_state:
            st.session_state.dashboard_filter = {'status': None, 'cliente': None}

        # Calcular métricas gerais
        total_pedidos = len(df_pedidos)
        total_concluido = len(df_pedidos[df_pedidos['Status'] == 'Concluído'])
        total_processando = len(df_pedidos[df_pedidos['Status'] == 'Em Processamento'])
        total_pendente = len(df_pedidos[df_pedidos['Status'] == 'Pendente'])
        total_urgente_pendente = len(df_pedidos[
            (df_pedidos['Status'] == 'Pendente') & 
            (df_pedidos['Urgente'].str.strip().str.lower() == 'sim')
        ])

        # Mostrar cards com métricas gerais
        st.markdown(f"""
        <div class="dashboard-container">
            <div class="metric-card total" data-status="todos">
                <div class="metric-label">TOTAL PEDIDOS</div>
                <div class="metric-value">{total_pedidos}</div>
            </div>
            <div class="metric-card concluido" data-status="Concluído">
                <div class="metric-label">CONCLUÍDO</div>
                <div class="metric-value">{total_concluido}</div>
            </div>
            <div class="metric-card processando" data-status="Em Processamento">
                <div class="metric-label">PROCESSO</div>
                <div class="metric-value">{total_processando}</div>
            </div>
            <div class="metric-card pendente" data-status="Pendente">
                <div class="metric-label">PENDENTE</div>
                <div class="metric-value">{total_pendente}</div>
            </div>
            <div class="metric-card urgente" data-status="urgente">
                <div class="metric-label">URGENTE</div>
                <div class="metric-value">{total_urgente_pendente}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Métricas por cliente
        clientes = df_pedidos['Cliente'].unique()
        for cliente in sorted(clientes):
            df_cliente = df_pedidos[df_pedidos['Cliente'] == cliente]
            
            # Calcular métricas do cliente
            total_concluido = len(df_cliente[df_cliente['Status'] == 'Concluído'])
            total_processando = len(df_cliente[df_cliente['Status'] == 'Em Processamento'])
            total_pendente = len(df_cliente[df_cliente['Status'] == 'Pendente'])
            total_urgente = len(df_cliente[
                (df_cliente['Status'] == 'Pendente') & 
                (df_cliente['Urgente'].str.strip().str.lower() == 'sim')
            ])
            
            # Mostrar métricas do cliente
            st.markdown(f"""
            <div class="cliente-dashboard">
                <div class="cliente-titulo">{cliente}</div>
                <div class="cliente-metricas">
                    <div class="cliente-metrica" style="background-color: #90EE90" 
                         data-status="Concluído" data-cliente="{cliente}">
                        <div class="metric-label">Concluído</div>
                        <div class="metric-value">{total_concluido}</div>
                    </div>
                    <div class="cliente-metrica" style="background-color: #87CEEB"
                         data-status="Em Processamento" data-cliente="{cliente}">
                        <div class="metric-label">Em Processo</div>
                        <div class="metric-value">{total_processando}</div>
                    </div>
                    <div class="cliente-metrica" style="background-color: #ffd700"
                         data-status="Pendente" data-cliente="{cliente}">
                        <div class="metric-label">Pendente</div>
                        <div class="metric-value">{total_pendente}</div>
                    </div>
                    <div class="cliente-metrica" style="background-color: #ff7f7f; color: white"
                         data-status="urgente" data-cliente="{cliente}">
                        <div class="metric-label">Urgente</div>
                        <div class="metric-value">{total_urgente}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    def mostrar_interface(self):
        """Mostra a interface do histórico de pedidos"""
        try:
            # Buscar pedidos primeiro para o dashboard
            df_pedidos = self.controller.buscar_pedidos(status=None)  # Buscar todos os pedidos para o dashboard
            
            if not df_pedidos.empty:
                # Mostrar dashboard no topo
                self._mostrar_dashboard(df_pedidos)
            
            st.markdown("### 📋 Histórico de Pedidos")
            
            # Filtro de Status (agora controlado pelo dashboard também)
            status_filtro = st.selectbox(
                "Status do Pedido",
                ["Todos", "Pendente", "Em Processamento", "Concluído"],
                key="status_filter",
                index=["Todos", "Pendente", "Em Processamento", "Concluído"].index(
                    st.session_state.dashboard_filter.get('status', 'Todos') 
                    if 'dashboard_filter' in st.session_state 
                    and st.session_state.dashboard_filter.get('status') != 'urgente'
                    else "Todos"
                )
            )
            
            # Filtro por Data
            col_data1, col_data2 = st.columns(2)
            with col_data1:
                data_inicial = st.date_input("Data inicial", value=None, key="filtro_data_inicial")
            with col_data2:
                data_final = st.date_input("Data final", value=None, key="filtro_data_final")
            
            # Aplicar filtros do dashboard e manter o DataFrame filtrado
            df_filtrado = df_pedidos.copy()
            filtro_aplicado = False
            
            # Aplicar filtro de status
            if status_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado["Status"] == status_filtro]
                filtro_aplicado = True
            
            # Aplicar filtros do dashboard se existirem
            if 'dashboard_filter' in st.session_state:
                dashboard_status = st.session_state.dashboard_filter.get('status')
                dashboard_cliente = st.session_state.dashboard_filter.get('cliente')
                
                if dashboard_status == 'urgente':
                    df_filtrado = df_filtrado[
                        (df_filtrado['Status'] == 'Pendente') & 
                        (df_filtrado['Urgente'].str.strip().str.lower() == 'sim')
                    ]
                    filtro_aplicado = True
                    st.info("🚨 Mostrando apenas pedidos urgentes pendentes")
                elif dashboard_status and dashboard_status != 'todos':
                    df_filtrado = df_filtrado[df_filtrado['Status'] == dashboard_status]
                    filtro_aplicado = True
                    st.info(f"📊 Mostrando pedidos com status: {dashboard_status}")
                
                if dashboard_cliente:
                    df_filtrado = df_filtrado[df_filtrado['Cliente'] == dashboard_cliente]
                    filtro_aplicado = True
                    st.info(f"👥 Mostrando pedidos do cliente: {dashboard_cliente}")
            
            # Aplicar filtro de data se selecionado
            if not df_filtrado.empty and (data_inicial or data_final):
                df_filtrado["Data_dt"] = pd.to_datetime(df_filtrado["Data"], format="%d/%m/%Y %H:%M", errors="coerce")
                if data_inicial:
                    df_filtrado = df_filtrado[df_filtrado["Data_dt"] >= pd.to_datetime(data_inicial)]
                if data_final:
                    df_filtrado = df_filtrado[df_filtrado["Data_dt"] <= pd.to_datetime(data_final) + pd.Timedelta(days=1)]
                df_filtrado = df_filtrado.drop(columns=["Data_dt"])
                filtro_aplicado = True
            
            if df_filtrado.empty:
                st.warning("Nenhum pedido encontrado com os filtros selecionados.")
                return
            
            # Mostrar total de pedidos encontrados com os filtros
            if filtro_aplicado:
                st.success(f"🔍 {len(df_filtrado)} pedidos encontrados com os filtros aplicados")
            else:
                st.write(f"Total: {len(df_filtrado)} pedidos")
            
            # Formatar DataFrame para exibição
            df_display = df_filtrado[[
                "Numero_Pedido", "Data", "Cliente", "RACK", 
                "Localizacao", "Solicitante", "Urgente", "Status",
                "Ultima_Atualizacao", "Responsavel_Atualizacao"
            ]].copy()
            
            # Renomear colunas
            df_display.columns = [
                "Número", "Data", "Cliente", "RACK",
                "Localização", "Solicitante", "Urgente", "Status",
                "Última Atualização", "Responsável"
            ]
            
            # Formatar status com cores
            def formatar_status(status):
                cores = {
                    "Pendente": "status-pendente",
                    "Concluído": "status-concluido",
                    "Em Processamento": "status-processando"
                }
                classe = cores.get(status, "")
                return f'<span class="{classe}">{status}</span>'
            
            df_display["Status"] = df_display["Status"].apply(formatar_status)
            
            # Formatar urgente com cores
            def formatar_urgente(urgente):
                if urgente.strip().lower() == "sim":
                    return '<span style="color:white;background-color:#d9534f;font-weight:bold;padding:2px 8px;border-radius:4px;">URGENTE</span>'
                else:
                    return '<span style="color:#222;background-color:#eee;padding:2px 8px;border-radius:4px;">Não</span>'
            
            df_display["Urgente"] = df_display["Urgente"].apply(formatar_urgente)
            
            # Mostrar tabela dentro de um expander
            with st.expander("Ver pedidos", expanded=True):
                st.markdown(
                    f'<div class="tabela-pedidos">{df_display.to_html(escape=False, index=False)}</div>',
                    unsafe_allow_html=True
                )
            
            # Detalhes do Pedido
            st.markdown("### Detalhes do Pedido")
            
            # Seleção do pedido (agora usando o DataFrame filtrado)
            pedidos_filtrados = df_filtrado["Numero_Pedido"].tolist()
            
            # Adicionar mensagem informativa se houver filtros ativos
            if filtro_aplicado:
                st.info("📌 Mostrando apenas os pedidos dos filtros selecionados")
            
            pedido_selecionado = st.selectbox(
                "Selecione um pedido",
                [""] + pedidos_filtrados,
                key="pedido_selecionado"
            )
            
            if pedido_selecionado:
                # Buscar detalhes do pedido
                detalhes = self.controller.get_pedido_detalhes(pedido_selecionado)
                
                # Informações e Itens do Pedido lado a lado
                col_info, col_itens = st.columns(2)
                with col_info:
                    st.markdown("#### Informações")
                    st.write(f"**Número:** {detalhes['info']['Numero_Pedido']}")
                    st.write(f"**Data:** {detalhes['info']['Data']}")
                    st.write(f"**Cliente:** {detalhes['info']['Cliente']}")
                    st.write(f"**RACK:** {detalhes['info']['RACK']}")
                    st.write(f"**Localização:** {detalhes['info']['Localizacao']}")
                    st.write(f"**Solicitante:** {detalhes['info']['Solicitante']}")
                    
                    # Formatar status com cor
                    status_html = formatar_status(detalhes['status'])
                    st.markdown(f"**Status:** {status_html}", unsafe_allow_html=True)
                    
                    # Mostrar se é urgente
                    if detalhes['info'].get('Urgente', '').strip().lower() == 'sim':
                        st.markdown("**Prioridade:** 🚨 URGENTE", unsafe_allow_html=True)
                
                with col_itens:
                    st.markdown("#### Itens do Pedido")
                    if detalhes['itens']:
                        for idx, item in enumerate(detalhes['itens'], 1):
                            st.write(f"**Item {idx}**")
                            st.write(f"**CÓD Yazaki:** {item['cod_yazaki']}")
                            st.write(f"**Código Cabo:** {item['codigo_cabo']}")
                            st.write(f"**Seção:** {item['seccao']}")
                            st.write(f"**Cor:** {item['cor']}")
                            st.write(f"**Quantidade:** {item['quantidade']}")
                            if idx < len(detalhes['itens']):
                                st.markdown("---")
                    else:
                        st.info("Nenhum item encontrado para este pedido.")

                # Botão de impressão
                if st.button("🖨️ Imprimir", help="Imprimir pedido"):
                    try:
                        link_html = self.controller.imprimir_pedido(pedido_selecionado, view=self)
                        if link_html:
                            st.success("Pedido pronto para impressão! Clique no link abaixo para abrir o comprovante.")
                            st.markdown(link_html, unsafe_allow_html=True)
                        else:
                            st.error("Erro ao gerar o comprovante do pedido.")
                    except Exception as e:
                        st.error(f"Erro ao imprimir pedido: {str(e)}")

                # Campos em coluna única, um abaixo do outro
                nome_usuario = st.text_input(
                    "Responsável",
                    value=st.session_state.get('nome_usuario', ''),
                    placeholder="Digite seu nome"
                )

                novo_status = st.selectbox(
                    "Novo Status",
                    ["Pendente", "Em Processamento", "Concluído"],
                    index=["Pendente", "Em Processamento", "Concluído"].index(detalhes['status']) if detalhes['status'] in ["Pendente", "Em Processamento", "Concluído"] else 0
                )

                if st.button("Atualizar Status", use_container_width=True):
                    if not nome_usuario:
                        st.error("Por favor, informe o nome do responsável!")
                    else:
                        try:
                            st.session_state['nome_usuario'] = nome_usuario
                            self.controller.atualizar_status_pedido(
                                pedido_selecionado,
                                novo_status,
                                nome_usuario
                            )
                            st.success("Status atualizado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            pass  # Não exibe nenhuma mensagem de erro para o usuário

                # Observações
                if detalhes['info'].get('Observacoes'):
                    st.markdown("---")
                    st.markdown("#### Observações")
                    st.write(detalhes['info']['Observacoes'])

            # Mostrar filtros ativos
            filtros_ativos = []
            
            if status_filtro != "Todos":
                filtros_ativos.append(("Status", status_filtro))
            
            if 'dashboard_filter' in st.session_state:
                dashboard_status = st.session_state.dashboard_filter.get('status')
                dashboard_cliente = st.session_state.dashboard_filter.get('cliente')
                
                if dashboard_status == 'urgente':
                    filtros_ativos.append(("Urgência", "Pedidos Urgentes"))
                elif dashboard_status and dashboard_status != 'todos':
                    filtros_ativos.append(("Status", dashboard_status))
                
                if dashboard_cliente:
                    filtros_ativos.append(("Cliente", dashboard_cliente))
            
            if data_inicial:
                filtros_ativos.append(("Data Inicial", data_inicial.strftime("%d/%m/%Y")))
            if data_final:
                filtros_ativos.append(("Data Final", data_final.strftime("%d/%m/%Y")))
            
            if filtros_ativos:
                st.markdown('<div class="filtros-ativos">', unsafe_allow_html=True)
                for tipo, valor in filtros_ativos:
                    st.markdown(
                        f'<div class="filtro-tag">{tipo}: {valor}'
                        f'<span class="remove" onclick="removerFiltro(\'{tipo}\', \'{valor}\')">✕</span></div>',
                        unsafe_allow_html=True
                    )
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Adicionar JavaScript para remover filtros
                st.markdown("""
                <script>
                function removerFiltro(tipo, valor) {
                    // Atualizar estado do Streamlit
                    let currentState = JSON.parse(localStorage.getItem('streamlit_state') || '{}');
                    
                    if (tipo === 'Status') {
                        // Resetar filtro de status
                        currentState.status_filter = 'Todos';
                        if (currentState.dashboard_filter) {
                            currentState.dashboard_filter.status = null;
                        }
                    } else if (tipo === 'Cliente') {
                        if (currentState.dashboard_filter) {
                            currentState.dashboard_filter.cliente = null;
                        }
                    } else if (tipo === 'Data Inicial') {
                        currentState.filtro_data_inicial = null;
                    } else if (tipo === 'Data Final') {
                        currentState.filtro_data_final = null;
                    }
                    
                    // Remover classe active dos cards
                    document.querySelectorAll('.metric-card, .cliente-metrica').forEach(card => {
                        card.classList.remove('active');
                    });
                    
                    // Atualizar estado do Streamlit
                    window.parent.postMessage({
                        type: "streamlit:setComponentValue",
                        value: JSON.stringify(currentState)
                    }, "*");
                    
                    // Recarregar a página para aplicar as mudanças
                    window.parent.location.reload();
                }
                
                // Adicionar classe active aos cards baseado nos filtros ativos
                document.addEventListener('DOMContentLoaded', function() {
                    const dashboardFilter = JSON.parse(localStorage.getItem('streamlit_state') || '{}').dashboard_filter || {};
                    const status = dashboardFilter.status;
                    const cliente = dashboardFilter.cliente;
                    
                    document.querySelectorAll('.metric-card, .cliente-metrica').forEach(card => {
                        const cardStatus = card.getAttribute('data-status');
                        const cardCliente = card.getAttribute('data-cliente');
                        
                        if (
                            (status && cardStatus === status) ||
                            (cliente && cardCliente === cliente)
                        ) {
                            card.classList.add('active');
                        }
                    });
                });
                </script>
                """, unsafe_allow_html=True)

            # Adicionar JavaScript para interação do dashboard
            st.markdown("""
            <script>
            // Função para atualizar os filtros quando o dashboard é clicado
            function updateDashboardFilter(status, cliente) {
                // Atualizar estado do Streamlit
                let currentState = JSON.parse(localStorage.getItem('streamlit_state') || '{}');
                
                if (!currentState.dashboard_filter) {
                    currentState.dashboard_filter = {};
                }
                
                // Se clicar no mesmo filtro, remove ele
                if (
                    currentState.dashboard_filter.status === status &&
                    currentState.dashboard_filter.cliente === cliente
                ) {
                    currentState.dashboard_filter.status = null;
                    currentState.dashboard_filter.cliente = null;
                    currentState.status_filter = 'Todos';
                } else {
                    currentState.dashboard_filter.status = status;
                    currentState.dashboard_filter.cliente = cliente;
                    
                    // Atualizar selectbox de status
                    if (status === 'urgente') {
                        currentState.status_filter = 'Pendente';
                    } else if (status && status !== 'todos') {
                        currentState.status_filter = status;
                    } else {
                        currentState.status_filter = 'Todos';
                    }
                }
                
                // Atualizar estado do Streamlit
                window.parent.postMessage({
                    type: "streamlit:setComponentValue",
                    value: JSON.stringify(currentState)
                }, "*");
                
                // Recarregar a página para aplicar as mudanças
                window.parent.location.reload();
            }
            
            // Adicionar listeners para os cards do dashboard
            document.addEventListener('DOMContentLoaded', function() {
                document.querySelectorAll('.metric-card, .cliente-metrica').forEach(card => {
                    card.addEventListener('click', function() {
                        const status = this.getAttribute('data-status');
                        const cliente = this.getAttribute('data-cliente');
                        updateDashboardFilter(status, cliente);
                    });
                });
            });
            </script>
            """, unsafe_allow_html=True)

            # Atualizar os cards do dashboard para incluir atributos de dados
            def formatar_card_dashboard(status, valor, cliente=None):
                status_class = status.lower().replace(" ", "-")
                data_attrs = f'data-status="{status}"'
                if cliente:
                    data_attrs += f' data-cliente="{cliente}"'
                
                return f'''
                <div class="metric-card {status_class}" {data_attrs}>
                    <div class="metric-label">{status.upper()}</div>
                    <div class="metric-value">{valor}</div>
                </div>
                '''
        except Exception as e:
            if "Quota exceeded" in str(e) or "[429]" in str(e):
                st.warning("Por favor, recarregue a página e aguarde um minuto antes de tentar novamente.")
            else:
                st.warning("Não foi possível carregar os pedidos. Por favor, tente novamente em alguns instantes.")

    def formatar_pedido_para_impressao(self, pedido: dict) -> str:
        """Formata os detalhes do pedido para impressão"""
        info = pedido['info']
        itens = pedido['itens']
        
        texto = f"""=================================================
            PEDIDO DE REQUISIÇÃO
=================================================
Número: {info['Numero_Pedido']}
Data: {info['Data']}
Status: {pedido['status']}

INFORMAÇÕES:
-------------------------------------------------
Cliente: {info['Cliente']}
RACK: {info['RACK']}
Localização: {info['Localizacao']}
Solicitante: {info['Solicitante']}

OBSERVAÇÕES:
{info['Observacoes']}

ITENS:
-------------------------------------------------"""

        for item in itens:
            texto += f"""
CÓD Yazaki: {item['cod_yazaki']}
Código Cabo: {item['codigo_cabo']}
Secção: {item['seccao']}
Cor: {item['cor']}
Quantidade: {item['quantidade']}
-------------------------------------------------"""
        
        texto += "\n\n"
        texto += "Assinatura: _____________________________\n"
        texto += f"Impresso em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        
        return texto 