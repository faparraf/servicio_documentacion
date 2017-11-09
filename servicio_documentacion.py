from flask import Flask, render_template, request, jsonify, make_response
from controllers import documento_pago, numero_a_letras, appconf
from flask_api import status
import pprint
import sys
import requests
import json
import pdfkit
import glob, os
import logging

# Definicion de rutas estaticas
ruta_archivos				= "/srv/http/documentos_mensuales/"
host_archivos				= "http://127.0.0.1/documentos_mensuales/"
ruta_assets					= "assets/"
ruta_servicios				= "http://127.0.0.1:5000/"
prefijo_cumplido			= "cumplido/"
prefijo_informe_gestion		= "informe_gestion/"
template_cumplido			= "cumplido/template_cumplido.html"
template_informe_gestion	= "informe_gestion/template_informe_gestion.html"

# create logger
logger = logging.getLogger('Logger App')
level = logging.DEBUG
logger.setLevel(level)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(level)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

#Creacion del app con flask
app = Flask(__name__)

#Inclusion de la funcion numero_a_letras con alias de valor_letras
app.jinja_env.globals.update(valor_letras=numero_a_letras.numero_a_letras)

#Obtencion de los parametros pasados al script de python
parametrosBase = appconf.parametros

@app.route('/documento_mensual/informe_gestion', methods=['POST'])
def generar_informe_gestion():
	print("Entra a servicio")
	"""
	Funcion para generar el informe de gestion de forma masiva, método POST
	recibe nombre de usuario y contraseña, ademas de query_filter
	Returns:
		200 si es exitoso, 404 de lo contrario.
	"""
	try:
		#Obtencion del body de la peticion
		parametros_body = request.get_json(force = True)
		logger.info("Body recuperado")
		logger.debug(pprint.pformat(parametros_body))
		parametros = parametros_body
		logger.debug("Parametros:")
		logger.debug(pprint.pformat(parametros))

		#Obtencion de las actividades filtradas con el query filter
		actividades = documento_pago.obtener_artefactos(parametros)
		logger.debug("Actividades:")
		#logger.debug(pprint.pformat(actividades))

	except Exception as inst:
		#Error en la generacion de las actividades
		logger.error("Error en obtencion de body")
		actividades = None
		pprint.pprint(inst)

	if actividades:
		logger.info("Actividades enviadas")
		#return jsonify(actividades)
		identificacion = parametros["identificacion"]
		#Obtencion de la informacion del contratista por medio de los servicios expuestos
		usuario_data = datos_contratista("1030577784")
		informe_data = datos_informe()

		logger.info("Plantilla de gestion renderizada")
		
		fname = ruta_archivos+prefijo_informe_gestion+informe_data["informe"]["vigencia"]+"/"+informe_data["informe"]["mes"]+"/"+str(identificacion)+".html"

		# Escritura sobre el archivo
		with open(fname, 'w') as f:
			html = render_template(template_informe_gestion, usuario=usuario_data, tamano_actividades=len(actividades), actividades=actividades, jefe=informe_data["jefe"], informe=informe_data["informe"])
			f.write(html)
		# Retorno de la plantilla renderizada con los datos proveidos
		return "Generación exitosa", status.HTTP_200_OK
		
	logger.error("Plantilla de gestion no renderizada")
	return "No generado", status.HTTP_404_NOT_FOUND

@app.route('/documento_mensual/cumplido', methods=['GET'])
def generar_cumplido_masivo():
	"""
	Funcion para generar los cumplidos de todos los contratistas registrados en la base de datos de la oficina
	Returns:
		200 si es exitoso, 406 de lo contrario.
	"""
	try:
		# Obtencion de los datos almacenados de contratistas a quienes se les generara el informe
		with open('datos_temp/base_datos_oas.json') as data_file:
			data = json.load(data_file)
		
		# Iteracion de los contratistas
		for contratista in data["contratistas"]:
			logger.debug(pprint.pformat(contratista))
			# Generacion individual de el cumplido
			generar_cumplido_individual(contratista["id"])

		return "Generación exitosa", status.HTTP_200_OK
	except:
		return "Error", HTTP_406_NOT_ACCEPTABLE

