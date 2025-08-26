import pytest
import pandas as pd
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Adicionar o diretório streamlit ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'streamlit'))

# Mock do streamlit antes de importar o dashboard
sys.modules['streamlit'] = Mock()
sys.modules['plotly.express'] = Mock()

from dashboard import get_kafka_consumer, load_kafka_data, update_data


class TestDashboard:
    """Testes para o dashboard Streamlit"""
    
    @patch('dashboard.Consumer')
    def test_get_kafka_consumer_success(self, mock_consumer_class):
        """Testa criação bem-sucedida do consumer Kafka"""
        mock_consumer = Mock()
        mock_consumer_class.return_value = mock_consumer
        
        consumer = get_kafka_consumer()
        
        assert consumer is not None
        mock_consumer_class.assert_called_once()
        mock_consumer.subscribe.assert_called_once_with(['csv-data'])
    
    @patch('dashboard.Consumer')
    @patch('dashboard.st')
    def test_get_kafka_consumer_error(self, mock_st, mock_consumer_class):
        """Testa erro na criação do consumer Kafka"""
        mock_consumer_class.side_effect = Exception("Connection failed")
        
        consumer = get_kafka_consumer()
        
        assert consumer is None
        mock_st.error.assert_called_once()
    
    @patch('dashboard.get_kafka_consumer')
    def test_load_kafka_data_no_consumer(self, mock_get_consumer):
        """Testa carregamento de dados sem consumer"""
        mock_get_consumer.return_value = None
        
        df = load_kafka_data()
        
        assert isinstance(df, pd.DataFrame)
        assert df.empty
    
    @patch('dashboard.get_kafka_consumer')
    def test_load_kafka_data_with_messages(self, mock_get_consumer, kafka_message_mock):
        """Testa carregamento de dados com mensagens válidas"""
        mock_consumer = Mock()
        mock_get_consumer.return_value = mock_consumer
        
        # Simular mensagens do Kafka
        mock_consumer.poll.side_effect = [kafka_message_mock, None]
        
        df = load_kafka_data()
        
        assert not df.empty
        assert len(df) == 1
        assert 'id' in df.columns
        assert 'timestamp_load' in df.columns
    
    @patch('dashboard.get_kafka_consumer')
    def test_load_kafka_data_with_error_message(self, mock_get_consumer):
        """Testa carregamento com mensagem de erro do Kafka"""
        mock_consumer = Mock()
        mock_get_consumer.return_value = mock_consumer
        
        # Simular mensagem com erro
        error_message = Mock()
        error_message.error.return_value = Mock()
        error_message.error.return_value.code.return_value = 1  # Erro genérico
        
        mock_consumer.poll.side_effect = [error_message, None]
        
        df = load_kafka_data()
        
        assert isinstance(df, pd.DataFrame)
    
    @patch('dashboard.get_kafka_consumer')
    def test_load_kafka_data_invalid_json(self, mock_get_consumer):
        """Testa carregamento com JSON inválido"""
        mock_consumer = Mock()
        mock_get_consumer.return_value = mock_consumer
        
        # Simular mensagem com JSON inválido
        invalid_message = Mock()
        invalid_message.error.return_value = None
        invalid_message.value.return_value = b'invalid json'
        
        mock_consumer.poll.side_effect = [invalid_message, None]
        
        df = load_kafka_data()
        
        assert isinstance(df, pd.DataFrame)
        assert df.empty
    
    @patch('dashboard.load_kafka_data')
    @patch('dashboard.st')
    def test_update_data_empty_session_state(self, mock_st, mock_load_data, sample_csv_data):
        """Testa atualização de dados com session_state vazio"""
        # Configurar session_state mock
        mock_st.session_state = {'kafka_data': pd.DataFrame()}
        
        # Simular dados novos
        mock_load_data.return_value = sample_csv_data
        
        result = update_data()
        
        assert not result.empty
        assert len(result) == len(sample_csv_data)
    
    @patch('dashboard.load_kafka_data')
    @patch('dashboard.st')
    def test_update_data_merge_existing(self, mock_st, mock_load_data, sample_csv_data):
        """Testa merge de dados novos com existentes"""
        # Dados existentes
        existing_data = pd.DataFrame({
            'id': [1, 2],
            'nome': ['João', 'Maria'],
            'idade': [25, 30],
            'cidade': ['São Paulo', 'Rio de Janeiro'],
            'valor': [100.50, 250.75]
        })
        
        # Novos dados (com ID duplicado)
        new_data = pd.DataFrame({
            'id': [1, 3],
            'nome': ['João Updated', 'Pedro'],
            'idade': [26, 35],
            'cidade': ['São Paulo', 'Belo Horizonte'],
            'valor': [110.50, 180.25]
        })
        
        mock_st.session_state = {'kafka_data': existing_data}
        mock_load_data.return_value = new_data
        
        result = update_data()
        
        # Deve ter 3 registros únicos (IDs 1, 2, 3)
        assert len(result) == 3
        # ID 1 deve ter dados atualizados
        updated_record = result[result['id'] == 1].iloc[0]
        assert updated_record['nome'] == 'João Updated'
    
    @patch('dashboard.load_kafka_data')
    @patch('dashboard.st')
    def test_update_data_no_new_data(self, mock_st, mock_load_data):
        """Testa atualização sem novos dados"""
        existing_data = pd.DataFrame({
            'id': [1],
            'nome': ['João'],
            'idade': [25],
            'cidade': ['São Paulo'],
            'valor': [100.50]
        })
        
        mock_st.session_state = {'kafka_data': existing_data}
        mock_load_data.return_value = pd.DataFrame()
        
        result = update_data()
        
        # Deve retornar dados existentes
        assert len(result) == 1
        assert result.iloc[0]['nome'] == 'João'


