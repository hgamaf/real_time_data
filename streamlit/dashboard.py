import streamlit as st
import pandas as pd
import plotly.express as px
from kafka import KafkaConsumer
import json
from datetime import datetime
import threading
import time

# Configuração do Kafka
KAFKA_BROKER = 'localhost:9092'
TOPIC = 'csv-data-processed'

class KafkaDataConsumer:
    def __init__(self):
        self.data = []
        self.consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            auto_offset_reset='earliest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=1000
        )
        self.running = True
        
    def start_consuming(self):
        """Inicia o consumo de mensagens em thread separada"""
        def consume():
            while self.running:
                try:
                    for message in self.consumer:
                        if not self.running:
                            break
                        self.data.append(message.value)
                        # Manter apenas os últimos 100 registros
                        if len(self.data) > 100:
                            self.data = self.data[-100:]
                except Exception as e:
                    print(f"Erro no consumidor: {e}")
                    time.sleep(1)
        
        self.thread = threading.Thread(target=consume)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_consuming(self):
        """Para o consumo de mensagens"""
        self.running = False
        self.consumer.close()
        if hasattr(self, 'thread'):
            self.thread.join()

def main():
    st.set_page_config(page_title="Dashboard de Dados CSV", layout="wide")
    st.title("Dashboard em Tempo Real - Dados CSV")
    
    # Inicializar consumidor
    if 'consumer' not in st.session_state:
        st.session_state.consumer = KafkaDataConsumer()
        st.session_state.consumer.start_consuming()
    
    # Atualizar dados a cada segundo
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            # Dados atuais
            current_data = st.session_state.consumer.data
            
            if current_data:
                df = pd.DataFrame(current_data)
                
                # Exibir métricas
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if 'valor' in df.columns:
                        total_valor = df['valor'].sum()
                        st.metric("Valor Total", f"R$ {total_valor:,.2f}")
                
                with col2:
                    if 'imposto' in df.columns:
                        total_imposto = df['imposto'].sum()
                        st.metric("Imposto Total", f"R$ {total_imposto:,.2f}")
                
                with col3:
                    total_registros = len(df)
                    st.metric("Total de Registros", total_registros)
                
                with col4:
                    if 'idade' in df.columns:
                        idade_media = df['idade'].mean()
                        st.metric("Idade Média", f"{idade_media:.1f} anos")
                
                # Gráficos
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'cidade' in df.columns and 'valor' in df.columns:
                        st.subheader("Valor por Cidade")
                        city_data = df.groupby('cidade')['valor'].sum().reset_index()
                        fig = px.bar(city_data, x='cidade', y='valor', 
                                    title="Valor Total por Cidade")
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if 'idade' in df.columns:
                        st.subheader("Distribuição de Idades")
                        fig = px.histogram(df, x='idade', nbins=10, 
                                          title="Distribuição de Idades")
                        st.plotly_chart(fig, use_container_width=True)
                
                # Tabela com dados recentes
                st.subheader("Dados Recentes")
                st.dataframe(df.tail(10))
            else:
                st.info("Aguardando dados... Verifique se o produtor está em execução.")
        
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if 'consumer' in st.session_state:
            st.session_state.consumer.stop_consuming()
    finally:
        if 'consumer' in st.session_state:
            st.session_state.consumer.stop_consuming()