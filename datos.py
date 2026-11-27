
from flask import Flask, request, redirect, url_for, render_template_string, session, abort
from contextlib import contextmanager
from datetime import date
import sqlite3
import os
import secrets
import hmac

# ==================================================
# CONFIGURACION GENERAL
# ==================================================

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "prueba.db")


# ==================================================
# CONEXION A BASE DE DATOS
# ==================================================

@contextmanager
def conectar():
    conexion = sqlite3.connect(DB)
    conexion.row_factory = sqlite3.Row

    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


# ==================================================
# CREAR Y ACTUALIZAR TABLA
# ==================================================

def crear_tabla():

    with conectar() as conexion:

        conexion.execute("""
            CREATE TABLE IF NOT EXISTS ejemplo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                edad INTEGER,
                fecha_nacimiento TEXT
            )
        """)

        columnas = [
            fila["name"]
            for fila in conexion.execute(
                "PRAGMA table_info(ejemplo)"
            ).fetchall()
        ]

        if "edad" not in columnas:
            conexion.execute(
                "ALTER TABLE ejemplo ADD COLUMN edad INTEGER"
            )

        if "fecha_nacimiento" not in columnas:
            conexion.execute(
                "ALTER TABLE ejemplo ADD COLUMN fecha_nacimiento TEXT"
            )


# ==================================================
# CALCULAR EDAD
# ==================================================

def calcular_edad(fecha_nacimiento):

    nacimiento = date.fromisoformat(fecha_nacimiento)
    hoy = date.today()

    edad = hoy.year - nacimiento.year

    if (hoy.month, hoy.day) < (nacimiento.month, nacimiento.day):
        edad -= 1

    return edad


# ==================================================
# SEGURIDAD CSRF
# ==================================================

def obtener_token():

    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)

    return session["csrf_token"]


@app.before_request
def verificar_token():

    if request.method == "POST":

        token = request.form.get("csrf_token", "")
        esperado = session.get("csrf_token", "")

        if not esperado or not hmac.compare_digest(token, esperado):
            abort(400, description="Token de seguridad inválido.")


# ==================================================
# DISEÑO MILITAR HTML Y CSS
# ==================================================

