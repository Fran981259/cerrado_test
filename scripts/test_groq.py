"""
Teste do Groq — Atualiza Brasil
API gratuita com limites generosos.
"""

import os
import sys

# Load .env manually
env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value


def test_groq():
    """Testa Groq API."""
    from app.groq_client import GroqClient, test_groq_connection
    
    api_key = os.getenv("GROQ_API_KEY")
    
    print("="*60)
    print("TESTE: Groq API (100% Gratuita)")
    print("="*60)
    
    if not api_key or len(api_key) < 20:
        print("\n❌ GROQ_API_KEY não configurada!")
        print("\nPara configurar:")
        print("1. Acesse https://console.groq.com")
        print("2. Crie uma conta (grátis)")
        print("3. Dashboard → API Keys → Create Key")
        print("4. Cole no arquivo .env:")
        print("   GROQ_API_KEY=gsk_seu_codigo_aqui")
        return False
    
    # Testa conexão
    print(f"\n🔑 API Key: {api_key[:15]}...")
    print(f"📊 Limite FREE: 14 req/min, 5760 req/dia\n")
    
    if test_groq_connection():
        print("\n✅ Conexão OK!\n")
        
        # Testa tradução
        print("="*60)
        print("TESTE: Tradução EN → PT")
        print("="*60)
        
        client = GroqClient()
        
        text_en = """OpenAI has announced GPT-5, its most advanced AI model.
The new system shows unprecedented reasoning capabilities and is 
expected to revolutionize the technology industry worldwide."""
        
        print(f"\nOriginal: {text_en[:60]}...")
        translated = client.translate_to_pt_br(text_en)
        print(f"Traduzido: {translated[:80]}..." if translated else "❌ Sem tradução")
        
        # Testa reescrita
        print("\n" + "="*60)
        print("TESTE: Reescrita como Repórter")
        print("="*60)
        
        article = {
            'title': 'AI Breakthrough Announced',
            'summary': 'OpenAI launches new AI model with unprecedented capabilities.',
            'source': 'TechCrunch',
            'url': 'https://techcrunch.com/news/ai',
            'category': 'tech',
        }
        
        reporter_prompt = """Você é Enzo Bianchi, repórter de tecnologia.
Escreva de forma clara, técnica e acessível."""
        
        result = client.rewrite_article(
            article,
            reporter_prompt,
            "Por Enzo Bianchi, do Atualiza Brasil"
        )
        
        if result.get('rewritten_content'):
            print(f"\n✅ Reescrito com sucesso!")
            print(f"\n{result['rewritten_content'][:300]}...")
        else:
            print("\n❌ Falha na reescrita")
        
        return True
    else:
        return False


if __name__ == "__main__":
    try:
        success = test_groq()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
