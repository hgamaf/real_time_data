import streamlit as st
import pandas as pd
import plotly.express as px
import time
import json
from datetime import datetime
from kafka import KafkaConsumer
from kafka.errors import KafkaError

# Configuração da página
st.set_page_config(
    page_title="Dashboard Real-Time Kafka", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configuração do Kafka Consumer
KAFKA_CONFIG = {
    'bootstrap_servers': ['localhost:9092'],
    'group_id': 'dashboard-consumer',
    'auto_offset_reset': 'earliest',
    'enable_auto_commit': True,
    'session_timeout_ms': 6000,
    'heartbeat_interval_ms': 3000,
    'value_deserializer': lambda m: json.loads(m.decode('utf-8')),
    'consumer_timeout_ms': 1000
}

@st.cache_resource
def get_kafka_consumer():
    """Cria e retorna um consumer Kafka"""
    try:
        consumer = KafkaConsumer('csv-data', **KAFKA_CONFIG)
        return consumer
    except Exception as e:
        st.error(f"Erro ao conectar com Kafka: {e}")
        return None

def load_kafka_data():
    """Carrega dados do Kafka"""
    consumer = get_kafka_consumer()
    if not consumer:
        return pd.DataFrame()
    
    messages = []
    try:
        # Consumir mensagens disponíveis (timeout já configurado no consumer)
        for message in consumer:
            try:
                data = message.value
                messages.append(data)
            except Exception as e:
                st.warning(f"Erro ao processar mensagem: {e}")
                continue
            
            # Limitar número de mensagens por poll para não travar a UI
            if len(messages) >= 100:
                break
                
    except Exception as e:
        # Timeout é esperado quando não há mensagens
        if "timeout" not in str(e).lower():
            st.error(f"Erro ao consumir do Kafka: {e}")
    
    # Converter para DataFrame
    if messages:
        df = pd.DataFrame(messages)
        # Remover duplicatas baseado no ID (manter a mais recente)
        if 'id' in df.columns:
            df = df.drop_duplicates(subset=['id'], keep='last')
        df['timestamp_load'] = datetime.now().strftime("%H:%M:%S")
        return df
    else:
        return pd.DataFrame()

# Armazenar dados no session state para persistência
if 'kafka_data' not in st.session_state:
    st.session_state.kafka_data = pd.DataFrame()

def update_data():
    """Atualiza dados do Kafka e merge com dados existentes"""
    new_data = load_kafka_data()
    
    if not new_data.empty:
        # Verificar se há comando de reset
        reset_messages = new_data[new_data.get('action') == 'reset']
        if not reset_messages.empty:
            print("Reset detectado - limpando dados existentes")
            st.session_state.kafka_data = pd.DataFrame()
            # Remover mensagens de reset dos novos dados
            new_data = new_data[new_data.get('action') != 'reset']
        
        # Processar dados normais
        if not new_data.empty:
            # Remover coluna 'action' se existir (não precisamos dela no dashboard)
            if 'action' in new_data.columns:
                new_data = new_data.drop('action', axis=1)
            
            if st.session_state.kafka_data.empty:
                st.session_state.kafka_data = new_data
            else:
                # Combinar dados novos com existentes
                combined = pd.concat([st.session_state.kafka_data, new_data], ignore_index=True)
                # Remover duplicatas baseado no ID (manter a mais recente)
                if 'id' in combined.columns:
                    combined = combined.drop_duplicates(subset=['id'], keep='last')
                st.session_state.kafka_data = combined
    
    return st.session_state.kafka_data

def main():
    st.title("🎯 Dashboard Real-Time - Kafka Stream")
    st.markdown("---")
    
    # Controles
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("🔄 Atualizar Dados", type="primary"):
            update_data()
            st.rerun()
    
    with col2:
        if st.button("🗑️ Limpar Cache"):
            st.session_state.kafka_data = pd.DataFrame()
            st.rerun()
    
    with col3:
        auto_refresh = st.checkbox("🔄 Auto-refresh (3s)", value=True)
    
    with col4:
        consumer = get_kafka_consumer()
        if consumer:
            st.markdown("**📡 Status:** 🟢 Conectado ao Kafka")
        else:
            st.markdown("**📡 Status:** 🔴 Desconectado do Kafka")
    
    # Carregar dados do Kafka
    df = update_data()
    
    if not df.empty:
        # Métricas principais
        st.subheader("📊 Métricas")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_valor = df['valor'].sum()
            st.metric("💰 Valor Total", f"R$ {total_valor:,.2f}")
        
        with col2:
            valor_medio = df['valor'].mean()
            st.metric("📈 Valor Médio", f"R$ {valor_medio:,.2f}")
        
        with col3:
            total_registros = len(df)
            st.metric("📋 Total Registros", total_registros)
        
        with col4:
            idade_media = df['idade'].mean()
            st.metric("👥 Idade Média", f"{idade_media:.1f} anos")
        
        # Gráficos
        st.subheader("📈 Visualizações")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**💰 Valor por Cidade**")
            city_data = df.groupby('cidade')['valor'].sum().reset_index()
            city_data = city_data.sort_values('valor', ascending=False)
            
            fig1 = px.bar(
                city_data, 
                x='cidade', 
                y='valor',
                title="Valor Total por Cidade",
                color='valor',
                color_continuous_scale='viridis'
            )
            fig1.update_layout(height=400)
            fig1.update_xaxes(tickangle=45)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.markdown("**👥 Distribuição de Idades**")
            fig2 = px.histogram(
                df, 
                x='idade', 
                nbins=10,
                title="Distribuição de Idades",
                color_discrete_sequence=['#1f77b4']
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Gráfico de pizza - Valor por Cidade
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🥧 Distribuição de Valores por Cidade**")
            fig3 = px.pie(
                city_data, 
                values='valor', 
                names='cidade',
                title="Percentual de Valores por Cidade"
            )
            fig3.update_layout(height=400)
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            st.markdown("**📊 Valor vs Idade**")
            fig4 = px.scatter(
                df, 
                x='idade', 
                y='valor',
                color='cidade',
                size='valor',
                title="Relação Valor x Idade",
                hover_data=['nome']
            )
            fig4.update_layout(height=400)
            st.plotly_chart(fig4, use_container_width=True)
        
        # Tabela de dados completa
        st.subheader("📋 Todos os Dados")
        
        # Ordenar por valor (maior primeiro)
        df_display = df.sort_values('valor', ascending=False)
        
        # Adicionar formatação
        df_display['valor_formatado'] = df_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
        
        st.dataframe(
            df_display[['id', 'nome', 'idade', 'cidade', 'valor_formatado', 'timestamp_load']].rename(columns={
                'valor_formatado': 'valor',
                'timestamp_load': 'última_atualização'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Estatísticas por cidade
        st.subheader("🏙️ Estatísticas por Cidade")
        city_stats = df.groupby('cidade').agg({
            'valor': ['sum', 'mean', 'count'],
            'idade': 'mean'
        }).round(2)
        city_stats.columns = ['Valor Total', 'Valor Médio', 'Qtd Registros', 'Idade Média']
        city_stats = city_stats.sort_values('Valor Total', ascending=False)
        
        # Formatar valores
        city_stats['Valor Total'] = city_stats['Valor Total'].apply(lambda x: f"R$ {x:,.2f}")
        city_stats['Valor Médio'] = city_stats['Valor Médio'].apply(lambda x: f"R$ {x:,.2f}")
        
        st.dataframe(city_stats, use_container_width=True)
        
        # Informações do Kafka
        st.subheader("📡 Informações do Stream")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Tópico Kafka:** csv-data")
        
        with col2:
            st.info(f"**Total de registros:** {len(df)}")
        
        with col3:
            st.info(f"**Última atualização:** {datetime.now().strftime('%H:%M:%S')}")
        
    else:
        st.warning("📭 Nenhum dado encontrado no stream Kafka.")
        st.markdown("""
        ### 📝 Como adicionar dados:
        1. Certifique-se de que o Kafka está rodando: `docker-compose up -d`
        2. Execute o CSV Producer: `cd csv-monitor && uv run python csv_producer.py`
        3. Adicione dados no arquivo CSV: `echo "8,Roberto,45,Fortaleza,275.50" >> data/input.csv`
        4. Os dados serão enviados para o Kafka automaticamente
        5. O dashboard consumirá do Kafka em tempo real
        
        ### 🔍 Monitoramento:
        - **Kafka UI**: http://localhost:8080
        - **Tópico**: csv-data
        - **Consumer Group**: dashboard-consumer
        """)
    
    # Auto-refresh
    if auto_refresh and not df.empty:
        time.sleep(3)
        st.rerun()

if __name__ == "__main__":
    main()