import os
import sys

def main():
    """Entry point principal do sistema Real-Time Data"""
    print("🎯 Real-Time Data Processing System")
    print("=" * 40)
    
    print("\n📁 Estrutura do projeto:")
    print("   • csv-monitor/    - Monitor de CSV + Kafka Producer")
    print("   • data/          - Dados de entrada (input.csv)")
    print("   • flink/         - Jobs de processamento Flink")
    print("   • streamlit/     - Dashboard de visualização")
    
    print("\n🚀 Para iniciar o sistema:")
    print("   python start.py")
    
    print("\n📋 Componentes individuais:")
    print("   • CSV Monitor:   cd csv-monitor && python csv_producer.py")
    print("   • Dashboard:     cd streamlit && streamlit run dashboard.py")
    print("   • Flink Job:     cd flink && python process_job.py")
    
    print("\n📊 Dados de exemplo em: data/input.csv")
    
    # Verificar se arquivo de dados existe
    data_file = os.path.join(os.path.dirname(__file__), "data", "input.csv")
    if os.path.exists(data_file):
        print(f"✅ Arquivo de dados encontrado: {data_file}")
    else:
        print(f"❌ Arquivo de dados não encontrado: {data_file}")


if __name__ == "__main__":
    main()
