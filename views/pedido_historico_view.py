import streamlit as stMore actions
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
            }
            
            .metric-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
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

            .cliente-dashboard {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .cliente-titulo {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
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
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .cliente-metrica:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }

            /* Tabela responsiva */
            .tabela-pedidos {
                width: 100%;
                max-width: 100%;
                overflow-x: auto;
                display: block;
                white-space: nowrap;
                border-collapse: collapse;
                margin: 0.5rem 0;
            }

            .tabela-pedidos table {
                width: 100%;
                border-collapse: collapse;
            }

            .tabela-pedidos th {
                background-color: #f0f2f6;
                padding: 8px 15px;
                text-align: left;
                font-weight: bold;
                border-bottom: 2px solid #ddd;
                font-size: 13px;
            }

            .tabela-pedidos td {
                padding: 6px 15px;
                border-bottom: 1px solid #ddd;
                font-size: 13px;
                line-height: 1.2;
            }

            .tabela-pedidos tr:hover {
                background-color: #f5f5f5;
            }

            /* Ajuste para telas menores */
            @media screen and (max-width: 768px) {
                .tabela-pedidos {
                    font-size: 12px;
                }
                .tabela-pedidos td, .tabela-pedidos th {
                    padding: 5px 8px;
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
            <div class="metric-card total" onclick="filterDashboard('todos', null)">
                <div class="metric-label">TOTAL PEDIDOS</div>
                <div class="metric-value">{total_pedidos}</div>
            </div>
            <div class="metric-card concluido" onclick="filterDashboard('Concluído', null)">
                <div class="metric-label">CONCLUÍDO</div>
                <div class="metric-value">{total_concluido}</div>
            </div>
            <div class="metric-card processando" onclick="filterDashboard('Em Processamento', null)">
                <div class="metric-label">PROCESSO</div>
                <div class="metric-value">{total_processando}</div>
            </div>
            <div class="metric-card pendente" onclick="filterDashboard('Pendente', null)">
                <div class="metric-label">PENDENTE</div>
                <div class="metric-value">{total_pendente}</div>
            </div>
            <div class="metric-card urgente" onclick="filterDashboard('urgente', null)">
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
                         onclick="filterDashboard('Concluído', '{cliente}')">
                        <div class="metric-label">Concluído</div>
                        <div class="metric-value">{total_concluido}</div>
                    </div>
                    <div class="cliente-metrica" style="background-color: #87CEEB"
                         onclick="filterDashboard('Em Processamento', '{cliente}')">
                        <div class="metric-label">Em Processo</div>
                        <div class="metric-value">{total_processando}</div>
                    </div>
                    <div class="cliente-metrica" style="background-color: #ffd700"
                         onclick="filterDashboard('Pendente', '{cliente}')">
                        <div class="metric-label">Pendente</div>
                        <div class="metric-value">{total_pendente}</div>
                    </div>
                    <div class="cliente-metrica" style="background-color: #ff7f7f; color: white"
                         onclick="filterDashboard('urgente', '{cliente}')">
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
                ["Todos", "Pendente", "Concluído", "Em Processamento"],
                key="status_filter"
            )

            # Filtro por Data
            col_data1, col_data2 = st.columns(2)
            with col_data1:
                data_inicial = st.date_input("Data inicial", value=None, key="filtro_data_inicial")
            with col_data2:
                data_final = st.date_input("Data final", value=None, key="filtro_data_final")

            # Aplicar filtros do dashboard
            # Aplicar filtros do dashboard e manter o DataFrame filtrado
            df_filtrado = df_pedidos.copy()
            filtro_aplicado = False
            
            if 'dashboard_filter' in st.session_state:
                dashboard_status = st.session_state.dashboard_filter.get('status')
                dashboard_cliente = st.session_state.dashboard_filter.get('cliente')

                if dashboard_status == 'urgente':
                    df_pedidos = df_pedidos[
                        (df_pedidos['Status'] == 'Pendente') & 
                        (df_pedidos['Urgente'].str.strip().str.lower() == 'sim')
                    df_filtrado = df_filtrado[
                        (df_filtrado['Status'] == 'Pendente') & 
                        (df_filtrado['Urgente'].str.strip().str.lower() == 'sim')
                    ]
                    filtro_aplicado = True
                elif dashboard_status and dashboard_status != 'todos':
                    df_pedidos = df_pedidos[df_pedidos['Status'] == dashboard_status]
                    df_filtrado = df_filtrado[df_filtrado['Status'] == dashboard_status]
                    filtro_aplicado = True

                if dashboard_cliente:
                    df_pedidos = df_pedidos[df_pedidos['Cliente'] == dashboard_cliente]
            # Aplicar filtros normais
                    df_filtrado = df_filtrado[df_filtrado['Cliente'] == dashboard_cliente]
                    filtro_aplicado = True
            # Aplicar filtros normais se não houver filtro do dashboard
            elif status_filtro != "Todos":
                df_pedidos = df_pedidos[df_pedidos["Status"] == status_filtro]
                df_filtrado = df_filtrado[df_filtrado["Status"] == status_filtro]
                filtro_aplicado = True

            # Aplicar filtro de data se selecionado
            if not df_pedidos.empty and (data_inicial or data_final):
                df_pedidos["Data_dt"] = pd.to_datetime(df_pedidos["Data"], format="%d/%m/%Y %H:%M", errors="coerce")
            if not df_filtrado.empty and (data_inicial or data_final):
                df_filtrado["Data_dt"] = pd.to_datetime(df_filtrado["Data"], format="%d/%m/%Y %H:%M", errors="coerce")
                if data_inicial:
                    df_pedidos = df_pedidos[df_pedidos["Data_dt"] >= pd.to_datetime(data_inicial)]
                    df_filtrado = df_filtrado[df_filtrado["Data_dt"] >= pd.to_datetime(data_inicial)]
                if data_final:
                    df_pedidos = df_pedidos[df_pedidos["Data_dt"] <= pd.to_datetime(data_final) + pd.Timedelta(days=1)]
                df_pedidos = df_pedidos.drop(columns=["Data_dt"])
                    df_filtrado = df_filtrado[df_filtrado["Data_dt"] <= pd.to_datetime(data_final) + pd.Timedelta(days=1)]
                df_filtrado = df_filtrado.drop(columns=["Data_dt"])
                filtro_aplicado = True

            if df_pedidos.empty:
            if df_filtrado.empty:
                st.warning("Nenhum pedido encontrado com os filtros selecionados.")
                return

            # Mostrar total de pedidos
            st.write(f"Total: {len(df_pedidos)} pedidos encontrados")
            # Mostrar total de pedidos encontrados com os filtros
            if filtro_aplicado:
                st.success(f"🔍 {len(df_filtrado)} pedidos encontrados com os filtros aplicados")
            else:
                st.write(f"Total: {len(df_filtrado)} pedidos")

            # Formatar DataFrame para exibição
            df_display = df_pedidos[[
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

            # Seleção do pedido
            # Seleção do pedido (agora usando o DataFrame filtrado)
            pedidos_filtrados = df_filtrado["Numero_Pedido"].tolist()
            
            # Adicionar mensagem informativa se houver filtros ativos
            if filtro_aplicado:
                st.info("📌 Mostrando apenas os pedidos dos filtros selecionados")
            
            pedido_selecionado = st.selectbox(
                "Selecione um pedido",
                [""] + df_pedidos["Numero_Pedido"].tolist()
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
                    st.write(f"**Status:** {detalhes['status']}")
                    
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