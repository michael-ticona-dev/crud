#importamos Flask para crear la aplicacion
#render_templates cargar archivos de /templates :3
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from database.MySQL import db, Usuario, Pedido

app = Flask(__name__)
app.secret_key = 'kfc_secret_key_2026'

# Manejo automático de la conexión a MySQL
@app.before_request
def before_request():
    db.connect(reuse_if_open=True)

@app.teardown_request
def teardown_request(exc):
    if not db.is_closed():
        db.close()

# RUTA 1: Cargar la página principal (READ)
@app.route('/')
def inicio():
    # Contamos cuántos pedidos hay en total para mostrar en el ícono del carrito
    total_items = Pedido.select().count()
    return render_template('principal_inicio.html', total_items=total_items)

# RUTA 2: Recibir datos desde JavaScript (CREATE)
@app.route('/agregar_pedido', methods=['POST'])
def agregar_pedido():
    # Recibimos el JSON enviado por fetch() en carrito.js
    data = request.get_json() 
    
    # Extraemos los datos
    nombre_producto = data.get('producto')
    precio_producto = data.get('precio')
    imagen_producto = data.get('imagen', '')
    
    try:
        # IMPORTANTE: Como la tabla 'pedidos' exige un 'usuario_id',
        # asignamos temporalmente el ID 1. (Este usuario debe existir en MySQL)
        usuario_estatico_id = 1 
        
        # Guardamos en la base de datos usando Peewee
        Pedido.create(
            usuario_id=usuario_estatico_id,
            producto=nombre_producto,
            precio=precio_producto,
            imagen=imagen_producto,
            cantidad=1
        )
        
        # Contamos el nuevo total de pedidos
        total_items = Pedido.select().count()
        
        # Respondemos a JavaScript con éxito y el nuevo total
        return jsonify({
            "status": "success",
            "mensaje": f"{nombre_producto} guardado correctamente en MySQL",
            "total_items": total_items
        })
        
    except Exception as e:
        # Si algo falla (por ejemplo, si el usuario con ID 1 no existe)
        print(f"Error al guardar: {e}")
        return jsonify({"status": "error", "mensaje": str(e)}), 500

# RUTA 3: Obtener todos los pedidos del carrito (READ)
@app.route('/obtener_pedidos', methods=['GET'])
def obtener_pedidos():
    try:
        pedidos = (Pedido
                   .select()
                   .where(Pedido.estado == 'En carrito')
                   .order_by(Pedido.fecha_pedido.desc()))
        
        lista = []
        total_precio = 0
        for p in pedidos:
            subtotal = float(p.precio) * p.cantidad
            total_precio += subtotal
            lista.append({
                "id": p.id,
                "producto": p.producto,
                "precio": float(p.precio),
                "cantidad": p.cantidad,
                "subtotal": subtotal,
                "imagen": p.imagen or ''
            })
        
        return jsonify({
            "status": "success",
            "pedidos": lista,
            "total_items": len(lista),
            "total_precio": round(total_precio, 2)
        })
    except Exception as e:
        print(f"Error al obtener pedidos: {e}")
        return jsonify({"status": "error", "mensaje": str(e)}), 500

# RUTA 4: Actualizar cantidad de un pedido (UPDATE)
@app.route('/actualizar_pedido/<int:pedido_id>', methods=['PUT'])
def actualizar_pedido(pedido_id):
    try:
        data = request.get_json()
        nueva_cantidad = data.get('cantidad', 1)
        
        if nueva_cantidad < 1:
            return jsonify({"status": "error", "mensaje": "La cantidad debe ser al menos 1"}), 400
        
        pedido = Pedido.get_by_id(pedido_id)
        pedido.cantidad = nueva_cantidad
        pedido.save()
        
        total_items = Pedido.select().where(Pedido.estado == 'En carrito').count()
        
        return jsonify({
            "status": "success",
            "mensaje": f"Cantidad de {pedido.producto} actualizada a {nueva_cantidad}",
            "total_items": total_items
        })
    except Pedido.DoesNotExist:
        return jsonify({"status": "error", "mensaje": "Pedido no encontrado"}), 404
    except Exception as e:
        print(f"Error al actualizar: {e}")
        return jsonify({"status": "error", "mensaje": str(e)}), 500

# RUTA 5: Eliminar un pedido del carrito (DELETE)
@app.route('/eliminar_pedido/<int:pedido_id>', methods=['DELETE'])
def eliminar_pedido(pedido_id):
    try:
        pedido = Pedido.get_by_id(pedido_id)
        nombre = pedido.producto
        pedido.delete_instance()
        
        total_items = Pedido.select().where(Pedido.estado == 'En carrito').count()
        
        return jsonify({
            "status": "success",
            "mensaje": f"{nombre} eliminado del carrito",
            "total_items": total_items
        })
    except Pedido.DoesNotExist:
        return jsonify({"status": "error", "mensaje": "Pedido no encontrado"}), 404
    except Exception as e:
        print(f"Error al eliminar: {e}")
        return jsonify({"status": "error", "mensaje": str(e)}), 500