class TestDataProcessing:
    """Testes para processamento de dados do dashboard"""
    
    def test_dataframe_deduplication(self):
        """Testa remoção de duplicatas baseada no ID"""
        # Dados com IDs duplicados
        df = pd.DataFrame({
            'id': [1, 2, 1, 3, 2],
            'nome': ['João', 'Maria', 'João Updated', 'Pedro', 'Maria Updated'],
            'valor': [100, 200, 150, 300, 250]
        })
        
        # Remover duplicatas mantendo o último
        df_unique = df.drop_duplicates(subset=['id'], keep='last')
        
        assert len(df_unique) == 3
        # Verificar se manteve os registros mais recentes
        joao_record = df_unique[df_unique['id'] == 1].iloc[0]
        assert joao_record['nome'] == 'João Updated'
        
        maria_record = df_unique[df_unique['id'] == 2].iloc[0]
        assert maria_record['nome'] == 'Maria Updated'
    
    def test_data_aggregation(self, sample_csv_data):
        """Testa agregação de dados por cidade"""
        city_stats = sample_csv_data.groupby('cidade').agg({
            'valor': ['sum', 'mean', 'count'],
            'idade': 'mean'
        }).round(2)
        
        assert not city_stats.empty
        assert len(city_stats) == sample_csv_data['cidade'].nunique()
        
        # Verificar se todas as colunas esperadas existem
        expected_columns = [('valor', 'sum'), ('valor', 'mean'), ('valor', 'count'), ('idade', 'mean')]
        for col in expected_columns:
            assert col in city_stats.columns
    
    def test_metrics_calculation(self, sample_csv_data):
        """Testa cálculo de métricas principais"""
        total_valor = sample_csv_data['valor'].sum()
        valor_medio = sample_csv_data['valor'].mean()
        total_registros = len(sample_csv_data)
        idade_media = sample_csv_data['idade'].mean()
        
        assert total_valor > 0
        assert valor_medio > 0
        assert total_registros == 5
        assert idade_media > 0
        
        # Verificar se métricas são consistentes
        assert total_valor == sample_csv_data['valor'].sum()
        assert valor_medio == total_valor / total_registros


class TestKafkaIntegration:
    """Testes de integração com Kafka"""
    
    @patch('dashboard.Consumer')
    def test_kafka_consumer_configuration(self, mock_consumer_class):
        """Testa configuração do consumer Kafka"""
        mock_consumer = Mock()
        mock_consumer_class.return_value = mock_consumer
        
        get_kafka_consumer()
        
        # Verificar se Consumer foi chamado com configurações corretas
        mock_consumer_class.assert_called_once()
        config = mock_consumer_class.call_args[0][0]
        
        assert config['bootstrap.servers'] == 'localhost:9092'
        assert config['group.id'] == 'dashboard-consumer'
        assert config['auto.offset.reset'] == 'earliest'
        assert config['enable.auto.commit'] is True
    
    def test_message_processing(self):
        """Testa processamento de mensagens Kafka"""
        # Simular mensagem JSON válida
        json_message = {
            'id': 1,
            'nome': 'João',
            'idade': 25,
            'cidade': 'São Paulo',
            'valor': 100.50,
            'timestamp': '2024-01-01T10:00:00'
        }
        
        # Converter para formato de mensagem Kafka
        json_str = json.dumps(json_message)
        json_bytes = json_str.encode('utf-8')
        
        # Processar mensagem
        decoded_data = json.loads(json_bytes.decode('utf-8'))
        
        assert decoded_data['id'] == 1
        assert decoded_data['nome'] == 'João'
        assert decoded_data['valor'] == 100.50
        assert 'timestamp' in decoded_data