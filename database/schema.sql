-- =========================================================
-- Base de Datos: Sistema de Pedidos
-- Proyecto Flask + Peewee + MySQL
-- =========================================================

CREATE DATABASE IF NOT EXISTS sistema_pedidos;
USE sistema_pedidos;


-- =========================================================
-- TABLA: usuarios
-- Almacena información de clientes registrados
-- =========================================================
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- TABLA: pedidos
-- Cada usuario puede crear múltiples pedidos
-- =========================================================
CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    producto VARCHAR(150) NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    precio DECIMAL(10,2) NOT NULL,
    estado VARCHAR(50) DEFAULT 'En carrito',
    fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Relación con usuarios
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    ON DELETE CASCADE
);