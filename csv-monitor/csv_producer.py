import pandas as pd
from kafka import KafkaProducer
import json
import time
import os
from datetime import datetime

class CSVMonitor:
    def __init__(self, csv_file, kafka_topic, bootstrap_servers='localhost:9092'):
        self.csv_file = csv_file
        self.kafka_topic = kafka_topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.last_modified = 0
        self.processed_rows = set()
        
    def read_csv(self):
        """Lê o arquivo CSV e retorna os dados"""
        try:
            df = pd.read_csv(self.csv_file)
            return df
        except Exception as e:
            print(f"Erro ao ler CSV: {e}")
            return pd.DataFrame()
    
    def get_row_hash(self, row):
        """Gera um hash único para uma linha"""
        return hash(tuple(row))
    
    def send_new_data(self):
        """Verifica por novas linhas e envia para o Kafka"""
        current_modified = os.path.getmtime(self.csv_file)
        
        if current_modified > self.last_modified:
            print("Arquivo modificado. Processando novas linhas...")
            self.last_modified = current_modified
            
            df = self.read_csv()
            if df.empty:
                return
            
            for _, row in df.iterrows():
                row_hash = self.get_row_hash(row)
                
                if row_hash not in self.processed_rows:
                    # Converter a linha para dicionário
                    row_data = row.to_dict()
                    row_data['timestamp'] = datetime.now().isoformat()
                    
                    # Enviar para o Kafka
                    self.producer.send(self.kafka_topic, row_data)
                    print(f"Enviado: {row_data}")
                    
                    self.processed_rows.add(row_hash)
    
    def run(self, interval=5):
        """Executa o monitor continuamente"""
        print(f"Monitorando {self.csv_file} a cada {interval} segundos...")
        
        # Processar dados existentes na primeira execução
        self.send_new_data()
        
        try:
            while True:
                time.sleep(interval)
                self.send_new_data()
        except KeyboardInterrupt:
            print("Interrompendo monitor...")
        finally:
            self.producer.close()

if __name__ == "__main__":
    # Configurações
    CSV_FILE = "../data/input.csv"
    KAFKA_TOPIC = "csv-data"
    
    # Criar monitor e executar
    monitor = CSVMonitor(CSV_FILE, KAFKA_TOPIC)
    monitor.run(interval=3)