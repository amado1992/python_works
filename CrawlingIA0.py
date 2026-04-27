import asyncio
import random
from datetime import datetime, UTC
from typing import Optional, List, Dict, Any
import aiohttp
from tenacity import retry, stop_after_attempt

class ProfessionalPriceExtractor:
    def __init__(self):
        self.strategies = [
            self.extract_with_llm,
            self.extract_with_regex,
            self.extract_with_selector,
            self.extract_with_ml,
        ]
        self.results_cache = {}

    def rotating_headers(self) -> Dict[str, str]:
        """Simula rotación de User-Agent."""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    # --- Estrategias de extracción (implementaciones mock para prueba) ---
    async def extract_with_llm(self, html: str) -> Dict[str, Any]:
        """Simula extracción con LLM."""
        await asyncio.sleep(0.1)  # simula latencia
        # Simula éxito aleatorio
        if random.random() > 0.3:
            return {'success': True, 'price': 99.99, 'strategy': 'llm'}
        else:
            return {'success': False, 'price': None, 'strategy': 'llm'}

    async def extract_with_regex(self, html: str) -> Dict[str, Any]:
        """Simula extracción con regex."""
        await asyncio.sleep(0.05)
        if random.random() > 0.2:
            return {'success': True, 'price': 99.99, 'strategy': 'regex'}
        else:
            return {'success': False, 'price': None, 'strategy': 'regex'}

    async def extract_with_selector(self, html: str) -> Dict[str, Any]:
        """Simula extracción con CSS selectors."""
        await asyncio.sleep(0.08)
        if random.random() > 0.4:
            return {'success': True, 'price': 99.99, 'strategy': 'selector'}
        else:
            return {'success': False, 'price': None, 'strategy': 'selector'}

    async def extract_with_ml(self, html: str) -> Dict[str, Any]:
        """Simula extracción con modelo local."""
        await asyncio.sleep(0.15)
        if random.random() > 0.5:
            return {'success': True, 'price': 99.99, 'strategy': 'ml'}
        else:
            return {'success': False, 'price': None, 'strategy': 'ml'}

    # --- Métodos auxiliares ---
    def validate_prices(self, results: List[Dict[str, Any]]) -> Optional[float]:
        """Votación por mayoría simple entre precios extraídos."""
        price_votes = {}
        for r in results:
            if r.get('success') and r.get('price') is not None:
                price = round(r['price'], 2)
                price_votes[price] = price_votes.get(price, 0) + 1
        if price_votes:
            # Mayoría simple
            return max(price_votes, key=price_votes.get)
        return None

    def calculate_confidence(self, results: List[Dict[str, Any]]) -> float:
        """Calcula confianza basada en cantidad de estrategias exitosas."""
        successful = sum(1 for r in results if r.get('success'))
        return successful / len(results) if results else 0.0

    def check_price_change(self, url: str, new_price: Optional[float]) -> bool:
        """Verifica si el precio cambió respecto a la última extracción (cache)."""
        if url in self.results_cache:
            old_price = self.results_cache[url].get('price')
            if old_price is not None and new_price is not None and old_price != new_price:
                return True
        return False

    async def send_alert(self, url: str, new_price: Optional[float]) -> None:
        """Simula envío de alerta (por ejemplo, email, webhook)."""
        print(f"⚠️ ALERTA: Precio cambiado para {url} -> {new_price}")

    @retry(stop=stop_after_attempt(3))
    async def extract(self, url: str) -> dict:
        """Extrae precio con múltiples estrategias y validación."""
        # 1. Obtener HTML
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.rotating_headers()) as response:
                html = await response.text()

        # 2. Ejecutar todas las estrategias en paralelo
        tasks = [strategy(html) for strategy in self.strategies]
        results = await asyncio.gather(*tasks)

        # 3. Validar resultados con IA (votación)
        final_price = self.validate_prices(results)

        # 4. Alertas de cambios significativos
        if self.check_price_change(url, final_price):
            await self.send_alert(url, final_price)

        # Guardar en caché para futuras comparaciones
        self.results_cache[url] = {'price': final_price, 'timestamp': datetime.now(UTC)}

        return {
            'url': url,
            'price': final_price,
            'confidence': self.calculate_confidence(results),
            'timestamp': datetime.now(UTC).isoformat(),
            'strategies_used': [r['strategy'] for r in results if r.get('success')]
        }

# ========== EJECUCIÓN DE PRUEBA ==========
async def main():
    extractor = ProfessionalPriceExtractor()
    # Usa una URL real que devuelva HTML (por ejemplo, una página de producto de prueba)
    test_url = "https://httpbin.org/html"  # Página de prueba que siempre devuelve HTML
    result = await extractor.extract(test_url)
    print("Resultado final:")
    for key, value in result.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())