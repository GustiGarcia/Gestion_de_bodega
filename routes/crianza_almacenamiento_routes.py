import uuid
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from datetime import datetime
from models.crianza_almacenamiento import CrianzaAlmacenamiento
from models.loteVino import LoteVino # Necesitamos importar LoteVino para el dropdown
from models.db import db
from models.estados.estado_crianza import EstadoCrianza
from flask_login import login_required  # ← AGREGAR ESTA IMPORTACIÓN

# Creamos el blueprint para crianza_almacenamiento
crianza_bp = Blueprint('crianza_bp', __name__)

# RUTAS DE API (JSON) - Para Postman
# GET /api/crianza/ - Obtener todas las crianzas/almacenamientos (API)
@crianza_bp.route('/api/', methods=['GET']) # CAMBIO IMPORTANTE AQUÍ
def get_almacenamientos_api(): # Renombrado para diferenciar de la HTML
    almacenamientos = CrianzaAlmacenamiento.query.all()
    resultados = []
    for res in almacenamientos:
        # CORREGIDO: Usar 'nombre_identificativo' en lugar de 'nombre_lote'
        lote_nombre = res.lote_vino.nombre_identificativo if res.lote_vino else "N/A"
        resultados.append({
            'id': res.id,
            'lote_vino_id': res.lote_vino_id,
            'lote_nombre': lote_nombre, # Añadido para la API
            'fecha_inicio': res.fecha_inicio.isoformat(),
            'fecha_fin': res.fecha_fin.isoformat() if res.fecha_fin else None, # Manejar si fecha_fin es None
            'tipo_recipiente': res.tipo_recipiente,
            'volumen_litros': res.volumen_litros,
            'ph_medicion': res.ph_medicion,
            'acidez_medicion_g_l': res.acidez_medicion_g_l,
            'notas': res.notas
        })
    return jsonify(resultados), 200

# GET /api/crianza/<id> - Obtener Crianza/Almacenamiento por ID (API)
@crianza_bp.route('/api/<string:id>', methods=['GET']) # CAMBIO IMPORTANTE AQUÍ
def get_almacenamiento_api(id): # Renombrado para diferenciar de la HTML
    res = CrianzaAlmacenamiento.query.get(id)
    if not res:
        return jsonify({'error': 'Crianza/Almacenamiento no encontrado'}), 404 # Añadido 404
    
    # CORREGIDO: Usar 'nombre_identificativo' en lugar de 'nombre_lote'
    lote_nombre = res.lote_vino.nombre_identificativo if res.lote_vino else "N/A"
    return jsonify({
        'id': res.id,
        'lote_vino_id': res.lote_vino_id,
        'lote_nombre': lote_nombre, # Añadido para la API
        'fecha_inicio': res.fecha_inicio.isoformat(),
        'fecha_fin': res.fecha_fin.isoformat() if res.fecha_fin else None,
        'tipo_recipiente': res.tipo_recipiente,
        'volumen_litros': res.volumen_litros,
        'ph_medicion': res.ph_medicion,
        'acidez_medicion_g_l': res.acidez_medicion_g_l,
        'notas': res.notas
    }), 200

