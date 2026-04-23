import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict
import math
from typing import List, Dict, Set, Tuple


class SimpleSearchEngine:
    """
    Un motor de búsqueda sencillo que implementa crawling, indexación y búsqueda
    con ranking TF-IDF (Term Frequency - Inverse Document Frequency)
    https://es.wikipedia.org/wiki/Tf-idf
    """

    def __init__(self):
        # Índice invertido: palabra -> { doc_id: [posiciones, frecuencias] }
        self.inverted_index = defaultdict(lambda: defaultdict(int))
        # Almacena los documentos (doc_id -> {"url": url, "title": title, "content": content})
        self.documents = {}
        # Para estadísticas globales
        self.idf_cache = {}
        self.next_doc_id = 0

    def crawl_and_index(self, url: str):
        """
        Descarga una página web, la procesa y la añade al índice.
        """
        print(f"🕷️ Rastreando: {url}")

        # --- 1. Descargar la página (Crawling) ---
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Lanza error si la descarga falla
            html_content = response.text
        except Exception as e:
            print(f"❌ Error al descargar {url}: {e}")
            return

        # --- 2. Extraer texto limpio (Parsing) ---
        soup = BeautifulSoup(html_content, 'html.parser')

        # === AJUSTA ESTOS SELECTORES SEGÚN LA PÁGINA ===
        # Método 1: buscar por clase
        precio_elemento = soup.find('span', class_='price')

        # Método 2: buscar por selector CSS (más preciso)
        precio_elemento = soup.select_one('.product-price .current-price')

        # Extraer el texto del precio
        if precio_elemento:
            precio = precio_elemento.get_text().strip()
            print(f"💰 Precio encontrado: {precio}")
        else:
            print("❌ No se encontró el precio")

        # Extraer título
        title = soup.title.string if soup.title else "Sin título"

        # Eliminar scripts, estilos, y metadatos que no queremos indexar
        for script in soup(["script", "style", "meta", "noscript", "header", "footer", "nav"]):
            script.decompose()

        # Obtener el texto plano
        text = soup.get_text(separator=' ', strip=True)

        # Limpiar el texto: eliminar caracteres especiales y normalizar
        text = re.sub(r'[^\w\s]', ' ', text)  # reemplaza signos de puntuación
        text = text.lower()  # Normalizar a minúsculas

        # --- 3. Indexar (Indexing) ---
        doc_id = self.next_doc_id
        self.next_doc_id += 1

        # Guardar el documento
        self.documents[doc_id] = {
            "url": url,
            "title": title,
            "content": text[:500] + "..."  # guardamos un preview para mostrar
        }

        # Dividir en palabras (tokens)
        words = text.split()

        # Construir índice invertido simple (palabra -> conteo en este documento)
        word_count = defaultdict(int)
        for word in words:
            if len(word) > 2:  # filtro: palabras de al menos 3 caracteres
                word_count[word] += 1

        # Agregar al índice global
        for word, count in word_count.items():
            self.inverted_index[word][doc_id] += count

            print(f"✅ WORD: {word}")

        print(f"✅ Indexado: {title} ({len(words)} palabras)")

    def compute_idf(self, word: str) -> float:
        """
        Calcula el IDF (Inverse Document Frequency) para una palabra.
        Mide cuán 'específica' es la palabra (menos común = más peso)
        """
        if word in self.idf_cache:
            return self.idf_cache[word]

        # Documentos que contienen esta palabra
        doc_count = len(self.inverted_index.get(word, {}))
        total_docs = len(self.documents)

        if doc_count == 0:
            return 0.0

        # Fórmula IDF = log( N / df )
        idf = math.log(total_docs / doc_count) + 1  # +1 para evitar valores negativos
        self.idf_cache[word] = idf
        return idf

    def search(self, query: str, top_n: int = 5) -> List[Tuple[str, str, float]]:
        """
        Busca documentos que coincidan con la consulta usando ranking TF-IDF.
        Retorna lista de (url, título, score) ordenada por relevancia.
        """
        # Limpiar la consulta
        query_words = re.sub(r'[^\w\s]', ' ', query.lower()).split()
        query_words = [w for w in query_words if len(w) > 2]

        if not query_words:
            return []

        # Diccionario para acumular por documento: doc_id -> score total
        scores = defaultdict(float)

        # Para cada palabra en la consulta
        for word in query_words:
            # Obtener el IDF
            idf = self.compute_idf(word)

            # Para cada documento que contiene la palabra
            for doc_id, tf in self.inverted_index.get(word, {}).items():
                # TF-IDF = TF * IDF (uso log TF para suavizar)
                tf_score = 1 + math.log(tf) if tf > 0 else 0
                scores[doc_id] += tf_score * idf

        # Ordenar documentos por puntuación (más alta = más relevante)
        ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

        # Construir resultados
        results = []
        for doc_id, score in ranked_docs:
            doc = self.documents[doc_id]
            results.append((doc["url"], doc["title"], round(score, 4)))

        return results

    def display_results(self, results: List[Tuple[str, str, float]]):
        """Muestra los resultados de búsqueda de forma amigable"""
        if not results:
            print("🔍 No se encontraron resultados.")
            return

        print(f"\n📊 Resultados encontrados: {len(results)}")
        print("=" * 70)
        for i, (url, title, score) in enumerate(results, 1):
            print(f"{i}. {title}")
            print(f"   URL: {url}")
            print(f"   Relevancia: {score}")
            print()

    def get_stats(self):
        """Muestra estadísticas del índice"""
        total_words = sum(len(idx) for idx in self.inverted_index.values())
        print("\n📈 Estadísticas del índice:")
        print(f"   Documentos indexados: {len(self.documents)}")
        print(f"   Términos únicos: {len(self.inverted_index)}")
        print(f"   Entradas en índice: {total_words}")


# ---------------------------
# EJEMPLO DE USO PRÁCTICO
# ---------------------------

def main():
    # 1. Crear el motor de búsqueda
    engine = SimpleSearchEngine()

    # 2. Indexar algunas páginas de ejemplo (puedes poner URLs reales)
    print("🚀 Iniciando rastreo e indexación...")
    print("-" * 50)

    # La técnica más usada por motores reales es empezar con una lista de URLs semilla
    # y seguir enlaces encontrados (recursivamente). Por simplicidad,
    # aquí indexamos unas URLs de muestra

    sample_urls = [
        "https://www.revolico.com/",
        "https://elyerromenu.com/",
        "https://es.wikipedia.org/wiki/Inteligencia_artificial",
        "https://es.wikipedia.org/wiki/Aprendizaje_autom%C3%A1tico",
        "https://es.wikipedia.org/wiki/Red_neuronal_artificial",
        "https://es.wikipedia.org/wiki/Procesamiento_de_lenguaje_natural",
        "https://es.wikipedia.org/wiki/Ciencia_de_datos",
        "https://dev.to/esdanielgomez/desarrollo-de-aplicaciones-web-con-asp-net-core-dotvvm-y-postgresql-46fa"
    ]

    for url in sample_urls:
        engine.crawl_and_index(url)

    # 3. Mostrar estadísticas
    engine.get_stats()

    # 4. Hacer búsquedas de ejemplo
    print("\n🔍 Realizando búsquedas...")
    print("-" * 50)

    queries = [
        "web",
        "redes neuronales",
        "procesamiento del lenguaje",
        "aprendizaje automático",
        "machine learning",
    ]

    for query in queries:
        print(f"\n📝 Consulta: '{query}'")
        results = engine.search(query, top_n=3)
        engine.display_results(results)


if __name__ == "__main__":
    main()