import pytest
import pandas as pd
import json
from unittest.mock import Mock, patch
import sys
import os


def test_kafka_message_processing():
    """Testa processamento de mensagens Kafka"""
    # Simular mensagem JSON válida
    json_message = {
        'id': 1,
        'nome': 'Joao',
        'idade': 25,
        'cidade': 'Sao Paulo',
        'valor': 100.50,
        'timestamp': '2024-01-01T10:00:00'
    }
    
    # Converter para formato de mensagem Kafka
    json_str = json.dumps(json_message)
    json_bytes = json_str.encode('utf-8')
    
    # Processar mensagem
    decoded_data = json.loads(json_bytes.decode('utf-8'))
    
    assert decoded_data['id'] == 1
    assert decoded_data['nome'] == 'Joao'
    assert decoded_data['valor'] == 100.50
    assert 'timestamp' in decoded_data


def test_data_deduplication():
    """Testa remoção de duplicatas por ID"""
    # Dados com IDs duplicados
    df = pd.DataFrame({
        'id': [1, 2, 1, 3],
        'nome': ['Joao', 'Maria', 'Joao Updated', 'Pedro'],
        'valor': [100, 200, 150, 300]
    })
    
    # Remover duplicatas mantendo o último registro
    df_unique = df.drop_duplicates(subset=['id'], keep='last')
    
    assert len(df_unique) == 3  # Deve ter apenas 3 registros únicos
    
    # Verificar se manteve o registro mais recente do ID 1
    joao_record = df_unique[df_unique['id'] == 1].iloc[0]
    assert joao_record['nome'] == 'Joao Updated'
    assert joao_record['valor'] == 150


def test_metrics_calculation():
    """Testa cálculo de métricas básicas"""
    sample_data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'nome': ['Joao', 'Maria', 'Pedro', 'Ana', 'Carlos'],
        'idade': [25, 30, 35, 28, 42],
        'cidade': ['Sao Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 'Brasilia'],
        'valor': [100.50, 250.75, 180.25, 320.00, 95.80]
    })
    
    # Calcular métricas
    total_valor = sample_data['valor'].sum()
    valor_medio = sample_data['valor'].mean()
    total_registros = len(sample_data)
    idade_media = sample_data['idade'].mean()
    
    # Verificar resultados
    assert total_valor == 947.30
    assert round(valor_medio, 2) == 189.46
    assert total_registros == 5
    assert idade_media == 32.0
    
    # Testar agregação por cidade
    city_stats = sample_data.groupby('cidade')['valor'].sum()
    assert len(city_stats) == 5  # 5 cidades diferentes
    assert city_stats['Sao Paulo'] == 100.50