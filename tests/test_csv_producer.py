import pytest
import pandas as pd
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from csv_monitor.csv_producer import CSVMonitor


class TestCSVMonitor:
    """Testes para a classe CSVMonitor"""
    
    def test_init_with_valid_file(self, temp_csv_file, mock_kafka_producer):
        """Testa inicialização com arquivo CSV válido"""
        with patch('csv_monitor.csv_producer.Producer', return_value=mock_kafka_producer):
            monitor = CSVMonitor(temp_csv_file, 'test-topic')
            assert monitor.csv_file == temp_csv_file
            assert monitor.kafka_topic == 'test-topic'
            assert monitor.last_modified == 0
            assert len(monitor.processed_rows) == 0
    
    def test_init_with_nonexistent_file(self, mock_kafka_producer):
        """Testa inicialização com arquivo inexistente"""
        with patch('csv_monitor.csv_producer.Producer', return_value=mock_kafka_producer):
            with pytest.raises(FileNotFoundError):
                CSVMonitor('nonexistent.csv', 'test-topic')
    
    def test_init_kafka_connection_error(self, temp_csv_file):
        """Testa erro de conexão com Kafka"""
        with patch('csv_monitor.csv_producer.Producer', side_effect=Exception("Connection failed")):
            with pytest.raises(Exception):
                CSVMonitor(temp_csv_file, 'test-topic')
    
    def test_read_csv_valid_file(self, temp_csv_file, sample_csv_data, mock_kafka_producer):
        """Testa leitura de arquivo CSV válido"""
        with patch('csv_monitor.csv_producer.Producer', return_value=mock_kafka_producer):
            monitor = CSVMonitor(temp_csv_file, 'test-topic')
            df = monitor.read_csv()
            
            assert not df.empty
            assert len(df) == len(sample_csv_data)
            assert list(df.columns) == list(sample_csv_data.columns)
    
    def test_read_csv_invalid_file(self, mock_kafka_producer):
        """Testa leitura de arquivo CSV inválido"""
        with patch('csv_monitor.csv_producer.Producer', return_value=mock_kafka_producer):
            # Criar arquivo temporário com conteúdo inválido
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write('invalid,csv,content\n')
                f.write('no,proper,structure')
                temp_file = f.name
            
            try:
                monitor = CSVMonitor(temp_file, 'test-topic')
                df = monitor.read_csv()
                # Deve retornar DataFrame vazio em caso de erro
                assert isinstance(df, pd.DataFrame)
            finally:
                os.unlink(temp_file)
    
    def test_get_row_hash(self, temp_csv_file, mock_kafka_producer):
        """Testa geração de hash para linha"""
        with patch('csv_monitor.csv_producer.Producer', return_value=mock_kafka_producer):
            monitor = CSVMonitor(temp_csv_file, 'test-topic')
            
            # Criar duas linhas idênticas
            row1 = pd.Series([1, 'João', 25, 'São Paulo', 100.50])
            row2 = pd.Series([1, 'João', 25, 'São Paulo', 100.50])
            row3 = pd.Series([2, 'Maria', 30, 'Rio de Janeiro', 250.75])
            
            hash1 = monitor.get_row_hash(row1)
            hash2 = monitor.get_row_hash(row2)
            hash3 = monitor.get_row_hash(row3)
            
            assert hash1 == hash2  # Linhas idênticas devem ter mesmo hash
            assert hash1 != hash3  # Linhas diferentes devem ter hashes diferentes
    
    def test_send_all_data(self, temp_csv_file, sample_csv_data, mock_kafka_producer):
        """Testa envio de todos os dados para Kafka"""
        with patch('csv_monitor.csv_producer.Producer', return_value=mock_kafka_producer):
            monitor = CSVMonitor(temp_csv_file, 'test-topic')
            monitor.send_all_data()
            
            # Verificar se produce foi chamado para cada linha
            assert mock_kafka_producer.produce.call_count == len(sample_csv_data)
            assert mock_kafka_producer.flush.call_count == len(sample_csv_data)
    
    def test_send_all_data_empty_csv(self, empty_csv_file, mock_kafka_producer):
        """Testa envio de dados com CSV vazio"""
        with patch('csv_monitor.csv_producer.Producer', return_value=mock_kafka_producer):
            monitor = CSVMonitor(empty_csv_file, 'test-topic')
            monitor.send_all_data()
            
            # Não deve chamar produce para CSV vazio
            mock_kafka_producer.produce.assert_not_called()
    
    def test_send_new_data_file_not_modified(self, temp_csv_file, mock_kafka_producer):
        """Testa envio de novos dados quando arquivo não foi modificado"""
        with patch('csv_monitor.csv_producer.Producer', return_value=mock_kafka_producer):
            monitor = CSVMonitor(temp_csv_file, 'test-topic')
            
            # Simular que arquivo já foi processado
            monitor.last_modified = os.path.getmtime(temp_csv_file)
            
            monitor.send_new_data()
            
            # Não deve enviar dados se arquivo não foi modificado
            mock_kafka_producer.produce.assert_not_called()
    
    def test_send_new_data_file_modified(self, temp_csv_file, sample_csv_data, mock_kafka_producer):
        """Testa envio de novos dados quando arquivo foi modificado"""
        with patch('csv_monitor.csv_producer.Producer', return_value=mock_kafka_producer):
            monitor = CSVMonitor(temp_csv_file, 'test-topic')
            
            # Simular que arquivo foi modificado
            monitor.last_modified = 0
            
            monitor.send_new_data()
            
            # Deve enviar todos os dados
            assert mock_kafka_producer.produce.call_count == len(sample_csv_data)
    
    @patch('time.sleep')
    def test_run_with_keyboard_interrupt(self, mock_sleep, temp_csv_file, mock_kafka_producer):
        """Testa execução do monitor com interrupção por teclado"""
        with patch('csv_monitor.csv_producer.Producer', return_value=mock_kafka_producer):
            monitor = CSVMonitor(temp_csv_file, 'test-topic')
            
            # Simular KeyboardInterrupt após primeira iteração
            mock_sleep.side_effect = KeyboardInterrupt()
            
            monitor.run(interval=1)
            
            # Verificar se producer foi fechado
            mock_kafka_producer.close.assert_called_once()
    
    def test_kafka_message_format(self, temp_csv_file, mock_kafka_producer):
        """Testa formato das mensagens enviadas para Kafka"""
        with patch('csv_monitor.csv_producer.Producer', return_value=mock_kafka_producer):
            monitor = CSVMonitor(temp_csv_file, 'test-topic')
            monitor.send_all_data()
            
            # Verificar se as mensagens têm o formato correto
            calls = mock_kafka_producer.produce.call_args_list
            
            for call in calls:
                args, kwargs = call
                
                # Verificar argumentos posicionais
                assert len(args) >= 1  # Pelo menos o tópico
                assert args[0] == 'test-topic'
                
                # Verificar se value é JSON válido
                if 'value' in kwargs:
                    json_data = json.loads(kwargs['value'].decode('utf-8'))
                    assert 'id' in json_data
                    assert 'timestamp' in json_data
    
    def test_producer_configuration(self, temp_csv_file):
        """Testa configuração do producer Kafka"""
        with patch('csv_monitor.csv_producer.Producer') as mock_producer_class:
            mock_producer = Mock()
            mock_producer_class.return_value = mock_producer
            
            CSVMonitor(temp_csv_file, 'test-topic', 'custom:9092')
            
            # Verificar se Producer foi chamado com configurações corretas
            mock_producer_class.assert_called_once()
            config = mock_producer_class.call_args[0][0]
            
            assert config['bootstrap.servers'] == 'custom:9092'
            assert config['client.id'] == 'csv-producer'
            assert 'socket.timeout.ms' in config
            assert 'message.timeout.ms' in config