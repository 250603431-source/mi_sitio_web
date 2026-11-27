
import os
import sqlite3
import secrets
from functools import wraps
from datetime import datetime
from flask import (
    Flask, request, redirect, url_for,
    session, render_template_string, flash
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

DB = "abarrotes_rick.db"
PASSWORD = os.environ.get("STORE_PASSWORD", "QUE ROLLO")


# ---------------- BASE DE DATOS ----------------

def conectar():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def iniciar_db():
    with conectar() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            categoria TEXT DEFAULT 'General'
        );

        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            total REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS detalles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            subtotal REAL NOT NULL
        );
        """)


# ---------------- SEGURIDAD ----------------

def protegido(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("logueado"):
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


@app.before_request
def proteger_formularios():
    if request.method == "POST":
        token = session.get("csrf")
        enviado = request.form.get("csrf")
        if not token or not secrets.compare_digest(token, enviado or ""):
            return "Solicitud no válida. Regresa e inténtalo de nuevo.", 400


@app.context_processor
def variables_globales():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(24)
    return {"csrf": session["csrf"]}


# ---------------- DISEÑO ANIME ----------------

ESTILO = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Rajdhani:wght@400;500;600;700&display=swap');

:root {
 --verde:#00ff9d;
 --morado:#a855f7;
 --rosa:#ff4fd8;
 --fondo:#080812;
 --panel:#111124;
 --texto:#f5f3ff;
}

*{box-sizing:border-box}

body{
 margin:0;
 min-height:100vh;
 color:var(--texto);
 font-family:'Rajdhani',sans-serif;
 font-size:17px;
 background:
 radial-gradient(ellipse at 15% 15%,#35105a88,transparent 35%),
 radial-gradient(ellipse at 85% 80%,#004e4780,transparent 35%),
 linear-gradient(135deg,#070711,#101025 55%,#080812);
 overflow-x:hidden;
}

body:before{
 content:"";
 position:fixed;
 inset:0;
 pointer-events:none;
 opacity:.25;
 background-image:
 radial-gradient(white 1px,transparent 1px),
 radial-gradient(#a855f7 1px,transparent 1px);
 background-size:75px 75px,110px 110px;
 animation:stars 35s linear infinite;
 z-index:-1;
}

@keyframes stars{
 from{background-position:0 0,0 0}
 to{background-position:500px 800px,-400px 600px}
}

header{
 padding:22px 5%;
 display:flex;
 align-items:center;
 justify-content:space-between;
 flex-wrap:wrap;
 gap:15px;
 border-bottom:1px solid #a855f755;
 background:#080812d9;
 backdrop-filter:blur(15px);
}

.logo{
 font-family:'Orbitron',sans-serif;
 font-weight:900;
 font-size:clamp(20px,4vw,32px);
 color:var(--verde);
 text-shadow:0 0 12px var(--verde),0 0 28px #00ff9d77;
}

.logo span{color:var(--rosa)}

nav{display:flex;gap:10px;flex-wrap:wrap}

a{color:inherit;text-decoration:none}

.container{
 width:min(1150px,94%);
 margin:30px auto;
}

.hero{
 position:relative;
 overflow:hidden;
 padding:35px;
 border:1px solid #a855f788;
 border-radius:22px;
 background:linear-gradient(120deg,#17172eec,#25113bec);
 box-shadow:0 0 30px #a855f722,inset 0 0 30px #a855f711;
}

.hero:after{
 content:"✦";
 position:absolute;
 right:35px;
 top:15px;
 font-size:110px;
 color:#00ff9d33;
 animation:float 4s ease-in-out infinite;
}

@keyframes float{
 50%{transform:translateY(-15px) rotate(15deg)}
}

h1,h2,h3{
 font-family:'Orbitron',sans-serif;
}

h1{
 color:var(--verde);
 text-shadow:0 0 15px #00ff9d77;
 font-size:clamp(23px,4vw,36px);
}

h2{font-size:20px;color:var(--rosa)}

.panel{
 background:#111124ed;
 border:1px solid #a855f755;
 border-radius:18px;
 padding:22px;
 margin-top:22px;
 box-shadow:0 8px 30px #0008;
}

.grid{
 display:grid;
 grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
 gap:16px;
 margin-top:20px;
}

.stat{
 padding:20px;
 border-radius:15px;
 background:linear-gradient(145deg,#191932,#10101f);
 border:1px solid #00ff9d66;
 box-shadow:0 0 15px #00ff9d12;
}

.stat strong{
 display:block;
 color:var(--verde);
 font-family:'Orbitron',sans-serif;
 font-size:25px;
 margin-top:8px;
}

button,.btn{
 display:inline-block;
 border:1px solid var(--verde);
 color:#06120e;
 background:linear-gradient(90deg,var(--verde),#75ffd0);
 border-radius:9px;
 padding:11px 17px;
 font-family:'Orbitron',sans-serif;
 font-weight:800;
 font-size:12px;
 cursor:pointer;
 transition:.25s;
 box-shadow:0 0 12px #00ff9d44;
}

button:hover,.btn:hover{
 transform:translateY(-3px);
 box-shadow:0 0 22px #00ff9d99;
}

.btn-purple{
 background:linear-gradient(90deg,#9333ea,#d946ef);
 color:white;
 border-color:#d946ef;
 box-shadow:0 0 15px #a855f755;
}

.btn-red{
 background:linear-gradient(90deg,#be123c,#fb7185);
 color:white;
 border-color:#fb7185;
}

input,select{
 width:100%;
 padding:12px;
 margin:7px 0 15px;
 border:1px solid #a855f788;
 border-radius:9px;
 background:#090918;
 color:white;
 font-family:'Rajdhani',sans-serif;
 font-size:17px;
 outline:none;
}

input:focus,select:focus{
 border-color:var(--verde);
 box-shadow:0 0 12px #00ff9d55;
}

label{color:#d8c8ff;font-weight:700}

table{
 width:100%;
 border-collapse:collapse;
 min-width:600px;
}

th{
 color:var(--verde);
 font-family:'Orbitron',sans-serif;
 font-size:11px;
 text-align:left;
}

td,th{
 padding:13px 10px;
 border-bottom:1px solid #ffffff17;
}

tr:hover{background:#a855f711}

.tabla{overflow-x:auto}

.badge{
 display:inline-block;
 background:#00ff9d1c;
 border:1px solid #00ff9d66;
 color:var(--verde);
 padding:4px 9px;
 border-radius:20px;
 font-size:13px;
}

.flash{
 background:#a855f722;
 border:1px solid var(--morado);
 border-radius:10px;
 padding:12px;
 margin:10px 0;
}

.login{
 width:min(420px,92%);
 margin:9vh auto;
 text-align:center;
}

.login .panel{padding:30px}

footer{
 text-align:center;
 padding:35px;
 color:#aaa;
}

.ticket{
 background:white;
 color:#111;
 padding:25px;
 max-width:420px;
 margin:25px auto;
 border-radius:10px;
 font-family:monospace;
}

.ticket h2{color:#111;text-align:center}

@media(max-width:600px){
 .hero{padding:22px}
 header{justify-content:center;text-align:center}
 nav{justify-content:center}
 .panel{padding:15px}
}

@media print{
 body{background:white;color:black}
 header,nav,.no-print,footer{display:none!important}
 .ticket{box-shadow:none;margin:auto}
}
</style>
"""


