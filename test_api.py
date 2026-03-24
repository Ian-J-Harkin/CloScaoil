import os
import sys
import litellm

def test_api_connection():
    print("--- 🛡️ ClóScaoil API Connection Diagnostics ---")
    
    # Provider Mapping
    providers = {
        "Gemini": ("GEMINI_API_KEY", "gemini/gemini-1.5-flash"),
        "OpenAI": ("OPENAI_API_KEY", "gpt-4o-mini"),
        "Claude": ("ANTHROPIC_API_KEY", "anthropic/claude-3-5-sonnet-20240620"),
        "OpenRouter": ("OPENROUTER_API_KEY", "openrouter/google/gemini-flash-1.5")
    }

    found_any = False
    
    for provider, (env_var, test_model) in providers.items():
        api_key = os.getenv(env_var)
        
        if api_key:
            found_any = True
            print(f"\n[+] {provider}: {env_var} found! (Key: {api_key[:5]}...{api_key[-4:]})")
            print(f"    Attempting handshake with {test_model}...")
            
            try:
                # Simple non-intensive handshake
                response = litellm.completion(
                    model=test_model,
                    messages=[{"role": "user", "content": "Hello. Respond with 'READY' if you hear me."}],
                    api_key=api_key,
                    max_tokens=10
                )
                result = response.choices[0].message.content.strip()
                print(f"    ✅ Success! Response: {result}")
            except Exception as e:
                print(f"    ❌ Connection Failed: {str(e)}")
        else:
            print(f"\n[-] {provider}: {env_var} NOT found in environment.")

    if not found_any:
        print("\n⚠️  No API keys were detected in your System Environment Variables.")
        print("    Please refer to USER_GUIDE.md for setup instructions.")
    
    print("\n---------------- Diagnostics Complete ----------------")

if __name__ == "__main__":
    test_api_connection()
