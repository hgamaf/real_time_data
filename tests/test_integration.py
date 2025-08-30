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

from fake_data_producer import FakeDataProducer


def test_end_to_end_data_flow():
    """Testa fluxo completo: FakeProducer -> Kafka -> Dashboard"""
    # Mock do Kafka Producer
    mock_producer = Mock()
    sent_messages = []
    
    def capture_message(*args, **kwargs):
        sent_messages.append({
            'topic': args[0],
            'key': kwargs.get('key'),
            'value': kwargs.get('value')
        })
        # Retornar mock future
        mock_future = Mock()
        mock_future.get.return_value = None
        return mock_future
    
    mock_producer.send.side_effect = capture_message
    
    # Testar envio de dados fake
    with patch('fake_data_producer.KafkaProducer', return_value=mock_producer):
        producer = FakeDataProducer('csv-data')
        
        # Gerar e enviar 3 dados fake
        for _ in range(3):
            fake_data = producer.generate_fake_data()
            producer.send_data(fake_data)
        
        # Verificar se todas as mensagens foram enviadas
        assert len(sent_messages) == 3
        assert all(msg['topic'] == 'csv-data' for msg in sent_messages)
        
        # Verificar conteúdo das mensagens
        for msg in sent_messages:
            data = msg['value']
            assert 'id' in data
            assert 'nome' in data
            assert 'idade' in data
            assert 'cidade' in data
            assert 'valor' in data
            assert 'timestamp' in data
            
            # Verificar tipos e ranges
            assert isinstance(data['id'], int)
            assert isinstance(data['nome'], str)
            assert 18 <= data['idade'] <= 80
            assert isinstance(data['cidade'], str)
            assert 50.0 <= data['valor'] <= 2000.0


def test_kafka_connection_error_handling():
    """Testa tratamento de erros de conexão com Kafka"""
    # Simular erro de conexão
    with patch('fake_data_producer.KafkaProducer', side_effect=Exception("Connection failed")):
        with pytest.raises(Exception) as exc_info:
            FakeDataProducer('test-topic')
        
        assert "Connection failed" in str(exc_info.value)


def test_fake_data_continuous_generation():
    """Testa geração contínua de dados fake"""
    mock_producer = Mock()
    mock_future = Mock()
    mock_future.get.return_value = None
    mock_producer.send.return_value = mock_future
    
    with patch('fake_data_producer.KafkaProducer', return_value=mock_producer):
        producer = FakeDataProducer('test-topic')
        
        # Simular geração de múltiplos dados
        generated_data = []
        for _ in range(5):
            fake_data = producer.generate_fake_data()
            result = producer.send_data(fake_data)
            generated_data.append(fake_data)
            assert result is True
        
        # Verificar se todos os dados foram enviados
        assert mock_producer.send.call_count == 5
        
        # Verificar diversidade dos dados gerados
        ids = [data['id'] for data in generated_data]
        nomes = [data['nome'] for data in generated_data]
        cidades = [data['cidade'] for data in generated_data]
        
        # IDs devem ser únicos (alta probabilidade)
        assert len(set(ids)) >= 4  # Pelo menos 4 IDs diferentes
        
        # Nomes devem ser diferentes (alta probabilidade)
        assert len(set(nomes)) >= 3  # Pelo menos 3 nomes diferentes
        
        # Todas as cidades devem estar na lista válida
        for cidade in cidades:
            assert cidade in producer.cidades