document.addEventListener('DOMContentLoaded', () => {
  const botonesAgregar = document.querySelectorAll('.btn-agregar');
  const contadorCarrito = document.getElementById('contador-carrito');
  const carritoItems = document.getElementById('carrito-items');
  const carritoTotal = document.getElementById('carrito-total');
  const btnVaciar = document.getElementById('btn-vaciar-carrito');
  const btnCheckout = document.getElementById('btn-checkout');

  // ==========================================
  // FUNCIÓN: Cargar pedidos desde el backend
  // ==========================================
  function cargarPedidosCarrito() {
    fetch('/obtener_pedidos')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          contadorCarrito.innerText = data.total_items;
          carritoTotal.innerText = `S/ ${data.total_precio.toFixed(2)}`;
          renderizarItems(data.pedidos);
        }
      })
      .catch(err => console.error('Error al cargar pedidos:', err));
  }

  // Exponer globalmente para que el script del HTML pueda llamarla
  window.cargarPedidosCarrito = cargarPedidosCarrito;

  // ==========================================
  // FUNCIÓN: Renderizar items en el panel
  // ==========================================
  function renderizarItems(pedidos) {
    if (pedidos.length === 0) {
      carritoItems.innerHTML = `
        <div class="carrito-vacio">
          <div class="carrito-vacio-icono">🍗</div>
          <p>Tu carrito está vacío</p>
          <span>¡Agrega algo delicioso!</span>
        </div>
      `;
      return;
    }

    carritoItems.innerHTML = pedidos.map(p => {
      // Si tiene imagen guardada, usarla; si no, un placeholder
      const imgSrc = p.imagen || '';
      const imgTag = imgSrc
        ? `<img class="carrito-item-img" src="${imgSrc}" alt="${p.producto}">`
        : `<div class="carrito-item-img" style="background:linear-gradient(135deg,#e4002b,#b80023);display:flex;align-items:center;justify-content:center;font-size:20px;">🍗</div>`;

      return `
        <div class="carrito-item" data-id="${p.id}">
          ${imgTag}
          <div class="carrito-item-info">
            <div class="carrito-item-nombre">${p.producto}</div>
            <div class="carrito-item-precio">S/ ${p.subtotal.toFixed(2)}</div>
          </div>
          <div class="carrito-item-controles">
            <button class="btn-cantidad btn-menos" data-id="${p.id}">−</button>
            <span class="cantidad-num">${p.cantidad}</span>
            <button class="btn-cantidad btn-mas" data-id="${p.id}">+</button>
            <button class="btn-eliminar" data-id="${p.id}">🗑</button>
          </div>
        </div>
      `;
    }).join('');

    // Event listeners para los botones de cada item
    carritoItems.querySelectorAll('.btn-menos').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-id');
        const item = btn.closest('.carrito-item');
        const cantidadSpan = item.querySelector('.cantidad-num');
        const cantidadActual = parseInt(cantidadSpan.textContent);
        if (cantidadActual <= 1) {
          eliminarPedido(id);
        } else {
          actualizarCantidad(id, cantidadActual - 1);
        }
      });
    });

    carritoItems.querySelectorAll('.btn-mas').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-id');
        const item = btn.closest('.carrito-item');
        const cantidadSpan = item.querySelector('.cantidad-num');
        const cantidadActual = parseInt(cantidadSpan.textContent);
        actualizarCantidad(id, cantidadActual + 1);
      });
    });

    carritoItems.querySelectorAll('.btn-eliminar').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-id');
        eliminarPedido(id);
      });
    });
  }

  // ==========================================
  // FUNCIÓN: Actualizar cantidad (UPDATE)
  // ==========================================
  function actualizarCantidad(id, nuevaCantidad) {
    fetch(`/actualizar_pedido/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cantidad: nuevaCantidad })
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          contadorCarrito.innerText = data.total_items;
          cargarPedidosCarrito();
        }
      })
      .catch(err => console.error('Error al actualizar:', err));
  }

  // ==========================================
  // FUNCIÓN: Eliminar un pedido (DELETE)
  // ==========================================
  function eliminarPedido(id) {
    const item = document.querySelector(`.carrito-item[data-id="${id}"]`);
    if (item) {
      item.style.transition = 'all 0.3s ease';
      item.style.transform = 'translateX(100%)';
      item.style.opacity = '0';
    }

    setTimeout(() => {
      fetch(`/eliminar_pedido/${id}`, { method: 'DELETE' })
        .then(res => res.json())
        .then(data => {
          if (data.status === 'success') {
            contadorCarrito.innerText = data.total_items;
            cargarPedidosCarrito();
          }
        })
        .catch(err => console.error('Error al eliminar:', err));
    }, 300);
  }

  // ==========================================
  // AGREGAR AL CARRITO (CREATE)
  // ==========================================
  if (botonesAgregar.length > 0) {
    botonesAgregar.forEach(boton => {
      boton.addEventListener('click', function() {
        const nombreProducto = this.getAttribute('data-nombre');
        const precioProducto = this.getAttribute('data-precio');
        const imagenProducto = this.getAttribute('data-img') || '';

        // Animación del botón
        const textoOriginal = this.textContent;
        this.textContent = '✓ Agregado';
        this.style.transform = 'scale(0.95)';
        this.style.background = '#2ecc40';
        this.style.color = 'white';
        setTimeout(() => {
          this.textContent = textoOriginal;
          this.style.transform = '';
          this.style.background = '';
          this.style.color = '';
        }, 600);

        fetch('/agregar_pedido', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            producto: nombreProducto,
            precio: precioProducto,
            imagen: imagenProducto
          })
        })
          .then(response => response.json())
          .then(data => {
            if (data.status === 'success') {
              contadorCarrito.innerText = data.total_items;
              // Si el panel está abierto, recargar items
              if (document.body.classList.contains('chat-activo')) {
                cargarPedidosCarrito();
              }
              console.log(data.mensaje);
            }
          })
          .catch(error => {
            console.error('Error al procesar la petición Fetch:', error);
          });
      });
    });
  }

  // ==========================================
  // VACIAR CARRITO (DELETE ALL)
  // ==========================================
  if (btnVaciar) {
    btnVaciar.addEventListener('click', () => {
      fetch('/vaciar_carrito', { method: 'DELETE' })
        .then(res => res.json())
        .then(data => {
          if (data.status === 'success') {
            contadorCarrito.innerText = 0;
            cargarPedidosCarrito();
          }
        })
        .catch(err => console.error('Error al vaciar:', err));
    });
  }

  // ==========================================
  // CHECKOUT (placeholder)
  // ==========================================
  if (btnCheckout) {
    btnCheckout.addEventListener('click', () => {
      alert('¡Pedido confirmado! 🎉');
    });
  }

  // Cargar pedidos al iniciar
  cargarPedidosCarrito();
});