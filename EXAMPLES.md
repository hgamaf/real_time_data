# 📊 Exemplos Práticos - Real-Time Data System

## 🎯 Casos de Uso Reais

### 1. 💰 Monitoramento de Vendas

**Cenário**: Loja online quer acompanhar vendas em tempo real

```csv
id,produto,preco,categoria,vendedor
1,Notebook Dell,2500.00,Eletrônicos,João
2,Mouse Gamer,150.00,Acessórios,Maria
3,Teclado Mecânico,300.00,Acessórios,Pedro
4,Monitor 4K,1200.00,Eletrônicos,Ana
```

**Dashboard mostrará**:
- 💰 Faturamento total em tempo real
- 📊 Vendas por categoria
- 👥 Performance por vendedor
- 📈 Ticket médio

### 2. 🏥 Monitoramento de Pacientes

**Cenário**: Hospital monitora entrada de pacientes

```csv
id,nome,idade,setor,gravidade
1,Carlos Silva,45,UTI,Alta
2,Ana Costa,32,Emergência,Média
3,João Santos,67,Cardiologia,Baixa
4,Maria Oliveira,28,Pediatria,Média
```

**Dashboard mostrará**:
- 📋 Total de pacientes
- 🏥 Distribuição por setor
- ⚠️ Casos por gravidade
- 👥 Faixa etária

### 3. 📦 Logística e Entregas

**Cenário**: Empresa de entregas acompanha status

```csv
id,pedido,cidade,status,valor_frete
1,PED001,São Paulo,Entregue,25.00
2,PED002,Rio de Janeiro,Em Trânsito,30.00
3,PED003,Belo Horizonte,Pendente,20.00
4,PED004,Salvador,Entregue,35.00
```

**Dashboard mostrará**:
- 📦 Status das entregas
- 🗺️ Entregas por cidade
- 💰 Receita de frete
- ⏱️ Performance de entrega

## 🔧 Exemplos de Configuração

### Personalizar Métricas

```python
# Em dashboard.py, adicionar novas métricas
with col5:
    if 'categoria' in df.columns:
        categorias_unicas = df['categoria'].nunique()
        st.metric("📂 Categorias", categorias_unicas)
```

### Novos Tipos de Gráfico

```python
# Gráfico de linha temporal
if 'data' in df.columns:
    df['data'] = pd.to_datetime(df['data'])
    fig_timeline = px.line(df, x='data', y='valor', 
                          title="Evolução Temporal")
    st.plotly_chart(fig_timeline)
```

### Filtros Interativos

```python
# Adicionar filtros na sidebar
st.sidebar.header("Filtros")
cidade_filter = st.sidebar.multiselect(
    "Selecionar Cidades",
    options=df['cidade'].unique(),
    default=df['cidade'].unique()
)

# Aplicar filtro
df_filtered = df[df['cidade'].isin(cidade_filter)]
```

## 📊 Templates de CSV

### Template E-commerce
```csv
id,produto,preco,categoria,vendedor,data_venda
1,Smartphone,899.00,Eletrônicos,João,2025-08-25
2,Camiseta,49.90,Roupas,Maria,2025-08-25
3,Livro Python,79.90,Livros,Pedro,2025-08-25
```

### Template RH
```csv
id,funcionario,salario,departamento,tempo_empresa
1,Ana Silva,5500.00,TI,2.5
2,Carlos Santos,4200.00,Vendas,1.8
3,Maria Costa,6800.00,Gerência,5.2
```

### Template Financeiro
```csv
id,transacao,valor,tipo,categoria,data
1,Pagamento Fornecedor,-1500.00,Saída,Operacional,2025-08-25
2,Venda Produto,2300.00,Entrada,Receita,2025-08-25
3,Aluguel,-800.00,Saída,Fixo,2025-08-25
```

## 🚀 Scripts de Automação

### Gerador de Dados de Teste

```python
# generate_test_data.py
import pandas as pd
import random
from datetime import datetime, timedelta

def generate_sales_data(n_records=50):
    produtos = ['Notebook', 'Mouse', 'Teclado', 'Monitor', 'Headset']
    vendedores = ['João', 'Maria', 'Pedro', 'Ana', 'Carlos']
    
    data = []
    for i in range(1, n_records + 1):
        data.append({
            'id': i,
            'produto': random.choice(produtos),
            'preco': round(random.uniform(50, 3000), 2),
            'vendedor': random.choice(vendedores),
            'data': datetime.now() - timedelta(days=random.randint(0, 30))
        })
    
    df = pd.DataFrame(data)
    df.to_csv('data/input.csv', index=False)
    print(f"✅ Gerados {n_records} registros de teste")

if __name__ == "__main__":
    generate_sales_data()
```