# POST /api/crianza/ - Crear nueva crianza/almacenamiento (API)
@crianza_bp.route('/api/', methods=['POST']) # CAMBIO IMPORTANTE AQUÍ
def crear_almacenamiento_api(): # Renombrado para diferenciar de la HTML
    data = request.get_json()

    # Validaciones para la API (fecha_fin es opcional ahora)
    if not data or "lote_vino_id" not in data or "fecha_inicio" not in data:
        return jsonify({'Error': 'Faltan campos requeridos: lote_vino_id, fecha_inicio'}), 400
    
    # Validar si el lote_vino_id existe
    if not LoteVino.query.get(data['lote_vino_id']):
        return jsonify({'error': 'El lote de vino asociado no existe'}), 400

    try:
        fecha_inicio_dt = datetime.fromisoformat(data['fecha_inicio'])
        # fecha_fin es opcional
        fecha_fin_dt = datetime.fromisoformat(data['fecha_fin']) if 'fecha_fin' in data and data['fecha_fin'] else None
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Usar YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS'}), 400
    
    nuevo_almacenamiento = CrianzaAlmacenamiento(
        lote_vino_id=data['lote_vino_id'],
        fecha_inicio=fecha_inicio_dt,
        fecha_fin=fecha_fin_dt,
        tipo_recipiente=data.get('tipo_recipiente'),
        volumen_litros=data.get('volumen_litros'),
        ph_medicion=data.get('ph_medicion'),
        acidez_medicion_g_l=data.get('acidez_medicion_g_l'),
        notas=data.get('notas')
    )

    db.session.add(nuevo_almacenamiento)
    db.session.commit()

    # CORREGIDO: Usar 'nombre_identificativo' en lugar de 'nombre_lote'
    lote_nombre = nuevo_almacenamiento.lote_vino.nombre_identificativo if nuevo_almacenamiento.lote_vino else "N/A"
    return jsonify({
        'id': nuevo_almacenamiento.id,
        'lote_vino_id': nuevo_almacenamiento.lote_vino_id,
        'lote_nombre': lote_nombre,
        'fecha_inicio': nuevo_almacenamiento.fecha_inicio.isoformat(),
        'fecha_fin': nuevo_almacenamiento.fecha_fin.isoformat() if nuevo_almacenamiento.fecha_fin else None,
        'tipo_recipiente': nuevo_almacenamiento.tipo_recipiente,
        'volumen_litros': nuevo_almacenamiento.volumen_litros,
        'ph_medicion': nuevo_almacenamiento.ph_medicion,
        'acidez_medicion_g_l': nuevo_almacenamiento.acidez_medicion_g_l,
        'notas': nuevo_almacenamiento.notas
    }), 201