HTML = """
<!DOCTYPE html>
<html lang="es">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>COMMAND CENTER | Registro</title>

<style>

:root {
    --verde: #253629;
    --verde-claro: #3c563c;
    --negro: #111711;
    --arena: #c4b58a;
    --fondo: #171e19;
    --panel: #222d24;
    --blanco: #e7eadf;
    --rojo: #a83b32;
    --borde: #52624c;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    background:
        radial-gradient(circle at top, #354535 0%, #171e19 65%);
    color: var(--blanco);
    min-height: 100vh;
}

/* ENCABEZADO */

header {
    background: linear-gradient(120deg, #101710, #344735);
    border-bottom: 4px solid var(--arena);
    padding: 28px 15px;
    text-align: center;
}

header h1 {
    color: var(--arena);
    font-size: 30px;
    letter-spacing: 3px;
}

header p {
    color: #cbd5bd;
    margin-top: 10px;
    letter-spacing: 2px;
    font-size: 12px;
}

.estado {
    display: inline-block;
    margin-top: 15px;
    padding: 7px 15px;
    border: 1px solid #71866b;
    border-radius: 4px;
    color: #b9d5a7;
    font-size: 11px;
    letter-spacing: 2px;
}

/* CONTENEDOR */

.contenedor {
    max-width: 1150px;
    margin: 30px auto;
    padding: 15px;
}

/* PANELES */

.panel {
    background: linear-gradient(145deg, #29362b, #1c261e);
    border: 1px solid var(--borde);
    border-left: 5px solid var(--arena);
    padding: 25px;
    margin-bottom: 25px;
    border-radius: 8px;
    box-shadow: 0 8px 25px #0006;
}

.panel h2 {
    color: var(--arena);
    font-size: 19px;
    margin-bottom: 22px;
    letter-spacing: 1px;
}

.descripcion {
    color: #aab5a5;
    font-size: 13px;
    margin-bottom: 20px;
}

/* ESTADISTICAS */

.estadisticas {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-bottom: 25px;
}

.tarjeta {
    background: #263529;
    border: 1px solid var(--borde);
    padding: 22px;
    border-radius: 7px;
    text-align: center;
}

.tarjeta h3 {
    color: #b5c0a9;
    font-size: 12px;
    letter-spacing: 1px;
}

.tarjeta h2 {
    font-size: 34px;
    color: var(--arena);
    margin-top: 12px;
}

/* FORMULARIOS */

.grupo {
    margin-bottom: 17px;
}

label {
    display: block;
    color: #d1d9c9;
    margin-bottom: 9px;
    font-size: 13px;
    font-weight: bold;
}

input {
    width: 100%;
    padding: 14px;
    background: #111a13;
    color: white;
    border: 1px solid #53644f;
    border-radius: 5px;
    font-size: 15px;
}

input:focus {
    outline: 2px solid var(--arena);
    border-color: var(--arena);
}

input[type="date"] {
    color-scheme: dark;
}

input[readonly] {
    background: #303d31;
    color: var(--arena);
    cursor: not-allowed;
}

.grid-formulario {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
}

button, .boton {
    display: inline-block;
    padding: 13px 20px;
    border: 1px solid #78866a;
    border-radius: 5px;
    background: var(--verde-claro);
    color: white;
    text-decoration: none;
    cursor: pointer;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 1px;
    transition: .2s;
}

button:hover, .boton:hover {
    background: #526b4d;
    transform: translateY(-2px);
}

.guardar {
    background: #52633c;
    border-color: var(--arena);
}

.editar {
    background: #52633c;
}

.eliminar {
    background: var(--rojo);
    border-color: #d17a70;
}

.eliminar:hover {
    background: #762b25;
}

.cancelar {
    background: #555d52;
}

/* TABLA */

.tabla-contenedor {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 750px;
}

th {
    background: #131c15;
    color: var(--arena);
    padding: 16px;
    text-align: left;
    font-size: 12px;
    letter-spacing: 1px;
}

td {
    padding: 15px;
    border-bottom: 1px solid #455344;
    color: #e0e5d9;
    font-size: 13px;
}

tr:hover {
    background: #354335;
}

.identificador {
    color: var(--arena);
    font-weight: bold;
}

.acciones {
    display: flex;
    gap: 8px;
    align-items: center;
}

.acciones form {
    margin: 0;
}

.acciones button, .acciones a {
    padding: 9px 12px;
    font-size: 11px;
}

.sin-registros {
    text-align: center;
    color: #aab5a5;
    padding: 30px;
}

/* BUSCADOR */

.busqueda {
    display: flex;
    gap: 10px;
}

.busqueda input {
    flex: 1;
}

.mensaje {
    color: #c6d4b6;
    margin-bottom: 15px;
    font-size: 13px;
}

/* PIE DE PAGINA */

footer {
    background: #101710;
    border-top: 1px solid var(--borde);
    text-align: center;
    padding: 25px;
    color: #9eaa99;
    font-size: 12px;
    letter-spacing: 1px;
}

footer span {
    color: var(--arena);
}

/* RESPONSIVE */

@media(max-width: 700px) {

    .estadisticas {
        grid-template-columns: 1fr;
    }

    .grid-formulario {
        grid-template-columns: 1fr;
    }

    header h1 {
        font-size: 22px;
    }

    .panel {
        padding: 17px;
    }

    .busqueda {
        flex-direction: column;
    }

}

</style>
</head>

<body>

<header>

    <h1>⚔ COMMAND CENTER ⚔</h1>

    <p>SISTEMA DE CONTROL Y REGISTRO DE PERSONAL</p>

    <div class="estado">
        ● SISTEMA OPERATIVO
    </div>

</header>


<div class="contenedor">

    <!-- ESTADISTICAS -->

    <div class="estadisticas">

        <div class="tarjeta">
            <h3>PERSONAS REGISTRADAS</h3>
            <h2>{{ total }}</h2>
        </div>

        <div class="tarjeta">
            <h3>EDAD PROMEDIO</h3>
            <h2>{{ promedio }}</h2>
        </div>

        <div class="tarjeta">
            <h3>REGISTROS COMPLETOS</h3>
            <h2>{{ completos }}</h2>
        </div>

    </div>


    <!-- FORMULARIO -->

    <section class="panel">

        {% if registro_editar %}

            <h2>✎ MODIFICAR REGISTRO</h2>

            <p class="descripcion">
                Actualiza los datos de la persona seleccionada.
            </p>

        {% else %}

            <h2>✚ NUEVO REGISTRO DE PERSONAL</h2>

            <p class="descripcion">
                Introduce los datos solicitados para registrar una persona.
            </p>

        {% endif %}

        <form method="POST"
              action="{% if registro_editar %}{{ url_for('editar', id=registro_editar.id) }}{% else %}{{ url_for('agregar') }}{% endif %}">

            <input type="hidden" name="csrf_token" value="{{ csrf_token }}">

            <div class="grupo">

                <label>NOMBRE COMPLETO</label>

                <input
                    type="text"
                    name="nombre"
                    maxlength="100"
                    placeholder="Nombre y apellidos"
                    value="{{ registro_editar.nombre if registro_editar else '' }}"
                    required
                >

            </div>

            <div class="grid-formulario">

                <div class="grupo">

                    <label>FECHA DE NACIMIENTO</label>

                    <input
                        type="date"
                        id="fecha_nacimiento"
                        name="fecha_nacimiento"
                        max="{{ hoy }}"
                        value="{{ registro_editar.fecha_nacimiento if registro_editar and registro_editar.fecha_nacimiento else '' }}"
                        required
                        onchange="calcularEdad()"
                    >

                </div>

                <div class="grupo">

                    <label>EDAD (AÑOS)</label>

                    <input
                        type="number"
                        id="edad"
                        name="edad"
                        min="0"
                        max="120"
                        placeholder="Edad calculada"
                        value="{{ registro_editar.edad if registro_editar and registro_editar.edad is not none else '' }}"
                        required
                    >

                </div>

            </div>

            <button type="submit" class="guardar">
                {% if registro_editar %}
                    GUARDAR MODIFICACIONES
                {% else %}
                    REGISTRAR PERSONA
                {% endif %}
            </button>

            {% if registro_editar %}

                <a href="{{ url_for('inicio') }}" class="boton cancelar">
                    CANCELAR
                </a>

            {% endif %}

        </form>

    </section>


    <!-- BUSCADOR -->

    <section class="panel">

        <h2>⌕ BUSCAR PERSONAL</h2>

        <form method="GET" action="{{ url_for('inicio') }}" class="busqueda">

            <input
                type="text"
                name="buscar"
                placeholder="Buscar por nombre..."
                value="{{ busqueda }}"
            >

            <button type="submit">BUSCAR</button>

            <a href="{{ url_for('inicio') }}" class="boton cancelar">
                LIMPIAR
            </a>

        </form>

    </section>


    <!-- TABLA DE REGISTROS -->

    <section class="panel">

        <h2>▤ BASE DE DATOS DE PERSONAL</h2>

        <p class="descripcion">
            Información almacenada permanentemente en SQLite.
        </p>

        {% if datos %}

        <div class="tabla-contenedor">

            <table>

                <thead>

                    <tr>
                        <th>ID</th>
                        <th>NOMBRE COMPLETO</th>
                        <th>EDAD</th>
                        <th>FECHA NACIMIENTO</th>
                        <th>ACCIONES</th>
                    </tr>

                </thead>

                <tbody>

                    {% for persona in datos %}

                    <tr>

                        <td class="identificador">
                            #{{ persona.id }}
                        </td>

                        <td>
                            {{ persona.nombre }}
                        </td>

                        <td>
                            {{ persona.edad if persona.edad is not none else 'Pendiente' }}
                        </td>

                        <td>
                            {{ persona.fecha_nacimiento if persona.fecha_nacimiento else 'Pendiente' }}
                        </td>

                        <td>

                            <div class="acciones">

                                <a
                                    href="{{ url_for('editar', id=persona.id) }}"
                                    class="boton editar"
                                >
                                    EDITAR
                                </a>

                                <form
                                    action="{{ url_for('eliminar', id=persona.id) }}"
                                    method="POST"
                                    onsubmit="return confirm('¿Confirmas eliminar este registro?')"
                                >

                                    <input
                                        type="hidden"
                                        name="csrf_token"
                                        value="{{ csrf_token }}"
                                    >

                                    <button type="submit" class="eliminar">
                                        ELIMINAR
                                    </button>

                                </form>

                            </div>

                        </td>

                    </tr>

                    {% endfor %}

                </tbody>

            </table>

        </div>

        {% else %}

            <div class="sin-registros">
                NO SE ENCONTRARON REGISTROS.
            </div>

        {% endif %}

    </section>

</div>


<footer>

    <p>COMMAND CENTER | <span>DATABASE SYSTEM</span></p>

    <p style="margin-top:8px;">
        SISTEMA DE ADMINISTRACIÓN DE INFORMACIÓN
    </p>

</footer>


<script>

// CALCULAR AUTOMATICAMENTE LA EDAD

function calcularEdad() {

    const campoFecha = document.getElementById("fecha_nacimiento");
    const campoEdad = document.getElementById("edad");

    if (!campoFecha.value) {
        campoEdad.value = "";
        return;
    }

    const nacimiento = new Date(campoFecha.value + "T00:00:00");
    const hoy = new Date();

    let edad = hoy.getFullYear() - nacimiento.getFullYear();

    const diferenciaMes = hoy.getMonth() - nacimiento.getMonth();

    if (
        diferenciaMes < 0 ||
        (diferenciaMes === 0 && hoy.getDate() < nacimiento.getDate())
    ) {
        edad--;
    }

    campoEdad.value = edad;

}

// CALCULAR EDAD AL ABRIR EL FORMULARIO

document.addEventListener("DOMContentLoaded", function() {

    const fecha = document.getElementById("fecha_nacimiento");

    if (fecha && fecha.value) {
        calcularEdad();
    }

});

</script>

</body>
</html>
"""


