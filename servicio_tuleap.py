from flask import Flask, request, jsonify
from flask_api import status
from flask_restful import Resource, Api
from controllers import tuleap_api, comment_tuleap_from_github
from controllers import text_tool, appconf
import re
app = Flask(__name__)
api = Api(app)

todos = {}
parametros = appconf.parametros
class TuleapService(Resource):
    def post(self):
        print(parametros)
        parametros["user_data"] = tuleap_api.autenticar_tuleap(parametros)
        hookGitData = request.get_json(force = True) 
        
        for commitInfo in hookGitData["commits"]:
            try:
                comment = text_tool.format_comment_by_expr(commitInfo["message"].encode("utf-8"), '#(.+?)# ', '',commitInfo)
                if comment["artifact_id"]:
                    artifact_id = comment["artifact_id"]
                    print 'Artifact # --'+ str(artifact_id)+'--'
                    print "Status "+str(tuleap_api.send_comment_tuleap(parametros, str(comment["message"]), str(artifact_id)))
                else:
                    print "No hay Artifact asociado"
            except Exception as inst:
                print "No hay Artifact asociado error inesperado"
                print inst
             
        return hookGitData["commits"]

    def get(self):
        return "Servicio activo", status.HTTP_200_OK

api.add_resource(TuleapService, '/tuleap_service')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True ,port=int(parametros["appport"]))
