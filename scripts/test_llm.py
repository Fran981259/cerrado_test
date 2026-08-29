"""
Teste do LLM com modelos FREE do OpenRouter
"""

import os
import sys

# Carrega .env manualmente
env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

def test_free_models():
    """Testa modelos FREE do OpenRouter."""
    from app.llm_client import LLMClient, FREE_MODELS, test_llm_connection
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY não configurada")
        print("\nEdite o arquivo .env e adicione:")
        print("OPENROUTER_API_KEY=sk-or-v1-sua-key-aqui")
        return False
    
    print("="*60)
    print("TESTE: OpenRouter com modelos FREE")
    print("="*60)
    
    print("\n📋 Modelos FREE disponíveis:")
    for name, model in FREE_MODELS.items():
        print(f"   {name:15} → {model}")
    
    print("\n" + "="*60)
    print("TESTE: Conexão básica")
    print("="*60)
    
    if test_llm_connection():
        print("\n✅ Conexão OK!")
    else:
        print("\n❌ Falha na conexão")
        return False
    
    print("\n" + "="*60)
    print("TESTE: Tradução EN→PT")
    print("="*60)
    
    client = LLMClient()
    
    text_en = """OpenAI has announced GPT-5, its most advanced AI model yet.
The new system shows unprecedented reasoning capabilities and is 
expected to revolutionize the technology industry."""
    
    print(f"\nOriginal: {text_en[:80]}...")
    translated = client.translate_to_pt_br(text_en)
    print(f"Traduzido: {translated[:80]}..." if translated else "❌ Sem tradução")
    
    print("\n" + "="*60)
    print("TESTE: Reescrita como repórter")
    print("="*60)
    
    article = {
        'title': 'AI Breakthrough Announced',
        'summary': 'OpenAI launches new AI model with unprecedented capabilities.',
        'source': 'TechCrunch',
        'url': 'https://techcrunch.com/news/ai',
        'category': 'tech',
    }
    
    reporter_prompt = """Você é Enzo Bianchi, repórter de tecnologia do Atualiza Brasil.
Escreva de forma clara, técnica e acessível. Use dados quando disponíveis."""
    
    result = client.rewrite_article(
        article,
        reporter_prompt,
        "Por Enzo Bianchi, do Atualiza Brasil",
        category="tech"
    )
    
    if result.get('rewritten_content'):
        print(f"\n✅ Reescrito com sucesso!")
        print(f"\nConteúdo (primeiras 200 chars):")
        print(result['rewritten_content'][:200] + "...")
    else:
        print("\n❌ Falha na reescrita")
    
    return True


if __name__ == "__main__":
    try:
        success = test_free_models()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
