
CREATE TABLE VINA (
    id_vina       INT AUTO_INCREMENT PRIMARY KEY,
    rut_vina      VARCHAR(15) NOT NULL UNIQUE,
    nombre        VARCHAR(100) NOT NULL,
    direccion     VARCHAR(255) NOT NULL,
    region        VARCHAR(100) NOT NULL,
    sitio_web     VARCHAR(150)
) COMMENT = 'La viña OFRECE tours, DISPONE DE productos y EMITE comprobantes.';

CREATE TABLE CONTACTO_VINA (
    id_contacto INT AUTO_INCREMENT PRIMARY KEY,
    id_vina     INT NOT NULL,
    tipo        VARCHAR(20) CHECK (tipo IN ('Telefono', 'Correo')),
    valor       VARCHAR(100) NOT NULL,
    CONSTRAINT fk_contacto_vina FOREIGN KEY (id_vina) REFERENCES VINA(id_vina) ON DELETE CASCADE
);

CREATE TABLE TOUR (
    id_tour         INT AUTO_INCREMENT PRIMARY KEY,
    id_vina         INT NOT NULL,
    nombre_tour     VARCHAR(100) NOT NULL,
    descripcion     VARCHAR(500),
    duracion_min    INT NOT NULL,
    fec_hora_inicio DATETIME NOT NULL,
    precio_persona  DECIMAL(10,2) NOT NULL,
    cupo_max        INT NOT NULL,
    CONSTRAINT fk_vina_ofrece_tour FOREIGN KEY (id_vina) REFERENCES VINA(id_vina)
);

CREATE TABLE CLIENTE (
    id_cliente       INT AUTO_INCREMENT PRIMARY KEY,
    nombres          VARCHAR(100) NOT NULL,
    apellidos        VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    tipo_cliente     VARCHAR(20) CHECK (tipo_cliente IN ('Nacional', 'Internacional'))
) COMMENT = 'El cliente REALIZA reservas, EMITE valoraciones y OBTIENE comprobantes.';

CREATE TABLE CLIENTE_NACIONAL (
    id_cliente INT PRIMARY KEY,
    rut        VARCHAR(15) NOT NULL UNIQUE,
    CONSTRAINT fk_cli_nac_gen FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id_cliente) ON DELETE CASCADE
);

CREATE TABLE CLIENTE_INTERNACIONAL (
    id_cliente   INT PRIMARY KEY,
    pasaporte    VARCHAR(50) NOT NULL UNIQUE,
    nacionalidad VARCHAR(100) NOT NULL,
    CONSTRAINT fk_cli_int_gen FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id_cliente) ON DELETE CASCADE
);

CREATE TABLE CONTACTO_CLIENTE (
    id_contacto INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente  INT NOT NULL,
    tipo        VARCHAR(20) CHECK (tipo IN ('Telefono', 'Correo')),
    valor       VARCHAR(100) NOT NULL,
    CONSTRAINT fk_contacto_cliente FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id_cliente) ON DELETE CASCADE
);

CREATE TABLE DESCUENTO (
    id_descuento  INT AUTO_INCREMENT PRIMARY KEY,
    codigo        VARCHAR(50) NOT NULL UNIQUE,
    porcentaje    DECIMAL(5,2) NOT NULL CHECK (porcentaje > 0 AND porcentaje <= 100),
    fecha_venc    DATE NOT NULL,
    estado        VARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo'))
);

CREATE TABLE RESERVA (
    id_reserva      INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente      INT NOT NULL,
    id_tour         INT NOT NULL,
    fec_reserva     DATETIME DEFAULT CURRENT_TIMESTAMP,
    cant_personas   INT NOT NULL CHECK (cant_personas > 0),
    monto_total     DECIMAL(10,2) NOT NULL,
    estado_pago     VARCHAR(20) DEFAULT 'Pendiente' CHECK (estado_pago IN ('Pendiente', 'Pagado', 'Reembolsado')),
    estado_reserva  VARCHAR(20) DEFAULT 'Activa' CHECK (estado_reserva IN ('Activa', 'Cancelada', 'Finalizada')),
    asistio_tour    TINYINT(1) DEFAULT 0 CHECK (asistio_tour IN (0, 1)),
    CONSTRAINT fk_cliente_realiza_reserva FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id_cliente),
    CONSTRAINT fk_tour_corresponde_reserva FOREIGN KEY (id_tour) REFERENCES TOUR(id_tour)
) COMMENT = 'La reserva CORRESPONDE A un tour, REGISTRA acompañantes y APLICA descuentos.';