# PATCH /api/crianza/<id> - Modificar parcialmente crianza/almacenamiento (API)
@crianza_bp.route('/api/<string:id>', methods=['PATCH']) # CAMBIO IMPORTANTE AQUÍ
def modificar_almacenamiento_api(id): # Renombrado para diferenciar de la HTML
    almacenamiento_cambio = CrianzaAlmacenamiento.query.get(id)
    if not almacenamiento_cambio:
        return jsonify({'error': 'Crianza/Almacenamiento no encontrado'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No hay datos para actualizar'}), 400 # Cambiado el mensaje

    if 'lote_vino_id' in data:
        if not LoteVino.query.get(data['lote_vino_id']):
            return jsonify({'error': 'El nuevo lote de vino asociado no existe'}), 400
        almacenamiento_cambio.lote_vino_id = data['lote_vino_id']

    try:
        if 'fecha_inicio' in data:
            almacenamiento_cambio.fecha_inicio = datetime.fromisoformat(data['fecha_inicio'])
        if 'fecha_fin' in data:
            almacenamiento_cambio.fecha_fin = datetime.fromisoformat(data['fecha_fin']) if data['fecha_fin'] else None
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Usar YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS'}), 400
    
    if 'tipo_recipiente' in data:
        almacenamiento_cambio.tipo_recipiente = data['tipo_recipiente']
    if 'volumen_litros' in data:
        almacenamiento_cambio.volumen_litros = data['volumen_litros']
    if 'ph_medicion' in data:
        almacenamiento_cambio.ph_medicion = data['ph_medicion']
    if 'acidez_medicion_g_l' in data:
        almacenamiento_cambio.acidez_medicion_g_l = data['acidez_medicion_g_l']
    if 'notas' in data:
        almacenamiento_cambio.notas = data['notas']

    db.session.commit()
    # CORREGIDO: Usar 'nombre_identificativo' en lugar de 'nombre_lote'
    lote_nombre = almacenamiento_cambio.lote_vino.nombre_identificativo if almacenamiento_cambio.lote_vino else "N/A"
    return jsonify({
        'id': almacenamiento_cambio.id,
        'lote_vino_id': almacenamiento_cambio.lote_vino_id,
        'lote_nombre': lote_nombre,
        'fecha_inicio': almacenamiento_cambio.fecha_inicio.isoformat(),
        'fecha_fin': almacenamiento_cambio.fecha_fin.isoformat() if almacenamiento_cambio.fecha_fin else None,
        'tipo_recipiente': almacenamiento_cambio.tipo_recipiente,
        'volumen_litros': almacenamiento_cambio.volumen_litros,
        'ph_medicion': almacenamiento_cambio.ph_medicion,
        'acidez_medicion_g_l': almacenamiento_cambio.acidez_medicion_g_l,
        'notas': almacenamiento_cambio.notas
    }), 200

# DELETE /api/crianza/<id> - Eliminar crianza/almacenamiento (API)
@crianza_bp.route('/api/<string:id>', methods=['DELETE']) # CAMBIO IMPORTANTE AQUÍ
def borrar_almacenamiento_api(id):
    almacenamiento = CrianzaAlmacenamiento.query.get(id)
    if not almacenamiento:
        return jsonify({'error': 'Crianza/Almacenamiento no encontrado'}), 404
    
    db.session.delete(almacenamiento)
    db.session.commit()
    return jsonify({'message': 'Crianza/Almacenamiento eliminada exitosamente'}), 200

# RUTAS PARA LA INTERFAZ DE USUARIO (HTML) - Para el navegador web
# URL: /crianza/menu
@crianza_bp.route('/menu', methods=['GET'])
@login_required  # ← AGREGADO
def menu_crianzas():
    return render_template('crianza/menuCrianza.html')

# Ruta para listar todas las crianzas/almacenamientos (HTML)
# URL: /crianza/listar
@crianza_bp.route('/listar', methods=['GET'])
@login_required  # ← AGREGADO
def listar_crianzas_html():
    crianzas = CrianzaAlmacenamiento.query.all()
    estados=list(EstadoCrianza)

    return render_template('crianza/listar_crianzas.html', crianzas=crianzas , estados=estados)

# Ruta para mostrar el formulario de creación de crianza/almacenamiento (GET HTML)
# URL: /crianza/crear
@crianza_bp.route('/crear', methods=['GET'])
@login_required  # ← AGREGADO
def mostrar_formulario_crianza():
    lotes = LoteVino.query.all() # Necesitamos pasar los lotes para el dropdown
    estados=list(EstadoCrianza)
    return render_template('crianza/crear_crianza.html', lotes=lotes , estados=estados)

# Ruta para manejar el envío del formulario de creación de crianza/almacenamiento (POST HTML)
# URL: /crianza/crear
@crianza_bp.route('/crear', methods=['POST'])
@login_required  # ← AGREGADO
def crear_crianza_html():
    estado=request.form['estado']
    estado_enum=EstadoCrianza[estado]

    lote_vino_id = request.form.get('lote_vino_id')
    fecha_inicio_str = request.form.get('fecha_inicio')
    fecha_fin_str = request.form.get('fecha_fin') # Opcional
    tipo_recipiente = request.form.get('tipo_recipiente')
    volumen_litros = request.form.get('volumen_litros')
    ph_medicion = request.form.get('ph_medicion')
    acidez_medicion_g_l = request.form.get('acidez_medicion_g_l')
    notas = request.form.get('notas')

    # Validar campos obligatorios
    if not lote_vino_id or not fecha_inicio_str:
        flash('Los campos Lote Asociado y Fecha de Inicio son obligatorios.', 'danger')
        return redirect(url_for('crianza_bp.mostrar_formulario_crianza'))

    # Convertir a los tipos de datos correctos y manejar errores
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
        fecha_fin_dt = datetime.strptime(fecha_fin_str, '%Y-%m-%d') if fecha_fin_str else None

        volumen_litros_float = float(volumen_litros) if volumen_litros else None
        ph_medicion_float = float(ph_medicion) if ph_medicion else None
        acidez_medicion_g_l_float = float(acidez_medicion_g_l) if acidez_medicion_g_l else None

    except ValueError as e:
        flash(f'Error en el formato de datos: {e}. Asegúrate de ingresar números válidos y un formato de fecha correcto (AAAA-MM-DD).', 'danger')
        return redirect(url_for('crianza_bp.mostrar_formulario_crianza'))
    
    # Verificar si el lote_vino_id existe
    lote_existente = LoteVino.query.get(lote_vino_id)
    if not lote_existente:
        flash('El Lote de Vino seleccionado no existe. Por favor, crea el lote primero.', 'danger')
        return redirect(url_for('crianza_bp.mostrar_formulario_crianza'))

    # Crear la nueva instancia de CrianzaAlmacenamiento
    nueva_crianza = CrianzaAlmacenamiento(
        lote_vino_id=lote_vino_id,
        fecha_inicio=fecha_inicio_dt,
        fecha_fin=fecha_fin_dt,
        tipo_recipiente=tipo_recipiente,
        volumen_litros=volumen_litros_float,
        ph_medicion=ph_medicion_float,
        acidez_medicion_g_l=acidez_medicion_g_l_float,
        notas=notas,

        estado=estado_enum
    )
    
    db.session.add(nueva_crianza)
    db.session.commit()
    flash('Registro de crianza/almacenamiento creado con éxito!', 'success')
    return redirect(url_for('crianza_bp.listar_crianzas_html'))

# Ruta para mostrar y procesar el formulario de edición de crianza/almacenamiento (GET/POST HTML)
# URL: /crianza/editar/<id>
@crianza_bp.route('/editar/<string:id>', methods=['GET', 'POST'])
@login_required  # ← AGREGADO
def editar_crianza_html(id):
    crianza = CrianzaAlmacenamiento.query.get_or_404(id)
    lotes = LoteVino.query.all() # Necesitamos los lotes para el dropdown

    if request.method == 'POST':
        # Obtener datos del formulario (request.form)
        lote_vino_id = request.form.get('lote_vino_id')
        fecha_inicio_str = request.form.get('fecha_inicio')
        fecha_fin_str = request.form.get('fecha_fin')
        tipo_recipiente = request.form.get('tipo_recipiente')
        volumen_litros = request.form.get('volumen_litros')
        ph_medicion = request.form.get('ph_medicion')
        acidez_medicion_g_l = request.form.get('acidez_medicion_g_l')
        notas = request.form.get('notas')

        # Validar campos obligatorios
        if not lote_vino_id or not fecha_inicio_str:
            flash('Los campos Lote Asociado y Fecha de Inicio son obligatorios.', 'danger')
            return redirect(url_for('crianza_bp.editar_crianza_html', id=id))
        
        # Convertir a los tipos de datos correctos y manejar errores
        try:
            estado_str=request.form['estado']
            crianza.estado=EstadoCrianza[estado_str]

            crianza.fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            crianza.fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d') if fecha_fin_str else None

            crianza.volumen_litros = float(volumen_litros) if volumen_litros else None
            crianza.ph_medicion = float(ph_medicion) if ph_medicion else None
            crianza.acidez_medicion_g_l = float(acidez_medicion_g_l) if acidez_medicion_g_l else None

        except ValueError as e:
            flash(f'Error en el formato de datos: {e}. Asegúrate de ingresar números válidos y un formato de fecha correcto (AAAA-MM-DD).', 'danger')
            return redirect(url_for('crianza_bp.editar_crianza_html', id=id))
        
        # Verificar si el lote_vino_id existe
        lote_existente = LoteVino.query.get(lote_vino_id)
        if not lote_existente:
            flash('El Lote de Vino seleccionado no existe.', 'danger')
            return redirect(url_for('crianza_bp.editar_crianza_html', id=id))

        # Asignar los valores actualizados al objeto crianza
        crianza.lote_vino_id = lote_vino_id
        crianza.tipo_recipiente = tipo_recipiente
        crianza.notas = notas

        db.session.commit()
        flash('Registro de crianza/almacenamiento actualizado con éxito!', 'success')
        return redirect(url_for('crianza_bp.listar_crianzas_html'))

    # Si es un GET request, simplemente renderiza el formulario con los datos actuales
    return render_template('crianza/editar_crianza.html', crianza=crianza, lotes=lotes , estados=EstadoCrianza , estado_actual=crianza.estado)

# Ruta para borrar una crianza/almacenamiento (POST HTML)
# URL: /crianza/borrar/<id>
@crianza_bp.route('/borrar/<string:id>', methods=['POST'])
@login_required  # ← AGREGADO
def borrar_crianza_html(id):
    crianza = CrianzaAlmacenamiento.query.get_or_404(id)
    
    db.session.delete(crianza)
    db.session.commit()
    flash('Registro de crianza/almacenamiento eliminado exitosamente!', 'success')
    return redirect(url_for('crianza_bp.listar_crianzas_html'))



# Ruta principal para el blueprint (redirecciona al menú HTML)
@crianza_bp.route('/', methods=['GET'])
@login_required  # ← AGREGADO
def index_crianza():
    return redirect(url_for('crianza_bp.menu_crianzas'))