# ==================================================
# VALIDAR DATOS
# ==================================================

def validar_datos():

    nombre = request.form.get("nombre", "").strip()
    fecha_nacimiento = request.form.get("fecha_nacimiento", "").strip()
    edad_texto = request.form.get("edad", "").strip()

    if not nombre or len(nombre) > 100:
        return None, "El nombre debe tener entre 1 y 100 caracteres."

    try:
        nacimiento = date.fromisoformat(fecha_nacimiento)
    except ValueError:
        return None, "La fecha de nacimiento no es válida."

    if nacimiento > date.today():
        return None, "La fecha de nacimiento no puede ser futura."

    edad_calculada = calcular_edad(fecha_nacimiento)

    if edad_calculada > 120:
        return None, "La edad supera el límite permitido de 120 años."

    try:
        edad = int(edad_texto)
    except ValueError:
        return None, "La edad debe ser un número entero."

    if edad != edad_calculada:
        return None, "La edad no coincide con la fecha de nacimiento."

    return {
        "nombre": nombre,
        "edad": edad_calculada,
        "fecha_nacimiento": fecha_nacimiento
    }, None


# ==================================================
# PAGINA PRINCIPAL
# ==================================================

@app.route("/")
def inicio():

    busqueda = request.args.get("buscar", "").strip()

    with conectar() as conexion:

        total = conexion.execute(
            "SELECT COUNT(*) FROM ejemplo"
        ).fetchone()[0]

        if busqueda:

            datos = conexion.execute(
                """
                SELECT * FROM ejemplo
                WHERE nombre LIKE ?
                ORDER BY id DESC
                """,
                (f"%{busqueda}%",)
            ).fetchall()

        else:

            datos = conexion.execute(
                "SELECT * FROM ejemplo ORDER BY id DESC"
            ).fetchall()

        completos = conexion.execute(
            """
            SELECT COUNT(*) FROM ejemplo
            WHERE edad IS NOT NULL
            AND fecha_nacimiento IS NOT NULL
            """
        ).fetchone()[0]

        promedio = conexion.execute(
            "SELECT AVG(edad) FROM ejemplo WHERE edad IS NOT NULL"
        ).fetchone()[0]

    promedio = round(promedio, 1) if promedio is not None else 0

    return render_template_string(
        HTML,
        datos=datos,
        total=total,
        completos=completos,
        promedio=promedio,
        busqueda=busqueda,
        csrf_token=obtener_token(),
        registro_editar=None,
        hoy=date.today().isoformat()
    )


