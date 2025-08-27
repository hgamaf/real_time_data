import pytest
import pandas as pd
import json
import tempfile
import os
from unittest.mock import Mock, patch
import sys

# Adicionar diretórios ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'csv-monitor'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'streamlit'))

# Mocks necessários
sys.modules['streamlit'] = Mock()
sys.modules['plotly.express'] = Mock()

from csv_producer import CSVMonitor


def test_end_to_end_data_flow():
    """Testa fluxo completo: CSV -> Kafka -> Dashboard"""
    # Dados de teste
    sample_data = pd.DataFrame({
        'id': [1, 2, 3],
        'nome': ['João', 'Maria', 'Pedro'],
        'idade': [25, 30, 35],
        'cidade': ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte'],
        'valor': [100.50, 250.75, 180.25]
    })
    
    # Criar arquivo CSV temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        sample_data.to_csv(f.name, index=False)
        temp_file = f.name
    
    try:
        # Mock do Kafka Producer
        mock_producer = Mock()
        sent_messages = []
        
        def capture_message(*args, **kwargs):
            sent_messages.append({
                'topic': args[0],
                'key': kwargs.get('key'),
                'value': kwargs.get('value')
            })
        
        mock_producer.produce.side_effect = capture_message
        
        # Testar envio de dados
        with patch('csv_producer.KafkaProducer', return_value=mock_producer):
            monitor = CSVMonitor(temp_file, 'csv-data')
            monitor.send_all_data()
            
            # Verificar se todas as mensagens foram enviadas
            assert len(sent_messages) == 3
            assert all(msg['topic'] == 'csv-data' for msg in sent_messages)
            
            # Verificar conteúdo das mensagens
            for i, msg in enumerate(sent_messages):
                data = json.loads(msg['value'].decode('utf-8'))
                assert data['id'] == sample_data.iloc[i]['id']
                assert data['nome'] == sample_data.iloc[i]['nome']
                assert 'timestamp' in data
                
    finally:
        os.unlink(temp_file)


def test_kafka_connection_error_handling():
    """Testa tratamento de erros de conexão com Kafka"""
    sample_data = pd.DataFrame({
        'id': [1],
        'nome': ['Teste'],
        'idade': [30],
        'cidade': ['Teste City'],
        'valor': [150.00]
    })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        sample_data.to_csv(f.name, index=False)
        temp_file = f.name
    
    try:
        # Simular erro de conexão
        with patch('csv_producer.KafkaProducer', side_effect=Exception("Connection failed")):
            with pytest.raises(Exception) as exc_info:
                CSVMonitor(temp_file, 'test-topic')
            
            assert "Connection failed" in str(exc_info.value)
            
    finally:
        os.unlink(temp_file)


def test_csv_file_monitoring():
    """Testa monitoramento de mudanças no arquivo CSV"""
    # Dados iniciais
    initial_data = pd.DataFrame({
        'id': [1, 2],
        'nome': ['João', 'Maria'],
        'idade': [25, 30],
        'cidade': ['São Paulo', 'Rio de Janeiro'],
        'valor': [100.50, 250.75]
    })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        initial_data.to_csv(f.name, index=False)
        temp_file = f.name
    
    try:
        mock_producer = Mock()
        
        with patch('csv_producer.KafkaProducer', return_value=mock_producer):
            monitor = CSVMonitor(temp_file, 'test-topic')
            
            # Primeira execução - deve processar dados existentes
            monitor.send_new_data()
            initial_calls = mock_producer.produce.call_count
            
            # Simular que arquivo não foi modificado
            monitor.send_new_data()
            # Não deve enviar novos dados
            assert mock_producer.produce.call_count == initial_calls
            
            # Simular modificação do arquivo
            monitor.last_modified = 0  # Forçar detecção de mudança
            monitor.send_new_data()
            # Deve processar novamente
            assert mock_producer.produce.call_count > initial_calls
            
    finally:
        os.unlink(temp_file)