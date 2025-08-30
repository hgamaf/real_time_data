import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
from faker import Faker

class FakeDataProducer:
    def __init__(self, kafka_topic, bootstrap_servers='localhost:9092'):
        self.kafka_topic = kafka_topic
        self.fake = Faker('pt_BR')  # Usar dados brasileiros
        
        # Configurar cidades brasileiras para mais realismo
        self.cidades = [
            'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 
            'Fortaleza', 'Brasília', 'Curitiba', 'Recife', 'Porto Alegre',
            'Manaus', 'Belém', 'Goiânia', 'Campinas', 'São Luís', 'Maceió',
            'Natal', 'João Pessoa', 'Teresina', 'Campo Grande', 'Cuiabá'
        ]
        
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[bootstrap_servers],
                client_id='fake-data-producer',
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8'),
                request_timeout_ms=10000,
                retries=3
            )
            print(f"🚀 Conectado ao Kafka em {bootstrap_servers}")
            print(f"📡 Enviando dados para o tópico: {kafka_topic}")
        except Exception as e:
            print(f"❌ Erro ao conectar com Kafka: {e}")
            print("🔧 Certifique-se de que o Kafka está rodando em localhost:9092")
            raise
    
    def generate_fake_person(self):
        """Gera dados fake de uma pessoa"""
        return {
            'id': random.randint(1000, 9999),
            'nome': self.fake.name(),
            'idade': random.randint(18, 80),
            'cidade': random.choice(self.cidades),
            'valor': round(random.uniform(50.0, 2000.0), 2),
            'timestamp': datetime.now().isoformat(),
            'action': 'upsert'
        }
    
    def generate_fake_transaction(self):
        """Gera dados fake de transação financeira"""
        transaction_types = ['Compra', 'Venda', 'Transferência', 'Pagamento', 'Recebimento']
        
        return {
            'id': random.randint(10000, 99999),
            'nome': self.fake.name(),
            'idade': random.randint(18, 65),
            'cidade': random.choice(self.cidades),
            'valor': round(random.uniform(10.0, 5000.0), 2),
            'tipo_transacao': random.choice(transaction_types),
            'email': self.fake.email(),
            'telefone': self.fake.phone_number(),
            'timestamp': datetime.now().isoformat(),
            'action': 'upsert'
        }
    
    def generate_fake_sale(self):
        """Gera dados fake de vendas"""
        produtos = [
            'Notebook', 'Smartphone', 'Tablet', 'Fone de Ouvido', 'Mouse',
            'Teclado', 'Monitor', 'Impressora', 'Câmera', 'Smartwatch'
        ]
        
        return {
            'id': random.randint(1, 10000),
            'nome': self.fake.name(),
            'idade': random.randint(16, 70),
            'cidade': random.choice(self.cidades),
            'valor': round(random.uniform(25.0, 3000.0), 2),
            'produto': random.choice(produtos),
            'quantidade': random.randint(1, 5),
            'vendedor': self.fake.name(),
            'timestamp': datetime.now().isoformat(),
            'action': 'upsert'
        }
    
    def send_data(self, data):
        """Envia dados para o Kafka"""
        try:
            future = self.producer.send(
                self.kafka_topic,
                key=data['id'],
                value=data
            )
            future.get(timeout=10)
            return True
        except Exception as e:
            print(f"❌ Erro ao enviar dados: {e}")
            return False
    
    def run_person_generator(self, interval=5):
        """Executa gerador de pessoas continuamente"""
        print(f"👥 Gerando dados de pessoas a cada {interval} segundos...")
        print("🔄 Pressione Ctrl+C para parar")
        
        try:
            counter = 0
            while True:
                # Gerar dados fake
                person_data = self.generate_fake_person()
                
                # Enviar para Kafka
                if self.send_data(person_data):
                    counter += 1
                    print(f"✅ [{counter}] Enviado: {person_data['nome']}, {person_data['idade']} anos, "
                          f"{person_data['cidade']}, R$ {person_data['valor']}")
                else:
                    print(f"❌ Falha ao enviar dados")
                
                # Aguardar próximo envio
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Interrompendo gerador...")
        finally:
            self.producer.close()
            print("✅ Producer fechado")
    
    def run_transaction_generator(self, interval=5):
        """Executa gerador de transações continuamente"""
        print(f"💰 Gerando dados de transações a cada {interval} segundos...")
        print("🔄 Pressione Ctrl+C para parar")
        
        try:
            counter = 0
            while True:
                # Gerar dados fake
                transaction_data = self.generate_fake_transaction()
                
                # Enviar para Kafka
                if self.send_data(transaction_data):
                    counter += 1
                    print(f"✅ [{counter}] Transação: {transaction_data['nome']}, "
                          f"{transaction_data['tipo_transacao']}, R$ {transaction_data['valor']}")
                else:
                    print(f"❌ Falha ao enviar dados")
                
                # Aguardar próximo envio
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Interrompendo gerador...")
        finally:
            self.producer.close()
            print("✅ Producer fechado")
    
    def run_sales_generator(self, interval=5):
        """Executa gerador de vendas continuamente"""
        print(f"🛒 Gerando dados de vendas a cada {interval} segundos...")
        print("🔄 Pressione Ctrl+C para parar")
        
        try:
            counter = 0
            while True:
                # Gerar dados fake
                sale_data = self.generate_fake_sale()
                
                # Enviar para Kafka
                if self.send_data(sale_data):
                    counter += 1
                    print(f"✅ [{counter}] Venda: {sale_data['produto']} x{sale_data['quantidade']}, "
                          f"Cliente: {sale_data['nome']}, R$ {sale_data['valor']}")
                else:
                    print(f"❌ Falha ao enviar dados")
                
                # Aguardar próximo envio
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Interrompendo gerador...")
        finally:
            self.producer.close()
            print("✅ Producer fechado")

def main():
    """Função principal com menu de opções"""
    KAFKA_TOPIC = "csv-data"
    
    print("🎯 Gerador de Dados Fake para Kafka")
    print("=" * 40)
    print("Escolha o tipo de dados para gerar:")
    print("1. 👥 Pessoas (nome, idade, cidade, valor)")
    print("2. 💰 Transações (com email, telefone, tipo)")
    print("3. 🛒 Vendas (com produto, quantidade, vendedor)")
    print("=" * 40)
    
    try:
        choice = input("Digite sua escolha (1-3): ").strip()
        
        if choice not in ['1', '2', '3']:
            print("❌ Opção inválida!")
            return
        
        # Perguntar intervalo
        try:
            interval = int(input("Intervalo entre dados (segundos) [5]: ") or "5")
            if interval < 1:
                interval = 5
        except ValueError:
            interval = 5
        
        # Criar producer
        producer = FakeDataProducer(KAFKA_TOPIC)
        
        # Executar gerador escolhido
        if choice == '1':
            producer.run_person_generator(interval)
        elif choice == '2':
            producer.run_transaction_generator(interval)
        elif choice == '3':
            producer.run_sales_generator(interval)
            
    except KeyboardInterrupt:
        print("\n👋 Saindo...")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()