# menu_interativo.py
import requests
import json
import os

API_URL = "http://127.0.0.1:5000/classify"

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def classificar(texto):
    try:
        response = requests.post(API_URL, json={"text": texto}, timeout=10)
        if response.status_code != 200:
            try:
                payload = response.json()
            except Exception:
                payload = {"erro_http": f"{response.status_code}", "body": response.text}
            return payload

        try:
            return response.json()
        except Exception as e:
            return {"erro": f"Resposta inválida da API: {e}", "body": response.text}
    except requests.exceptions.ConnectionError:
        return {"erro": "API não está rodando! Execute 'python app.py' primeiro"}
    except Exception as e:
        return {"erro": str(e)}

def menu():
    while True:
        limpar_tela()
        print("="*50)
        print("   🤖 FACTUM - Classificador de Notícias")
        print("="*50)
        print("\n1️⃣  Digite uma afirmação para classificar")
        print("2️⃣  Ver estatísticas")
        print("3️⃣  Sair")
        
        opcao = input("\n👉 Escolha uma opção: ")
        
        if opcao == "1":
            propria_noticia()
        elif opcao == "2":
            ver_estatisticas()
        elif opcao == "3":
            print("\n👋 Até logo!")
            break
        else:
            print("\n❌ Opção inválida!")
            input("\nPressione Enter para continuar...")

def propria_noticia():
    limpar_tela()
    print("="*50)
    print("   ✏️  CLASSIFICAR SUA NOTÍCIA")
    print("="*50)
    
    texto = input("\n📝 Digite a notícia/afirmação: ")
    
    if not texto.strip():
        print("\n❌ Texto vazio!")
        input("\nPressione Enter para continuar...")
        return
    
    print("\n⏳ Classificando...")
    resultado = classificar(texto)
    
    print("\n" + "="*50)
    print("📊 RESULTADO:")
    
    if "erro" in resultado:
        print(f"❌ {resultado['erro']}")
    else:
        classificacao = resultado.get('classification', resultado.get('result', {}).get('rating', 'N/A'))
        fonte = resultado.get('source', 'N/A')
        
        print(f"   📝 Texto: {texto}")
        print(f"   🏷️  Classificação: {classificacao}")
        print(f"   🔍 Fonte: {fonte}")
        
        if 'result' in resultado and 'source' in resultado['result']:
            print(f"   📌 Fact-check por: {resultado['result']['source']}")
    
    print("="*50)
    input("\nPressione Enter para continuar...")

def ver_estatisticas():
    limpar_tela()
    print("="*50)
    print("   📊 ESTATÍSTICAS DO SISTEMA")
    print("="*50)
    
    try:
        import sqlite3
        conn = sqlite3.connect("factum.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM predictions")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT source, COUNT(*) FROM predictions GROUP BY source")
        fontes = cursor.fetchall()
        
        cursor.execute("SELECT result, COUNT(*) FROM predictions GROUP BY result")
        resultados = cursor.fetchall()
        
        print(f"\n📈 Total de classificações: {total}")
        
        print("\n📊 Por fonte:")
        for fonte, count in fontes:
            print(f"   - {fonte}: {count}")
        
        print("\n🏷️  Por resultado:")
        for result, count in resultados:
            print(f"   - {result}: {count}")
        
        conn.close()
    except Exception as e:
        print(f"\n❌ Erro ao acessar banco: {e}")
    
    input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    # Verifica se a API está rodando
    try:
        requests.get("http://127.0.0.1:5000/", timeout=2)
    except:
        print("❌ ATENÇÃO: API não está rodando!")
        print("   Abra outro terminal e execute: python app.py")
        print("   Depois execute este programa novamente.")
        input("\nPressione Enter para sair...")
        exit()
    
    menu()