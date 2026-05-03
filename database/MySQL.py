from peewee import *
import pymysql
from datetime import datetime
# Permite usar PyMySQL como controlador
pymysql.install_as_MySQLdb()

# Configuración de conexión
db = MySQLDatabase(
    'sistema_pedidos',
    user='root',
    password='tutiopanchito',
    host='localhost',
    port=3306
)

# Modelo base
class BaseModel(Model):
    class Meta:
        database = db

# Modelo mapeado a la tabla "usuarios"
class Usuario(BaseModel):
    nombre = CharField(max_length=100)
    correo = CharField(max_length=150, unique=True)
    password = CharField(max_length=255)
    fecha_registro = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'usuarios'

# Modelo mapeado a la tabla "pedidos"
class Pedido(BaseModel):
    usuario_id = ForeignKeyField(Usuario, backref='pedidos', column_name='usuario_id')
    producto = CharField(max_length=150)
    cantidad = IntegerField(default=1)
    precio = DecimalField(max_digits=10, decimal_places=2)
    imagen = CharField(max_length=255, null=True, default=None)
    estado = CharField(max_length=50, default='En carrito')
    fecha_pedido = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'pedidos'

#PRUEBA DE CONEXION - no tocar jajaja
#try:
#    # Intentar conexión
#    db.connect()
#
#    if db.is_connection_usable():
#        print("Conexion exitosa con MySQL Workbench")
#    else:
#        print("La conexion existe pero no responde correctamente")
#
#except Exception as e:
#    print("Error de conexion:")
#    print(e)
#
#finally:
#    if not db.is_closed():
#        db.close()
#        print("Conexion cerrada correctamente")