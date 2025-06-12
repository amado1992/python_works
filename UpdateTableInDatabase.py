import pandas as pd
import mysql.connector
import numpy as np

# Ruta del archivo Excel
file_path = "D:\\news-projects\\Documentos\\inventories.xlsx"

sheets = ['Inventarios MTY', 'Inventario CDMX']  # Nombres exactos de las pestañas

# Configurar la conexión a la base de datos MySQL
connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="camvalcon_alcondb"
)

# Crear un cursor
cursor = connection.cursor()

# Verifica si la conexión está activa
if connection.is_connected():
    print("Conexión a la base de datos establecida correctamente.")
else:
    print("No se pudo establecer la conexión a la base de datos.")

# Nombre de la tabla en la base de datos
table_name = "inventories"

# Actualizar los datos en la base de datos

# Procesar cada hoja del Excel
for sheet in sheets:
    print(f"\nProcesando hoja: {sheet}")

    # Leer el archivo Excel
    df = pd.read_excel(file_path, sheet_name=sheet, header=0)

    # Reemplaza los valores `nan` con `None`
    df = df.replace({np.nan: None})

    for index, row in df.iterrows():
        quantity = 0
        folio = ''
        if row['quantity_update'] is not None:
           quantity = row['quantity_update']

        if row['folio'] is not None:
           folio = row['folio']

        query = f"UPDATE {table_name} SET quantity = %s WHERE folio = %s"
        values = (quantity, folio)
        cursor.execute(query, values)

# Confirmar la transacción
connection.commit()

# Cerrar la conexión
cursor.close()
connection.close()

print("Datos importados exitosamente.")
