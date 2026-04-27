"""
Demostración práctica de RAG + MCP con MySQL local (XAMPP)
- RAG: recuperación semántica de datos de la BD para responder preguntas.
- MCP: herramientas que el LLM puede invocar para consultar o modificar la BD.
"""

import json
import mysql.connector
from typing import Dict, List, Any, Optional
import ollama

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np

    USE_EMBEDDINGS = True
except ImportError:
    USE_EMBEDDINGS = False
    print("⚠️ sentence-transformers no instalado. Se usará búsqueda por palabras clave (menos precisa).")

# ========== CONFIGURACIÓN DB ==========
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # tu contraseña de MySQL (XAMPP suele estar vacía)
    "database": "camvalcon_alcondb"  # cambia por tu base de datos
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Verifica si la conexión está activa
if get_connection().is_connected():
    print("Conexión a la base de datos establecida correctamente.")
else:
    print("No se pudo establecer la conexión a la base de datos.")

# ========== 1. RAG: Índice semántico y recuperador ==========
class SimpleRAG:
    def __init__(self, table_name: str, text_columns: List[str]):
        """
        table_name: tabla de la BD donde están los documentos.
        text_columns: columnas que contienen texto (se concatenarán).
        """
        self.table_name = table_name
        self.text_columns = text_columns
        self.documents = []  # lista de {"id": row_id, "text": texto_completo}
        self.index = None  # matriz de embeddings (si se usa)
        self.model = None

        # Cargar datos desde la BD
        self._load_documents()

        # Construir índice de búsqueda
        if USE_EMBEDDINGS and self.documents:
            print("📚 Cargando modelo de embeddings (puede tardar la primera vez)...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self._build_index()
        else:
            print("📚 Usando búsqueda por palabras clave (sin embeddings).")

    def _load_documents(self):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Obtener todos los registros de la tabla
            cursor.execute(f"SELECT * FROM {self.table_name}")
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            for row in rows:
                doc_id = row[0]  # asumiendo que la primera columna es PK
                # Concatenar el texto de las columnas seleccionadas
                text_parts = []
                for col in self.text_columns:
                    if col in column_names:
                        idx = column_names.index(col)
                        val = row[idx]
                        if val is not None:
                            text_parts.append(str(val))
                doc_text = " ".join(text_parts)
                if doc_text.strip():
                    self.documents.append({"id": doc_id, "text": doc_text})
            print(f"✅ Cargados {len(self.documents)} documentos desde la tabla '{self.table_name}'")
        except Exception as e:
            print(f"❌ Error cargando documentos: {e}")
        finally:
            cursor.close()
            conn.close()

    def _build_index(self):
        texts = [doc["text"] for doc in self.documents]
        embeddings = self.model.encode(texts, show_progress_bar=False)
        self.index = np.array(embeddings)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        if not self.documents:
            return []
        if USE_EMBEDDINGS and self.index is not None:
            # Búsqueda semántica
            q_emb = self.model.encode([query])[0]
            similarities = np.dot(self.index, q_emb) / (np.linalg.norm(self.index, axis=1) * np.linalg.norm(q_emb))
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            return [self.documents[i] for i in top_indices]
        else:
            # Búsqueda por palabras clave (fallback)
            query_terms = set(query.lower().split())
            scored = []
            for doc in self.documents:
                terms = set(doc["text"].lower().split())
                score = len(query_terms.intersection(terms))
                if score > 0:
                    scored.append((score, doc))
            scored.sort(reverse=True, key=lambda x: x[0])
            return [doc for _, doc in scored[:top_k]]

    def answer(self, query: str) -> str:
        retrieved = self.retrieve(query)
        if not retrieved:
            return "No se encontró información relevante en la base de datos."
        context = "\n".join([f"- {doc['text'][:300]}" for doc in retrieved])
        prompt = f"""Responde la siguiente pregunta usando SOLO la información proporcionada.
        Si la respuesta no está en el contexto, di que no lo sabes.

        Contexto:
        {context}

        Pregunta: {query}
        Respuesta:"""

        # Usar Ollama para generar respuesta (RAG)
        response = ollama.generate(model="llama3.2:1b", prompt=prompt)
        return response['response'].strip()


# ========== 2. MCP: Herramientas para interactuar con BD ==========
class MCPServer:
    def __init__(self):
        self.tools = {
            "list_tables": {
                "description": "Muestra todas las tablas de la base de datos.",
                "handler": self._list_tables
            },
            "query_data": {
                "description": "Ejecuta una consulta SELECT sobre cualquier tabla (solo lectura).",
                "params": ["sql_query"],
                "handler": self._query_data
            },
            "update_data": {
                "description": "Ejecuta una sentencia UPDATE (cuidado, modifica datos).",
                "params": ["sql_update"],
                "handler": self._update_data
            },
            "insert_data": {
                "description": "Inserta una nueva fila en una tabla.",
                "params": ["table", "values"],
                "handler": self._insert_data
            }
        }

    def _list_tables(self, args: Dict) -> str:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return json.dumps({"tables": tables}, indent=2)

    def _query_data(self, args: Dict) -> str:
        sql = args.get("sql_query", "").strip()
        if not sql.lower().startswith("select"):
            return "Error: Solo se permiten consultas SELECT"
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            return json.dumps({"rows": rows}, default=str, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            cursor.close()
            conn.close()

    def _update_data(self, args: Dict) -> str:
        sql = args.get("sql_update", "").strip()
        if not sql.lower().startswith("update"):
            return "Error: Solo se permiten sentencias UPDATE"
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            conn.commit()
            return f"✅ Actualizadas {cursor.rowcount} fila(s)."
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            cursor.close()
            conn.close()

    def _insert_data(self, args: Dict) -> str:
        table = args.get("table", "")
        values = args.get("values", {})
        if not table or not values:
            return "Error: Se requiere 'table' y 'values' (diccionario clave=valor)"
        columns = ", ".join(values.keys())
        placeholders = ", ".join(["%s"] * len(values))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, list(values.values()))
            conn.commit()
            return f"✅ Insertada 1 fila. Nuevo ID: {cursor.lastrowid}"
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            cursor.close()
            conn.close()

    def call_tool(self, tool_name: str, args: Dict = None) -> str:
        tool = self.tools.get(tool_name)
        if not tool:
            return f"Herramienta '{tool_name}' no disponible"
        return tool["handler"](args or {})


# ========== 3. AGENTE INTELIGENTE (integra MCP + RAG) ==========
class IntelligentAgent:
    def __init__(self, rag: SimpleRAG, mcp: MCPServer):
        self.rag = rag
        self.mcp = mcp
        self.model = "llama3.2:1b"

    def run(self, user_input: str) -> str:
        # Primero, el LLM decide si es una consulta RAG o necesita usar MCP.
        decision_prompt = f"""
        Eres un asistente que puede:
        1. Responder preguntas sobre datos existentes usando RAG (búsqueda semántica en la BD).
        2. Usar herramientas MCP para consultar o modificar la base de datos.

        Decide qué acción tomar:
        - Si la pregunta es sobre información que podría estar en los registros de la BD (ej. "qué productos hay" o "cuántos clientes") → responde "RAG".
        - Si la pregunta implica consultar tablas concretas, actualizar o insertar datos → responde "MCP". En ese caso, especifica la herramienta y argumentos.

        Usuario: {user_input}

        Respuesta (solo una línea): RAG | MCP:herramienta,parámetros
        """
        # Se usa generate sin stream para simplificar
        decision = ollama.generate(model=self.model, prompt=decision_prompt)['response'].strip()

        if decision.startswith("RAG"):
            # Usar RAG
            return self.rag.answer(user_input)
        elif decision.startswith("MCP"):
            # Parsear herramienta
            # Formato esperado: "MCP:list_tables" o "MCP:query_data,{'sql_query':'SELECT * FROM users'}"
            parts = decision.split(":", 1)[1].split(",", 1)
            tool_name = parts[0].strip()
            args = {}
            if len(parts) > 1:
                try:
                    args = json.loads(parts[1].replace("'", '"'))
                except:
                    args = {"sql_query": parts[1]} if tool_name == "query_data" else {}
            # Ejecutar herramienta
            result = self.mcp.call_tool(tool_name, args)
            # Usar LLM para dar una respuesta legible al usuario
            final_prompt = f"""
            El usuario preguntó: {user_input}
            Se invocó la herramienta {tool_name} y se obtuvo este resultado en JSON:
            {result}

            Genera una respuesta natural para el usuario basada en ese resultado.
            """
            response = ollama.generate(model=self.model, prompt=final_prompt)
            return response['response'].strip()
        else:
            return "No entendí tu petición. Intenta reformular."


# ========== 4. EJEMPLO DE USO INTERACTIVO ==========
def main():
    print("=" * 70)
    print("🔍 DEMOSTRACIÓN DE RAG + MCP con MySQL local")
    print("=" * 70)

    # Configuración inicial: necesitas una tabla con datos para RAG.
    # Crearemos una tabla de ejemplo si no existe.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100),
            descripcion TEXT,
            precio DECIMAL(10,2)
        )
    """)
    # Insertar datos de ejemplo si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO productos (nombre, descripcion, precio) VALUES (%s, %s, %s)",
            [
                ("Laptop Gamer", "Computadora portátil con RTX 4060", 1200.00),
                ("Mouse Inalámbrico", "Mouse ergonómico con batería recargable", 25.50),
                ("Teclado Mecánico", "Teclado RGB con switches azules", 75.00)
            ]
        )
        conn.commit()
        print("✅ Tabla 'productos' creada con datos de ejemplo.")
    cursor.close()
    conn.close()

    # Inicializar RAG sobre la tabla 'productos', usando columnas 'nombre' y 'descripcion'
    rag = SimpleRAG(table_name="productos", text_columns=["nombre", "descripcion"])
    mcp = MCPServer()
    agent = IntelligentAgent(rag, mcp)

    print("\n✨ Agente listo. Puedes preguntar sobre productos o pedir acciones (listar, insertar).")
    print("Ejemplos:")
    print("- '¿Qué productos tienen descuento?' (RAG)")
    print("- 'Muestra todas las tablas' (MCP)")
    print("- 'Inserta un nuevo producto Televisor 4K por 500 USD' (MCP)")
    print("- 'Actualiza el precio de la Laptop a 1150' (MCP)")
    print("- 'Salir' para terminar\n")

    while True:
        user_input = input("🗣️ Tú: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            break
        response = agent.run(user_input)
        print(f"🤖 Agente: {response}\n")


if __name__ == "__main__":
    main()