# ---------------- PLANTILLAS ----------------

BASE = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ABARROTES RICK | Anime Edition</title>
""" + ESTILO + """
</head>
<body>
<header>
 <a class="logo" href="/">ABARROTES <span>RICK</span> ✦</a>
 {% if session.get('logueado') %}
 <nav>
  <a class="btn" href="/">INICIO</a>
  <a class="btn btn-purple" href="/productos">INVENTARIO</a>
  <a class="btn" href="/vender">VENTAS</a>
  <form method="POST" action="/salir" style="display:inline">
   <input type="hidden" name="csrf" value="{{csrf}}">
   <button class="btn-red">SALIR</button>
  </form>
 </nav>
 {% endif %}
</header>

<main class="container">
 {% with mensajes=get_flashed_messages() %}
 {% for mensaje in mensajes %}
 <div class="flash">{{mensaje}}</div>
 {% endfor %}
 {% endwith %}
 {{contenido|safe}}
</main>

<footer>✦ ABARROTES RICK ✦ ANIME EDITION ✦</footer>
</body>
</html>
"""


def pagina(contenido, **datos):
    # Crear el token antes de mostrar cualquier formulario
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(24)

    html = render_template_string(
        contenido,
        csrf=session["csrf"],
        **datos
    )

    return render_template_string(
        BASE,
        contenido=html,
        csrf=session["csrf"]
    )



# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            session.clear()
            session["logueado"] = True
            session["csrf"] = secrets.token_hex(24)
            flash("¡BIENVENIDO MUCHACHO! ✦ Acceso autorizado.")
            return redirect(url_for("inicio"))
        flash("Contraseña incorrecta.")

    return pagina("""
    <div class="login">
     <div class="panel">
      <div style="font-size:65px">🌌</div>
      <h1>ACCESO RICK</h1>
      <h2>✦ PORTAL INTERGALÁCTICO ✦</h2>
      <p>Identifícate para entrar a la tienda.</p>
      <form method="POST">
       <input type="hidden" name="csrf" value="{{csrf}}">
       <label>CONTRASEÑA DE ACCESO</label>
       <input type="password" name="password" placeholder="Introduce tu contraseña" required>
       <button style="width:100%">ENTRAR AL SISTEMA ✦</button>
      </form>
     </div>
    </div>
    """)


@app.route("/salir", methods=["POST"])
@protegido
def salir():
    session.clear()
    return redirect(url_for("login"))


# ---------------- INICIO ----------------

@app.route("/")
@protegido
def inicio():
    with conectar() as con:
        cantidad = con.execute(
            "SELECT COUNT(*) FROM productos"
        ).fetchone()[0]

        unidades = con.execute(
            "SELECT COALESCE(SUM(stock),0) FROM productos"
        ).fetchone()[0]

        ingresos = con.execute(
            "SELECT COALESCE(SUM(total),0) FROM ventas"
        ).fetchone()[0]

        ventas = con.execute(
            "SELECT COUNT(*) FROM ventas"
        ).fetchone()[0]

        recientes = con.execute(
            "SELECT * FROM productos ORDER BY id DESC LIMIT 5"
        ).fetchall()

    return pagina("""
    <section class="hero">
     <h1>¡BIENVENIDO MUCHACHO! ✦</h1>
     <h2>ABARROTES RICK — ANIME EDITION</h2>
     <p>Tu centro de operaciones está listo. Administra tu inventario y controla tus ventas desde un solo lugar.</p>
     <span class="badge">SISTEMA ONLINE ●</span>
    </section>

    <div class="grid">
     <div class="stat">📦 PRODUCTOS<strong>{{cantidad}}</strong></div>
     <div class="stat">🛒 UNIDADES<strong>{{unidades}}</strong></div>
     <div class="stat">⚡ VENTAS<strong>{{ventas}}</strong></div>
     <div class="stat">💎 INGRESOS<strong>${{"%.2f"|format(ingresos)}}</strong></div>
    </div>

    <section class="panel">
     <h2>✦ CENTRO DE OPERACIONES</h2>
     <div class="grid">
      <a class="btn" href="/productos">📦 ADMINISTRAR INVENTARIO</a>
      <a class="btn btn-purple" href="/agregar">＋ AGREGAR PRODUCTO</a>
      <a class="btn" href="/vender">🛒 REALIZAR VENTA</a>
     </div>
    </section>

    <section class="panel">
     <h2>ÚLTIMOS PRODUCTOS REGISTRADOS</h2>
     <div class="tabla">
     <table>
      <tr><th>PRODUCTO</th><th>PRECIO</th><th>EXISTENCIAS</th></tr>
      {% for p in recientes %}
      <tr>
       <td>{{p.nombre}}</td>
       <td>${{"%.2f"|format(p.precio)}}</td>
       <td>{{p.stock}}</td>
      </tr>
      {% else %}
      <tr><td colspan="3">Todavía no hay productos.</td></tr>
      {% endfor %}
     </table>
     </div>
    </section>
    """, cantidad=cantidad, unidades=unidades,
    ingresos=ingresos, ventas=ventas, recientes=recientes)


# ---------------- INVENTARIO ----------------

@app.route("/productos")
@protegido
def productos():
    busqueda = request.args.get("buscar", "").strip()

    with conectar() as con:
        lista = con.execute("""
            SELECT * FROM productos
            WHERE nombre LIKE ? OR categoria LIKE ?
            ORDER BY nombre
        """, (f"%{busqueda}%", f"%{busqueda}%")).fetchall()

    return pagina("""
    <section class="hero">
     <h1>INVENTARIO ✦</h1>
     <p>Administra todos los productos de tu tienda.</p>
    </section>

    <section class="panel">
     <form method="GET">
      <label>BUSCAR PRODUCTO</label>
      <input name="buscar" value="{{buscar}}" placeholder="Nombre o categoría...">
      <button>BUSCAR</button>
      <a href="/productos" class="btn btn-purple">VER TODOS</a>
     </form>
     <a href="/agregar" class="btn">＋ NUEVO PRODUCTO</a>
    </section>

    <section class="panel">
     <div class="tabla">
     <table>
      <tr><th>PRODUCTO</th><th>CATEGORÍA</th><th>PRECIO</th><th>STOCK</th><th>ACCIONES</th></tr>
      {% for p in lista %}
      <tr>
       <td>{{p.nombre}}</td>
       <td>{{p.categoria}}</td>
       <td>${{"%.2f"|format(p.precio)}}</td>
       <td><span class="badge">{{p.stock}}</span></td>
       <td>
        <a class="btn btn-purple" href="/editar/{{p.id}}">EDITAR</a>
        <form method="POST" action="/eliminar/{{p.id}}" style="display:inline" onsubmit="return confirm('¿Eliminar este producto?')">
         <input type="hidden" name="csrf" value="{{csrf}}">
         <button class="btn-red">BORRAR</button>
        </form>
       </td>
      </tr>
      {% else %}
      <tr><td colspan="5">No se encontraron productos.</td></tr>
      {% endfor %}
     </table>
     </div>
    </section>
    """, lista=lista, buscar=busqueda)


# ---------------- AGREGAR PRODUCTO ----------------

@app.route("/agregar", methods=["GET", "POST"])
@protegido
def agregar():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        categoria = request.form.get("categoria", "General").strip()
        try:
            precio = float(request.form.get("precio", ""))
            stock = int(request.form.get("stock", ""))
            if not nombre or precio < 0 or stock < 0:
                raise ValueError()
        except ValueError:
            flash("Revisa los datos: precio y existencias deben ser válidos.")
            return redirect(url_for("agregar"))

        with conectar() as con:
            con.execute("""
                INSERT INTO productos(nombre,precio,stock,categoria)
                VALUES(?,?,?,?)
            """, (nombre, precio, stock, categoria or "General"))

        flash("¡Producto agregado correctamente! ✦")
        return redirect(url_for("productos"))

    return pagina("""
    <section class="hero"><h1>NUEVO PRODUCTO ✦</h1><p>Registra un nuevo artículo en tu inventario.</p></section>
    <section class="panel">
     <form method="POST">
      <input type="hidden" name="csrf" value="{{csrf}}">
      <label>NOMBRE DEL PRODUCTO</label>
      <input name="nombre" placeholder="Ej. Refresco" required>
      <label>CATEGORÍA</label>
      <input name="categoria" placeholder="Ej. Bebidas">
      <label>PRECIO</label>
      <input type="number" name="precio" step="0.01" min="0" required>
      <label>EXISTENCIAS</label>
      <input type="number" name="stock" min="0" required>
      <button>GUARDAR PRODUCTO ✦</button>
      <a class="btn btn-purple" href="/productos">CANCELAR</a>
     </form>
    </section>
    """)


# ---------------- EDITAR PRODUCTO ----------------

@app.route("/editar/<int:id>", methods=["GET", "POST"])
@protegido
def editar(id):
    with conectar() as con:
        producto = con.execute(
            "SELECT * FROM productos WHERE id=?", (id,)
        ).fetchone()

    if not producto:
        flash("Producto no encontrado.")
        return redirect(url_for("productos"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        categoria = request.form.get("categoria", "General").strip()

        try:
            precio = float(request.form.get("precio", ""))
            stock = int(request.form.get("stock", ""))
            if not nombre or precio < 0 or stock < 0:
                raise ValueError()
        except ValueError:
            flash("Datos incorrectos.")
            return redirect(url_for("editar", id=id))

        with conectar() as con:
            con.execute("""
                UPDATE productos
                SET nombre=?,categoria=?,precio=?,stock=?
                WHERE id=?
            """, (nombre, categoria, precio, stock, id))

        flash("Producto actualizado.")
        return redirect(url_for("productos"))

    return pagina("""
    <section class="hero"><h1>EDITAR PRODUCTO ✦</h1></section>
    <section class="panel">
     <form method="POST">
      <input type="hidden" name="csrf" value="{{csrf}}">
      <label>NOMBRE</label>
      <input name="nombre" value="{{p.nombre}}" required>
      <label>CATEGORÍA</label>
      <input name="categoria" value="{{p.categoria}}">
      <label>PRECIO</label>
      <input type="number" name="precio" step="0.01" min="0" value="{{p.precio}}" required>
      <label>EXISTENCIAS</label>
      <input type="number" name="stock" min="0" value="{{p.stock}}" required>
      <button>GUARDAR CAMBIOS</button>
      <a class="btn btn-purple" href="/productos">VOLVER</a>
     </form>
    </section>
    """, p=producto)


# ---------------- ELIMINAR PRODUCTO ----------------

@app.route("/eliminar/<int:id>", methods=["POST"])
@protegido
def eliminar(id):
    with conectar() as con:
        con.execute("DELETE FROM productos WHERE id=?", (id,))
    flash("Producto eliminado.")
    return redirect(url_for("productos"))


# ---------------- VENTAS ----------------

@app.route("/vender", methods=["GET", "POST"])
@protegido
def vender():
    if request.method == "POST":
        cantidades = {}
        try:
            for clave, valor in request.form.items():
                if clave.startswith("cantidad_") and valor.strip():
                    cantidad = int(valor)
                    if cantidad < 0:
                        raise ValueError()
                    if cantidad > 0:
                        cantidades[int(clave.split("_")[1])] = cantidad
        except ValueError:
            flash("Cantidad no válida.")
            return redirect(url_for("vender"))

        if not cantidades:
            flash("Selecciona al menos un producto.")
            return redirect(url_for("vender"))

        try:
            with conectar() as con:
                con.execute("BEGIN IMMEDIATE")
                total = 0
                articulos = []

                for producto_id, cantidad in cantidades.items():
                    p = con.execute(
                        "SELECT * FROM productos WHERE id=?",
                        (producto_id,)
                    ).fetchone()

                    if not p or p["stock"] < cantidad:
                        raise ValueError("Existencias insuficientes para " +
                                         (p["nombre"] if p else "un producto"))

                    subtotal = round(p["precio"] * cantidad, 2)
                    total += subtotal
                    articulos.append((p, cantidad, subtotal))

                cursor = con.execute(
                    "INSERT INTO ventas(fecha,total) VALUES(?,?)",
                    (datetime.now().strftime("%d/%m/%Y %H:%M"), round(total, 2))
                )
                venta_id = cursor.lastrowid

                for p, cantidad, subtotal in articulos:
                    con.execute(
                        "UPDATE productos SET stock=stock-? WHERE id=?",
                        (cantidad, p["id"])
                    )
                    con.execute("""
                        INSERT INTO detalles
                        (venta_id,producto_id,nombre,cantidad,precio,subtotal)
                        VALUES(?,?,?,?,?,?)
                    """, (venta_id, p["id"], p["nombre"],
                          cantidad, p["precio"], subtotal))

        except ValueError as e:
            flash(str(e))
            return redirect(url_for("vender"))

        return redirect(url_for("ticket", venta_id=venta_id))

    with conectar() as con:
        lista = con.execute(
            "SELECT * FROM productos WHERE stock>0 ORDER BY nombre"
        ).fetchall()

    return pagina("""
    <section class="hero">
     <h1>NUEVA VENTA ✦</h1>
     <p>Selecciona los productos y las cantidades.</p>
    </section>

    <section class="panel">
     <form method="POST">
      <input type="hidden" name="csrf" value="{{csrf}}">
      <div class="tabla">
      <table>
       <tr><th>PRODUCTO</th><th>PRECIO</th><th>DISPONIBLES</th><th>CANTIDAD</th></tr>
       {% for p in lista %}
       <tr>
        <td>{{p.nombre}}</td>
        <td>${{"%.2f"|format(p.precio)}}</td>
        <td>{{p.stock}}</td>
        <td><input type="number" name="cantidad_{{p.id}}" min="0" max="{{p.stock}}" value="0"></td>
       </tr>
       {% else %}
       <tr><td colspan="4">No hay productos disponibles.</td></tr>
       {% endfor %}
      </table>
      </div>
      <br>
      <button>CONFIRMAR VENTA ✦</button>
     </form>
    </section>
    """, lista=lista)


# ---------------- TICKET ----------------

@app.route("/ticket/<int:venta_id>")
@protegido
def ticket(venta_id):
    with conectar() as con:
        venta = con.execute(
            "SELECT * FROM ventas WHERE id=?", (venta_id,)
        ).fetchone()

        detalles = con.execute(
            "SELECT * FROM detalles WHERE venta_id=?", (venta_id,)
        ).fetchall()

    if not venta:
        return redirect(url_for("inicio"))

    return pagina("""
    <section class="ticket">
     <h2>✦ ABARROTES RICK ✦</h2>
     <center>COMPROBANTE DE VENTA</center>
     <hr>
     <p>Folio: #{{venta.id}}</p>
     <p>Fecha: {{venta.fecha}}</p>
     <hr>
     {% for d in detalles %}
     <p>{{d.nombre}}</p>
     <p>{{d.cantidad}} x ${{"%.2f"|format(d.precio)}} = ${{"%.2f"|format(d.subtotal)}}</p>
     {% endfor %}
     <hr>
     <h2>TOTAL: ${{"%.2f"|format(venta.total)}}</h2>
     <center>¡GRACIAS POR TU COMPRA!</center>
    </section>
    <div class="no-print" style="text-align:center">
     <button onclick="window.print()">IMPRIMIR TICKET</button>
     <a class="btn btn-purple" href="/">VOLVER AL INICIO</a>
    </div>
    """, venta=venta, detalles=detalles)


# ---------------- ERRORES ----------------

@app.errorhandler(404)
def no_encontrado(e):
    return pagina("""
    <section class="hero">
     <h1>404 ✦</h1>
     <p>Esta zona del universo no existe.</p>
     <a class="btn" href="/">VOLVER AL INICIO</a>
    </section>
    """), 404


# ---------------- EJECUTAR ----------------

if __name__ == "__main__":
    iniciar_db()
    print("ABARROTES RICK ANIME EDITION")
    print("Abre http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