# ==================================================
# AGREGAR PERSONA
# ==================================================

@app.route("/agregar", methods=["POST"])
def agregar():

    datos, error = validar_datos()

    if error:
        return error, 400

    with conectar() as conexion:

        conexion.execute(
            """
            INSERT INTO ejemplo
            (nombre, edad, fecha_nacimiento)
            VALUES (?, ?, ?)
            """,
            (
                datos["nombre"],
                datos["edad"],
                datos["fecha_nacimiento"]
            )
        )

    return redirect(url_for("inicio"))


# ==================================================
# EDITAR PERSONA
# ==================================================

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    with conectar() as conexion:

        persona = conexion.execute(
            "SELECT * FROM ejemplo WHERE id = ?",
            (id,)
        ).fetchone()

        if persona is None:
            abort(404)

        if request.method == "POST":

            datos, error = validar_datos()

            if error:
                return error, 400

            conexion.execute(
                """
                UPDATE ejemplo
                SET nombre = ?,
                    edad = ?,
                    fecha_nacimiento = ?
                WHERE id = ?
                """,
                (
                    datos["nombre"],
                    datos["edad"],
                    datos["fecha_nacimiento"],
                    id
                )
            )

            return redirect(url_for("inicio"))

    return render_template_string(
        HTML,
        datos=[],
        total=0,
        completos=0,
        promedio=0,
        busqueda="",
        csrf_token=obtener_token(),
        registro_editar=persona,
        hoy=date.today().isoformat()
    )


# ==================================================
# ELIMINAR PERSONA
# ==================================================

@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):

    with conectar() as conexion:

        conexion.execute(
            "DELETE FROM ejemplo WHERE id = ?",
            (id,)
        )

    return redirect(url_for("inicio"))


# ==================================================
# PAGINAS DE ERROR
# ==================================================

@app.errorhandler(404)
def error_404(error):
    return "ERROR 404: REGISTRO NO ENCONTRADO.", 404


@app.errorhandler(400)
def error_400(error):
    return "ERROR 400: " + error.description, 400


# ==================================================
# INICIAR SISTEMA
# ==================================================

if __name__ == "__main__":

    crear_tabla()

    print("=" * 50)
    print(" COMMAND CENTER - SISTEMA DE REGISTROS")
    print("=" * 50)
    print(" BASE DE DATOS: prueba.db")
    print(" SERVIDOR: http://127.0.0.1:5000")
    print(" ESTADO: ACTIVO")
    print("=" * 50)

    app.run(debug=True)






