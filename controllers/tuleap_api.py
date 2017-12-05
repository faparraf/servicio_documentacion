import json
import requests
import pprint

def autenticar_tuleap(parametros):
    request_headers = {"Content-type" : "application/json"}
    request_data = {"username" : parametros["username"], "password" : parametros["password"]}
    request_url = parametros["url_base_tuleap"]+"tokens"
    request = requests.post(url=request_url, json=request_data, headers=request_headers)
    user_data = request.json()
    # pprint.pprint(user_data)
    return user_data

def get_membership_tuleap(parametros):
    request_headers = {"Content-type" : "application/json",
    "X-Auth-Token":str(parametros["user_data"]["token"]),
    "X-Auth-UserId":str(parametros["user_data"]["user_id"])}
    request_url = parametros["url_base_tuleap"]+"users/"+str(parametros["user_data"]["user_id"])+"/membership?limit=-1"
    request = requests.get(url=request_url, headers=request_headers)
    membership = request.json()
    # pprint.pprint(membership)
    return membership

def get_trackers_tuleap(parametros, project_id):
    request_headers = {"Content-type" : "application/json",
    "X-Auth-Token":str(parametros["user_data"]["token"]),
    "X-Auth-UserId":str(parametros["user_data"]["user_id"])}
    request_url = parametros["url_base_tuleap"]+"projects/"+str(project_id)+"/trackers?limit=-1"
    # requests_params = {"shortname":project_shortname}
    request = requests.get(url=request_url, headers=request_headers)
    project_trackers = request.json()
    # pprint.pprint(project_trackers)
    return project_trackers

def get_tracker_info_tuleap(parametros, tracker_id):
    request_headers = {"Content-type" : "application/json",
    "X-Auth-Token":str(parametros["user_data"]["token"]),
    "X-Auth-UserId":str(parametros["user_data"]["user_id"])}
    request_url = parametros["url_base_tuleap"]+"trackers/"+str(tracker_id)+""
    # requests_params = {"shortname":project_shortname}
    request = requests.get(url=request_url, headers=request_headers)
    tracker_info = request.json()
    # pprint.pprint(tracker_info)
    return tracker_info

def get_artifact_info_tuleap(parametros, artifact_id):
    request_headers = {"Content-type" : "application/json",
    "X-Auth-Token":str(parametros["user_data"]["token"]),
    "X-Auth-UserId":str(parametros["user_data"]["user_id"])}
    request_url = parametros["url_base_tuleap"]+"artifacts/"+str(artifact_id)+""
    # requests_params = {"shortname":project_shortname}
    request = requests.get(url=request_url, headers=request_headers)
    artifact_info = request.json()
    # pprint.pprint(artifact_info)
    return artifact_info

def get_tracker_artifacts(parametros, tracker_id):
    request_headers = {"Content-type" : "application/json",
    "X-Auth-Token":str(parametros["user_data"]["token"]),
    "X-Auth-UserId":str(parametros["user_data"]["user_id"])}
    request_url = parametros["url_base_tuleap"]+"trackers/"+str(tracker_id)+"/artifacts?limit=1000&order=desc"
    if "query" in parametros:
        requests_params = {"query":json.dumps(parametros["query"])}
    else:
        requests_params = {}
    #requests_params = {"query":json.dumps({"artifact_id":"14919"})}
    #requests_params = {"query":build_query_object(parametros["query"], tracker_id)}
    request = requests.get(url=request_url, headers=request_headers, params=requests_params)
    #print("Peticion " + request.url)
    tracker_artifacts = request.json()
    # pprint.pprint(tracker_artifacts)
    return tracker_artifacts

def build_query_object(query, tracker_id):
    tracker_info = get_tracker_info_tuleap(parametros, str(tracker_id))
    query_object = {}
    for field in tracker_info["fields"]:
        if field["name"] in query:
            query_object[field["field_id"]] = query[field["name"]]
    # pprint.pprint(tracker_artifacts)
    return query_object

def get_project_info_tuleap(parametros, project_shortname):
    request_headers = {"Content-type" : "application/json",
    "X-Auth-Token":str(parametros["user_data"]["token"]),
    "X-Auth-UserId":str(parametros["user_data"]["user_id"])}
    request_url = parametros["url_base_tuleap"]+"projects?query=%7B%22shortname%22%3A%22"+str(project_shortname)+"%22%7D"
    # requests_params = {"shortname":project_shortname}
    request = requests.get(url=request_url, headers=request_headers)
    project_info = request.json()
    # pprint.pprint(project_info)
    return project_info

def send_comment_tuleap(parametros, comentario, artifact_id):
    payload = {}
    payload["comment"]={}
    payload["comment"]["format"] = "text"
    payload["comment"]["body"] = comentario
    payload["values"] = []
    #pprint.pprint(payload)
    request_headers = {"Content-type" : "application/json",
    "X-Auth-Token":str(parametros["user_data"]["token"]),
    "X-Auth-UserId":str(parametros["user_data"]["user_id"])}
    request_url = parametros["url_base_tuleap"]+"artifacts/"+str(artifact_id)
    request = requests.put(url=request_url, headers=request_headers, json=payload)
    # pprint.pprint(request.json())
    return request.status_code
