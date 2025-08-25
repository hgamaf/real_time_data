import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard Real-Time CSV", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Caminho do arquivo CSV
CSV_FILE = "../data/input.csv"

def load_csv_data():
    """Carrega dados do arquivo CSV"""
    try:
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            df['timestamp_load'] = datetime.now().strftime("%H:%M:%S")
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao ler CSV: {e}")
        return pd.DataFrame()

def main():
    st.title("🎯 Dashboard Real-Time - Dados CSV")
    st.markdown("---")
    
    # Controles
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔄 Atualizar Dados", type="primary"):
            st.rerun()
    
    with col2:
        auto_refresh = st.checkbox("🔄 Auto-refresh (3s)", value=True)
    
    with col3:
        st.markdown(f"**📁 Arquivo:** `{CSV_FILE}`")
    
    # Carregar dados
    df = load_csv_data()
    
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
        
        # Informações do arquivo
        st.subheader("📄 Informações do Arquivo")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if os.path.exists(CSV_FILE):
                mod_time = os.path.getmtime(CSV_FILE)
                mod_time_str = datetime.fromtimestamp(mod_time).strftime("%d/%m/%Y %H:%M:%S")
                st.info(f"**Última modificação:** {mod_time_str}")
        
        with col2:
            st.info(f"**Total de linhas:** {len(df)}")
        
        with col3:
            st.info(f"**Atualizado em:** {datetime.now().strftime('%H:%M:%S')}")
        
    else:
        st.warning("📭 Nenhum dado encontrado no arquivo CSV.")
        st.markdown(f"""
        ### 📝 Como adicionar dados:
        1. Abra o arquivo: `{CSV_FILE}`
        2. Adicione uma nova linha no formato: `id,nome,idade,cidade,valor`
        3. Exemplo: `8,Roberto,45,Fortaleza,275.50`
        4. Salve o arquivo
        5. O dashboard será atualizado automaticamente
        """)
    
    # Auto-refresh
    if auto_refresh and not df.empty:
        time.sleep(3)
        st.rerun()

if __name__ == "__main__":
    main()