# RUTA 6: Vaciar todo el carrito (DELETE ALL)
@app.route('/vaciar_carrito', methods=['DELETE'])
def vaciar_carrito():
    try:
        Pedido.delete().where(Pedido.estado == 'En carrito').execute()
        return jsonify({
            "status": "success",
            "mensaje": "Carrito vaciado",
            "total_items": 0
        })
    except Exception as e:
        print(f"Error al vaciar carrito: {e}")
        return jsonify({"status": "error", "mensaje": str(e)}), 500

# =====================================================
# PÁGINA DE GESTIÓN DE PEDIDOS — CRUD COMPLETO
# =====================================================

# GESTIÓN: Página principal de gestión (READ - Listar todos)
@app.route('/pedidos')
def gestion_pedidos():
    """
    READ — Consulta todos los pedidos con Peewee ORM
    Usa .select() con JOIN para traer datos del usuario relacionado
    """
    pedidos = (Pedido
               .select(Pedido, Usuario)
               .join(Usuario)
               .order_by(Pedido.fecha_pedido.desc()))
    
    total_pedidos = pedidos.count()
    total_items = Pedido.select().count()
    
    return render_template('pedidos.html', 
                           pedidos=pedidos, 
                           total_pedidos=total_pedidos,
                           total_items=total_items)

# GESTIÓN: Crear nuevo pedido (CREATE)
@app.route('/pedidos/crear', methods=['POST'])
def crear_pedido():
    """
    CREATE — Inserta un nuevo registro con Pedido.create()
    Recibe datos del formulario HTML con request.form
    """
    producto = request.form.get('producto', '').strip()
    precio = request.form.get('precio', '0')
    cantidad = request.form.get('cantidad', '1')
    estado = request.form.get('estado', 'En carrito')
    
    if not producto:
        flash('El nombre del producto es obligatorio', 'error')
        return redirect(url_for('gestion_pedidos'))
    
    try:
        Pedido.create(
            usuario_id=1,
            producto=producto,
            precio=float(precio),
            cantidad=int(cantidad),
            estado=estado
        )
        flash(f'✅ Pedido "{producto}" creado exitosamente', 'success')
    except Exception as e:
        flash(f'❌ Error al crear pedido: {str(e)}', 'error')
    
    return redirect(url_for('gestion_pedidos'))

# GESTIÓN: Actualizar pedido existente (UPDATE)
@app.route('/pedidos/editar/<int:pedido_id>', methods=['POST'])
def editar_pedido(pedido_id):
    """
    UPDATE — Busca el registro con .get_by_id() y actualiza con .save()
    Modifica producto, precio, cantidad y estado
    """
    try:
        pedido = Pedido.get_by_id(pedido_id)
        
        pedido.producto = request.form.get('producto', pedido.producto).strip()
        pedido.precio = float(request.form.get('precio', pedido.precio))
        pedido.cantidad = int(request.form.get('cantidad', pedido.cantidad))
        pedido.estado = request.form.get('estado', pedido.estado)
        pedido.save()
        
        flash(f'✅ Pedido #{pedido_id} actualizado correctamente', 'success')
    except Pedido.DoesNotExist:
        flash(f'❌ Pedido #{pedido_id} no encontrado', 'error')
    except Exception as e:
        flash(f'❌ Error al actualizar: {str(e)}', 'error')
    
    return redirect(url_for('gestion_pedidos'))

# GESTIÓN: Eliminar pedido (DELETE)
@app.route('/pedidos/eliminar/<int:pedido_id>', methods=['POST'])
def borrar_pedido(pedido_id):
    """
    DELETE — Busca el registro con .get_by_id() y elimina con .delete_instance()
    Destruye el registro permanentemente de MySQL
    """
    try:
        pedido = Pedido.get_by_id(pedido_id)
        nombre = pedido.producto
        pedido.delete_instance()
        
        flash(f'🗑️ Pedido "{nombre}" eliminado correctamente', 'success')
    except Pedido.DoesNotExist:
        flash(f'❌ Pedido #{pedido_id} no encontrado', 'error')
    except Exception as e:
        flash(f'❌ Error al eliminar: {str(e)}', 'error')
    
    return redirect(url_for('gestion_pedidos'))

if __name__ == '__main__':
    app.run(debug=True)