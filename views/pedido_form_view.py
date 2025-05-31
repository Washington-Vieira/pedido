import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List

class PedidoFormView:
    def __init__(self, pedido_controller):
        self.pedido_controller = pedido_controller
        
    def _criar_formulario_pedido(self) -> Dict:
        """Cria o formulário de pedido com os campos necessários"""
        st.markdown("### 📝 Novo Pedido de Requisição")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cliente = st.selectbox(
                "Cliente",
                ["Renault", "Ford", "Volkswagen", "Outros"]
            )
            
            rack = st.text_input("RACK", key="rack")
            locacao = st.text_input("Localização", key="locacao")
            
        with col2:
            solicitante = st.text_input("Solicitante", key="solicitante")
            # Botão de seleção para urgência
            try:
                urgente = st.toggle("Esse pedido é urgente?", key="urgente_toggle")
            except AttributeError:
                urgente = st.checkbox("Esse pedido é urgente?", key="urgente_toggle")
            observacoes = st.text_area("Observações", key="observacoes")
        
        # Seção para adicionar itens
        st.markdown("### �� Itens do Pedido")
        
        itens = []
        for i in range(5):  # Permitir até 5 itens inicialmente
            st.markdown(f"#### Item {i+1}")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                cod_yazaki = st.text_input("Código Yazaki", key=f"cod_yazaki_{i}")
                codigo_cabo = st.text_input("Código Cabo", key=f"codigo_cabo_{i}")
                
            with col2:
                seccao = st.text_input("Seção", key=f"seccao_{i}")
                cor = st.text_input("Cor", key=f"cor_{i}")
                
            with col3:
                quantidade = st.number_input(
                    "Quantidade",
                    min_value=0,
                    value=0,
                    key=f"quantidade_{i}"
                )
            
            if cod_yazaki and quantidade > 0:
                itens.append({
                    "cod_yazaki": cod_yazaki,
                    "codigo_cabo": codigo_cabo,
                    "seccao": seccao,
                    "cor": cor,
                    "quantidade": quantidade
                })
        
        # Botão para salvar
        if st.button("💾 Salvar Pedido"):
            if not cliente or not rack or not solicitante:
                st.error("Por favor, preencha todos os campos obrigatórios!")
                return None
                
            if not itens:
                st.error("Adicione pelo menos um item ao pedido!")
                return None
                
            return {
                "cliente": cliente,
                "rack": rack,
                "locacao": locacao,
                "solicitante": solicitante,
                "observacoes": observacoes,
                "urgente": urgente,
                "data": datetime.now(),
                "itens": itens
            }
        
        return None

    def mostrar_interface(self):
        """Mostra a interface do formulário de pedido"""
        try:
            pedido = self._criar_formulario_pedido()
            
            if pedido:
                # Tentar salvar o pedido
                numero_pedido = self.pedido_controller.salvar_pedido(pedido)
                
                if numero_pedido:
                    st.success(f"""
                    ✅ Pedido {numero_pedido} criado com sucesso!
                    
                    Você pode visualizá-lo na aba de Histórico.
                    """)
                    
                    # Limpar formulário (recarregar página)
                    st.rerun()
                    
        except Exception as e:
            st.error(f"""
            ❌ Erro ao criar pedido:
            
            {str(e)}
            
            Por favor, tente novamente ou contate o suporte.
            """) 