@app.route('/documento_mensual/cumplido/<string:identificacion>', methods=['GET'])
def generar_cumplido_individual(identificacion):
	"""
	Funcion para generar el cumplido de un solo contratista
	Args:
		identificacion: numero .

        Returns:
            200 si es exitoso, 406 de lo contrario.
	"""
	try:
		logger.info("Cumplido Individual de "+identificacion)
		
		# Obtencion de datos de contratista y de informe
		usuario_data = datos_contratista(identificacion)
		informe_data = datos_informe()
		logger.debug("Informe data:")
		logger.debug(pprint.pformat(informe_data))

		# Ruta del archivo que se guardara
		fname = ruta_archivos+prefijo_cumplido+informe_data["informe"]["vigencia"]+"/"+informe_data["informe"]["mes"]+"/"+str(identificacion)+".html"
		
		logger.debug("Ruta: "+fname)
		
		# Escritura sobre el archivo
		with open(fname, 'w') as f:
			html = render_template(template_cumplido, usuario=usuario_data, jefe=informe_data["jefe"], informe=informe_data["informe"])
			f.write(html)

		return "Generación exitosa", status.HTTP_200_OK
	except:
		return "Error", HTTP_406_NOT_ACCEPTABLE

@app.route('/datos_informe', methods=['GET'])
def get_datos_informe():
	"""
	Funcion para obtener los datos del informe actual
	Return:
		Datos del informe en formato JSON
	"""
	return jsonify(datos_informe())


@app.route('/datos_contratista/<string:identificacion>', methods=['GET'])
def get_datos_contratista(identificacion):
	"""
	Funcion para obtener los datos del contratista con base a su identificacion
	Return:
		Datos del contratista en formato JSON en el caso existoso, un JSON vacio de lo contrario.
	"""
	try:
		return jsonify(datos_contratista(identificacion))
	except:
		return jsonify({})

@app.route('/documento_mensual/cumplido_pdf', methods=['POST'])
def get_html_to_pdf_masivo():
	"""
	"""
	parametros = None
	try:
		parametros = request.get_json(force = True)
		#pprint.pprint(parametros)
	except:
		print()
	if parametros:
		html_to_pdf_masivo(ruta_archivos+parametros["tipo"]+"/"+parametros["vigencia"]+"/"+parametros["mes"]+"")
		return "Generación exitosa", status.HTTP_200_OK 

def html_to_pdf_masivo(ruta):
	os.chdir(ruta)
	for file in glob.glob("*.html"):
		html_to_pdf(os.path.join(ruta,file),os.path.join(ruta,"pdf",file+".pdf"))


def html_to_pdf(path_html, path_pdf, options = None):
	if not options:
		options = {
		'page-size': 'Letter',
		'encoding': "UTF-8",
		'no-outline': None,
		'orientation': 'Landscape'
		}
	print("Ruta "+path_html)
	print("PDF  "+path_pdf)
	pdfkit.from_file(path_html, path_pdf, options=options)

def datos_informe():
	informe_data = {}
	informe_data["dia_inicial"]="01"
	informe_data["dia_final"]="30"
	informe_data["mes"]="noviembre"
	informe_data["vigencia"]="2017"
	informe_data["dia_informe"]=30

	jefe_data={}
	jefe_data["nombre_completo"]="Beatriz Jaramillo"
	jefe_data["cargo"]="Jefe Asesora de Sistemas"
	print("Datos informe")
	return {"informe":informe_data,"jefe":jefe_data}

def datos_contratista(identificacion):
	print("Datos contratista "+identificacion)
	with open('datos_temp/base_datos_contratista.json') as data_file:    
		data = json.load(data_file)
	
	try:
		return data[identificacion]
	except:
		return {}

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, port=int(parametrosBase["appport"]))
