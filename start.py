#!/usr/bin/env python3
"""
Script de inicialização do sistema Real-Time Data
"""
import subprocess
import sys
import time
import os

def run_command(command, cwd=None):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_docker():
    """Verifica se Docker está disponível"""
    success, _, _ = run_command("docker --version")
    return success

def start_infrastructure():
    """Inicia a infraestrutura (Kafka + Flink)"""
    print("🚀 Iniciando infraestrutura...")
    
    if not check_docker():
        print("❌ Docker não encontrado. Instale o Docker primeiro.")
        return False
    
    # Parar containers existentes
    print("🛑 Parando containers existentes...")
    run_command("docker-compose down")
    
    # Iniciar containers
    print("🐳 Iniciando containers...")
    success, stdout, stderr = run_command("docker-compose up -d")
    
    if not success:
        print(f"❌ Erro ao iniciar containers: {stderr}")
        return False
    
    print("✅ Containers iniciados com sucesso!")
    
    # Aguardar Kafka ficar pronto
    print("⏳ Aguardando Kafka ficar pronto...")
    for i in range(30):
        success, _, _ = run_command("docker-compose exec -T kafka kafka-topics --list --bootstrap-server localhost:9092")
        if success:
            print("✅ Kafka está pronto!")
            break
        time.sleep(2)
        print(f"   Tentativa {i+1}/30...")
    else:
        print("❌ Timeout aguardando Kafka")
        return False
    
    return True

def create_kafka_topic():
    """Cria o tópico Kafka necessário"""
    print("📝 Criando tópico Kafka...")
    success, _, _ = run_command(
        "docker-compose exec -T kafka kafka-topics --create --topic csv-data --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 --if-not-exists"
    )
    if success:
        print("✅ Tópico 'csv-data' criado/verificado!")
    else:
        print("⚠️  Tópico pode já existir ou houve erro")

def main():
    print("=" * 50)
    print("🎯 Real-Time Data System Starter")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("docker-compose.yml"):
        print("❌ Execute este script na pasta raiz do projeto (onde está o docker-compose.yml)")
        sys.exit(1)
    
    # Iniciar infraestrutura
    if not start_infrastructure():
        sys.exit(1)
    
    # Criar tópico
    create_kafka_topic()
    
    print("\n" + "=" * 50)
    print("✅ Sistema iniciado com sucesso!")
    print("=" * 50)
    print("🔗 Serviços disponíveis:")
    print("   • Kafka: localhost:9092")
    print("   • Flink Dashboard: http://localhost:8081")
    print("   • Zookeeper: localhost:2181")
    print("\n📋 Próximos passos:")
    print("   1. Execute: cd real_time_data/csv-monitor && python csv_producer.py")
    print("   2. Execute: cd real_time_data/streamlit && streamlit run dashboard.py")
    print("   3. Modifique o arquivo: real_time_data/data/input.csv")
    print("\n🛑 Para parar: docker-compose down")

if __name__ == "__main__":
    main()