CREATE TABLE ACOMPANANTE (
    id_acompanante  INT AUTO_INCREMENT PRIMARY KEY,
    id_reserva      INT NOT NULL,
    nombres         VARCHAR(100) NOT NULL,
    apellidos       VARCHAR(100) NOT NULL,
    identificacion  VARCHAR(50) NOT NULL,
    CONSTRAINT fk_reserva_registra_acomp FOREIGN KEY (id_reserva) REFERENCES RESERVA(id_reserva) ON DELETE CASCADE
);

CREATE TABLE RESERVA_DESCUENTO (
    id_reserva       INT NOT NULL,
    id_descuento     INT NOT NULL,
    monto_descontado DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id_reserva, id_descuento),
    CONSTRAINT fk_reserva_aplica_desc FOREIGN KEY (id_reserva) REFERENCES RESERVA(id_reserva),
    CONSTRAINT fk_desc_aplicado_reserva FOREIGN KEY (id_descuento) REFERENCES DESCUENTO(id_descuento)
);

CREATE TABLE VALORACION (
    id_valoracion  INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente     INT NOT NULL,
    id_tour        INT NOT NULL,
    puntuacion     INT NOT NULL CHECK (puntuacion BETWEEN 1 AND 5),
    comentario     VARCHAR(1000),
    fec_valoracion DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cliente_emite_val FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id_cliente),
    CONSTRAINT fk_tour_recibe_val FOREIGN KEY (id_tour) REFERENCES TOUR(id_tour)
);

CREATE TABLE PRODUCTO (
    id_producto     INT AUTO_INCREMENT PRIMARY KEY,
    id_vina         INT NOT NULL,
    nombre          VARCHAR(150) NOT NULL,
    tipo_vino       VARCHAR(50),
    anada           INT,
    precio_unitario DECIMAL(10,2) NOT NULL,
    stock           INT DEFAULT 0 NOT NULL,
    CONSTRAINT fk_vina_dispone_producto FOREIGN KEY (id_vina) REFERENCES VINA(id_vina)
);

CREATE TABLE COMPROBANTE_VENTA (
    id_comprobante     INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente         INT NOT NULL,
    id_vina            INT NOT NULL,
    fec_venta          DATETIME DEFAULT CURRENT_TIMESTAMP,
    subtotal           DECIMAL(10,2) NOT NULL,
    descuento_aplicado DECIMAL(10,2) DEFAULT 0,
    total_final        DECIMAL(10,2) NOT NULL,
    metodo_pago        VARCHAR(50) NOT NULL,
    CONSTRAINT fk_cliente_obtiene_comp FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id_cliente),
    CONSTRAINT fk_vina_emite_comp FOREIGN KEY (id_vina) REFERENCES VINA(id_vina)
) COMMENT = 'El comprobante CONTIENE detalles de venta que INCLUYEN productos.';

CREATE TABLE DETALLE_VENTA (
    id_comprobante   INT NOT NULL,
    id_producto      INT NOT NULL,
    cantidad         INT NOT NULL CHECK (cantidad > 0),
    precio_historico DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id_comprobante, id_producto),
    CONSTRAINT fk_comp_contiene_detalle FOREIGN KEY (id_comprobante) REFERENCES COMPROBANTE_VENTA(id_comprobante) ON DELETE CASCADE,
    CONSTRAINT fk_producto_incluido_det FOREIGN KEY (id_producto) REFERENCES PRODUCTO(id_producto)
);