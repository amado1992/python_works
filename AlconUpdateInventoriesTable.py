import mysql.connector

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
quantity = 6
updated_at = '2025-11-28'
branch_office_id = 5

query = f"UPDATE {table_name} SET quantity = %s WHERE updated_at >= %s AND branch_offices_id = %s"
values = (quantity, updated_at, branch_office_id)
cursor.execute(query, values)

# Confirmar la transacción
connection.commit()

# Cerrar la conexión
cursor.close()
connection.close()

print("Datos importados exitosamente.")
