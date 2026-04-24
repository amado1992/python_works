# Instalaciones necesarias
# pip install openai beautifulsoup4 requests tenacity

import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential


class PriceTracker:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2))
    def get_price(self, url: str) -> float:
        # 1. Obtener HTML
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; PriceBot/1.0)'
        })
        soup = BeautifulSoup(response.text, 'html.parser')

        # 2. Intentar con IA primero (más robusto)
        try:
            prompt = f"Extrae solo el número del precio de: {soup.get_text()[:3000]}"
            ai_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # O gpt-4-turbo para mejor precisión
                messages=[{"role": "user", "content": prompt}]
            )
            return float(ai_response.choices[0].message.content)
        except:
            # 3. Fallback: patrones regex comunes
            import re
            text = soup.get_text()
            patterns = [
                r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|€|EUR)',
                r'precio[:\s]*\$?\s*(\d+(?:\.\d{2})?)'
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return float(match.group(1).replace(',', ''))
        return None


# Uso
tracker = PriceTracker(openai_api_key="tu-key")
precio = tracker.get_price("https://ejemplo.com/producto")
print(f"💰 Precio: ${precio}")