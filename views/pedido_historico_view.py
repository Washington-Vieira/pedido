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
        """, unsafe_allow_html=True)

    def mostrar_interface(self):
        """Mostra a interface do histórico de pedidos"""
        st.markdown("### 📋 Histórico de Pedidos")
        
        # Filtro de Status
        status_filtro = st.selectbox(
            "Status do Pedido",
            ["Todos", "Pendente", "Concluído", "Em Processamento"]
        )
        
        # Filtro por Data
        col_data1, col_data2 = st.columns(2)
        with col_data1:
            data_inicial = st.date_input("Data inicial", value=None, key="filtro_data_inicial")
        with col_data2:
            data_final = st.date_input("Data final", value=None, key="filtro_data_final")
        
        try:
            # Buscar pedidos
            df_pedidos = self.controller.buscar_pedidos(
                status=None if status_filtro == "Todos" else status_filtro
            )
            
            # Aplicar filtro de data se selecionado
            if not df_pedidos.empty and (data_inicial or data_final):
                df_pedidos["Data_dt"] = pd.to_datetime(df_pedidos["Data"], format="%d/%m/%Y %H:%M", errors="coerce")
                if data_inicial:
                    df_pedidos = df_pedidos[df_pedidos["Data_dt"] >= pd.to_datetime(data_inicial)]
                if data_final:
                    df_pedidos = df_pedidos[df_pedidos["Data_dt"] <= pd.to_datetime(data_final) + pd.Timedelta(days=1)]
                df_pedidos = df_pedidos.drop(columns=["Data_dt"])
            
            if df_pedidos.empty:
                st.warning("Por favor, recarregue a página e aguarde um minuto antes de tentar novamente.")
                return
            
            # Mostrar total de pedidos
            st.write(f"Total: {len(df_pedidos)} pedidos encontrados")
            
            # Formatar DataFrame para exibição
            df_display = df_pedidos[[
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
            pedido_selecionado = st.selectbox(
                "Selecione um pedido",
                [""] + df_pedidos["Numero_Pedido"].tolist()
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
        """Formata os detalhes do pedido para impressão em formato de comprovante fiscal"""
        # Definir largura do comprovante
        largura = 40
        linha = "-" * largura
        
        # Cabeçalho
        texto = f"""
{"REQUISIÇÃO DE BOBINA":^{largura}}
{linha}
{"COMPROVANTE DE PEDIDO":^{largura}}
{linha}

PEDIDO Nº: {pedido['info']['Numero_Pedido']}
DATA/HORA: {pedido['info']['Data']}
{linha}

INFORMAÇÕES DO PEDIDO:
CLIENTE: {pedido['info']['Cliente']}
RACK: {pedido['info']['RACK']}
LOCAL.: {pedido['info']['Localizacao']}
SOLIC.: {pedido['info']['Solicitante']}
STATUS: {pedido['status']}
{linha}

ITENS DO PEDIDO:"""

        # Adicionar itens
        total_itens = 0
        for idx, item in enumerate(pedido['itens'], 1):
            texto += f"""

ITEM {idx:02d}
COD.YAZAKI: {item['cod_yazaki']}
COD.CABO..: {item['codigo_cabo']}
SEÇÃO.....: {item['seccao']}
COR.......: {item['cor']}
QTDE......: {item['quantidade']}
{"-" * (largura-10)}"""
            total_itens += item['quantidade']

        # Adicionar total e observações
        texto += f"""

{linha}
TOTAL DE ITENS: {total_itens}
{linha}"""

        # Adicionar observações se houver
        if pedido['info'].get('Observacoes'):
            texto += f"""

OBSERVAÇÕES:
{pedido['info']['Observacoes']}
{linha}"""

        # Adicionar rodapé
        texto += f"""

{"MANTENHA ESTE COMPROVANTE":^{largura}}
{"PARA CONTROLE":^{largura}}

{datetime.now().strftime('%d/%m/%Y %H:%M:%S'):^{largura}}
{"." * largura}
"""
        
        return texto 