### Simulador de Dados em Tempo Real

```python
# simulate_realtime.py
import time
import random
import pandas as pd

def add_random_sale():
    produtos = ['Notebook', 'Mouse', 'Teclado', 'Monitor']
    vendedores = ['João', 'Maria', 'Pedro', 'Ana']
    
    # Ler CSV atual
    try:
        df = pd.read_csv('data/input.csv')
        next_id = df['id'].max() + 1
    except:
        next_id = 1
    
    # Gerar nova venda
    nova_venda = f"{next_id},{random.choice(produtos)},{random.randint(100, 2000)}.00,Eletrônicos,{random.choice(vendedores)}\n"
    
    # Adicionar ao CSV
    with open('data/input.csv', 'a') as f:
        f.write(nova_venda)
    
    print(f"✅ Adicionada venda ID {next_id}")

# Simular vendas a cada 10 segundos
while True:
    add_random_sale()
    time.sleep(10)
```

## 🎨 Customizações Visuais

### Tema Escuro

```python
# Adicionar no início do dashboard.py
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    .metric-container {
        background-color: #262730;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)
```

### Cores Personalizadas

```python
# Paleta de cores customizada
colors = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e', 
    'success': '#2ca02c',
    'warning': '#d62728',
    'info': '#9467bd'
}

# Usar nas visualizações
fig = px.bar(data, color_discrete_sequence=[colors['primary']])
```

### Layout Responsivo

```python
# Adaptar layout para diferentes tamanhos
col_count = 4 if st.session_state.get('screen_width', 1200) > 800 else 2
cols = st.columns(col_count)
```

## 📱 Integração com APIs

### Webhook para Notificações

```python
import requests

def send_alert(message):
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    payload = {"text": message}
    requests.post(webhook_url, json=payload)

# Usar quando valor exceder limite
if total_valor > 10000:
    send_alert(f"🚨 Vendas ultrapassaram R$ {total_valor:,.2f}!")
```

### Integração com Banco de Dados

```python
import sqlite3

def save_to_database(df):
    conn = sqlite3.connect('data/sales.db')
    df.to_sql('sales', conn, if_exists='append', index=False)
    conn.close()

# Salvar dados periodicamente
if len(df) % 10 == 0:  # A cada 10 registros
    save_to_database(df)
```

## 🔔 Alertas e Notificações

### Sistema de Alertas

```python
def check_alerts(df):
    alerts = []
    
    # Alerta de valor alto
    high_values = df[df['valor'] > 1000]
    if not high_values.empty:
        alerts.append(f"🔥 {len(high_values)} vendas acima de R$ 1.000")
    
    # Alerta de baixa performance
    avg_value = df['valor'].mean()
    if avg_value < 100:
        alerts.append(f"⚠️ Ticket médio baixo: R$ {avg_value:.2f}")
    
    return alerts

# Mostrar alertas no dashboard
alerts = check_alerts(df)
for alert in alerts:
    st.warning(alert)
```

## 📊 Relatórios Automáticos

### Gerador de Relatório PDF

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_report(df):
    filename = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Título
    c.drawString(100, 750, "Relatório de Vendas")
    
    # Métricas
    c.drawString(100, 700, f"Total de Vendas: R$ {df['valor'].sum():,.2f}")
    c.drawString(100, 680, f"Ticket Médio: R$ {df['valor'].mean():,.2f}")
    c.drawString(100, 660, f"Total de Registros: {len(df)}")
    
    c.save()
    return filename
```

---

## 🎉 Conclusão dos Exemplos

Estes exemplos mostram a versatilidade do sistema para diferentes cenários:

- 💼 **Business Intelligence**: Dashboards executivos
- 🏥 **Saúde**: Monitoramento de pacientes  
- 📦 **Logística**: Rastreamento de entregas
- 💰 **Financeiro**: Controle de fluxo de caixa
- 🛒 **E-commerce**: Vendas em tempo real

**🚀 Adapte os exemplos para seu caso específico e crie dashboards poderosos!**