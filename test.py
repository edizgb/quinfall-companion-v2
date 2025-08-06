# test_ollama_integration.py
import requests
import json


def test_ollama_connection():
    try:
        # Provjera dostupnosti modela
        models = requests.get("http://localhost:11434/v1/models").json()
        print("Dostupni modeli:")
        for model in models['data']:
            print(f"- {model['id']}")

        # Test upita
        response = requests.post(
            "http://localhost:11434/v1/chat/completions",
            json={
                "model": "deepseek-coder:6.7b",
                "messages": [{
                    "role": "user",
                    "content": "Generiraj Python funkciju za izračun faktorijela"
                }]
            }
        )

        if response.status_code == 200:
            print("\nOdgovor od AI-a:")
            print(response.json()['choices'][0]['message']['content'])
            return True
        else:
            print(f"Greška u API pozivu: {response.status_code}")
            return False

    except Exception as e:
        print(f"Pogreška: {str(e)}")
        return False


if __name__ == "__main__":
    if test_ollama_connection():
        print("\n✅ Integracija je uspješna!")
    else:
        print("\n❌ Integracija nije uspjela. Provjerite postavke.")
