import pandas as pd
import mysql.connector
import numpy as np

# Ruta del archivo Excel
file_path = "D:\\news-projects\\Documentos\\inventoriespromoJunio2025\\inv6ags.xlsx"

# Nombres exactos de las pestañas
'''
sheets = [
    {'name': 'PEPSI', 'id': 4},
    {'name': 'GATORADE', 'id': 5},
    {'name': 'JARRITOS', 'id': 9},
    {'name': 'GATORLYTE', 'id': 2},
    {'name': 'NCBS', 'id': 8}
]
'''

'''
sheets = [
    {'name': 'PEPSI', 'id': 4},
    {'name': 'GATORADE', 'id': 5},
    {'name': 'GATORLYTE', 'id': 2},
    {'name': 'NCBS', 'id': 8},
    {'name': 'VARIOS', 'id': 3},
    {'name': 'SQUIRT', 'id': 6}
]
'''

sheets = [
    {'name': 'PEPSI', 'id': 4},
    {'name': 'GATORADE', 'id': 5},
    {'name': 'JARRITOS', 'id': 9},
    {'name': 'GATORLYTE', 'id': 2}
]

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
    database="promospc_db"
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
table_name_inventories = "inventories"


def product_exists(name):
    cleaned_name = name.strip().upper()  # Normalización
    queryProduct = f"SELECT id, name FROM {table_name} WHERE UPPER(name) = %s LIMIT 1"
    cursor.execute(queryProduct, (cleaned_name,))
    result = cursor.fetchone()
    return result if result else None


def inventory_exists(branch_office_id, product_id):
    queryProduct = f"SELECT id FROM {table_name_inventories} WHERE branch_offices_id = %s AND product_id = %s"
    cursor.execute(queryProduct, (branch_office_id, product_id))
    result = cursor.fetchone()
    return result if result else None


# Actualizar los datos en la base de datos
# count = 0
# count = 41

# count = 74
# countInventory = 77

# count = 102
# countInventory = 109

#count = 120
#countInventory = 128

count = 163
countInventory = 171

# Procesar cada hoja del Excel
for sheet in sheets:
    print(f"\nProcesando pestaña: {sheet['name']}")

    sheet_name = sheet['name']
    sheet_id = sheet['id']

    # Leer el archivo Excel
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)

    # Reemplaza los valores `nan` con `None`
    df = df.replace({np.nan: None})

    for index, row in df.iterrows():
        count += 1
        countInventory += 1

        # Verificar si TODAS las columnas de la fila están vacías (None, NaN, o vacío)
        if row.isna().all() or row.eq('').all():
            print(f"Fila {index} vacía. Deteniendo el procesamiento.")
            break  # Salir del bucle

        # insert in table at zero
        code = create_unique_code('P', count, 6)

        name = ""
        quantity = 0
        image = ""
        total = 0

        if 'name' in df.columns:
            if row['name'] is not None:
                name = row['name'].strip()
                print(f"NAME {name}")

        if 'image' in df.columns:
            if row['image'] is not None:
                image = row['image']
                print(f"IMAGE {image}")

        categorys_id = 8  # PROMOCIONAL
        existing_product = product_exists(name)

        if existing_product is None:
            print("NOT EXIST PRODUCT", existing_product)

            query = f"INSERT INTO {table_name} (number, name, description, material_description, brands_id, categorys_id, url_image, image, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (
                code, name, name, "", sheet_id, categorys_id, "", image, '2025-06-23 13:27:29', '2025-06-23 13:27:29')
            cursor.execute(query, values)

        existing_product_x = product_exists(name)
        if existing_product_x:
            print("EXIST PRODUCT", existing_product_x)
            product_id, name = existing_product_x

            # Sucursal
            gdl_id = 2  # ok
            leon_e_irapuato_id = 3  # ok
            morelia_id = 4  # ok
            vallarta_id = 5 # ok
            metro_id = 6 # ok
            aguascalientes_id = 7

            unit_measurements_id = 2  # Pieza
            physical_status_id = 1  # Good state

            if 'total' in df.columns:
                if row['total'] is not None:
                    total = row['total']

            if 'quantity' in df.columns:
                if row['quantity'] is not None:
                    quantity = row['quantity']

            codeInventory = create_unique_code('I', countInventory, 6)
            existing_inventory = inventory_exists(aguascalientes_id, product_id)

            if existing_inventory is None:
                queryInventory = f"INSERT INTO {table_name_inventories} (product_id, branch_offices_id, date_created, folio, bar_code, is_active, observation, expiration_date, batch, quantity, min_stock, sold, given, revenues, sale_price, purchase_price, user_created_id, user_updated_id, providers_id, unit_measurements_id, physical_status_id, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = (
                    product_id, aguascalientes_id, '2025-06-23 13:27:29', codeInventory, "", True, "", '2030-06-23 13:27:29',
                    "",
                    quantity, 1, total, 0, 0, 1, 1, None, None, None, unit_measurements_id, physical_status_id,
                    '2025-06-23 13:27:29', '2025-06-23 13:27:29')
                cursor.execute(queryInventory, values)

# Confirmar la transacción
connection.commit()

# Cerrar la conexión
cursor.close()
connection.close()

print("Datos importados exitosamente.")
