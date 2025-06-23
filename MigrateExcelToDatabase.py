import pandas as pd
import mysql.connector
import numpy as np

# Ruta del archivo Excel
file_path = "D:\\news-projects\\Documentos\\lentes2.xlsx"

# Leer el archivo Excel
#df = pd.read_excel(file_path, header=1)
df = pd.read_excel(file_path, header=0)

# Reemplaza los valores `nan` con `None`
df = df.replace({np.nan: None})

def create_unique_code(start, id, size=6):
    # Convierte el ID a cadena y calcula su longitud
    id_str = str(id)
    length = len(id_str)

    # Rellena con ceros a la izquierda si es necesario
    zeros = "0" * (size - length)

    # Concatena el prefijo, los ceros y el ID
    code = f"{start}-{zeros}{id_str}"
    return code

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
table_name = "products"

# Insertar los datos en la base de datos

position = 0
for index, row in df.iterrows():
    # insert in table at zero
    # code = create_unique_code('P', index, 6)

    # more products
    lastValue: int = 12473
    if index == 0:
        position = 1 + lastValue
    else:
        position = position + 1

    code = create_unique_code('P', position, 6)

    dchain_spec_status = 0
    material_group = ""
    sub_franchise = ""
    old_material_number = ""
    material = 0
    material_description = ""
    description = ""
    ean_upc = 0
    adn = 0
    mty = 0
    cd_mx = 0

    if 'dchain_spec_status' in df.columns:
        if row['dchain_spec_status'] is not None:
            dchain_spec_status = row['dchain_spec_status']

    if 'material_group' in df.columns:
        material_group = row['material_group']

    if 'sub_franchise' in df.columns:
        sub_franchise = row['sub_franchise']

    if 'old_material_number' in df.columns:
        old_material_number = row['old_material_number']

    if 'material' in df.columns:
        material = row['material']

    if 'material_description' in df.columns:
        material_description = row['material_description']

    if 'description' in df.columns:
        description = row['description']

    if 'ean_upc' in df.columns:
        ean_upc = row['ean_upc']

    if 'adn' in df.columns:
        if row['adn'] is not None:
           adn = row['adn']

    if 'mty' in df.columns:
       if row['mty'] is not None:
          mty = row['mty']

    if 'cd_mx' in df.columns:
       if row['cd_mx'] is not None:
          cd_mx = row['cd_mx']

    query = f"INSERT INTO {table_name} (number, purchase_price, sale_price, taxes, amount, minimum_amount, category, catalogue_id, unit_measurement_id, dchain_spec_status, material_group, sub_franchise, old_material_number, material, material_description, description, ean_upc, adn, mty, cd_mx, url_image, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (code, 0.00, 0.00, "", 0.00, 0.00, "", None, None, dchain_spec_status, material_group,
              sub_franchise, old_material_number, material, material_description,
              description, ean_upc, adn, mty, cd_mx, "", '2025-06-23 13:27:29',
              '2025-06-23 13:27:29')
    cursor.execute(query, values)

# Confirmar la transacción
connection.commit()

# Cerrar la conexión
cursor.close()
connection.close()

print("Datos importados exitosamente.")
