from flask import Flask, request
import requests
import os

db_url = server = os.environ.get('IPSERVIDOR')

app = Flask(__name__)

@app.route('/SETUP_ALL/',methods=['POST'])
def setuping():
    response = requests.put('http://admin:admin@%s:5000/tarefas'% db_url)
    print(response)
    json1 = '{"id": "_design/des","key": "_design/des","value": {"rev": "2-ef919c2734435196499689d9112b9599"},"doc": {"_id": "_design/des","_rev": "2-ef919c2734435196499689d9112b9599","views": {"getMaxID": {"reduce": "function (keys, values, rereduce) {\n  if (rereduce) {\n    return max(values);\n  } else {\n    return 0;\n  }\n}","map": "function (doc) {\n  emit(doc._id, 1);\n}"},"get_data": {"map": "function (doc) {\n  emit(doc._id, deb.tarefa, doc.quando);\n}"}},"language": "javascript"}}' 
    response = requests.put('http://admin:admin@%s:5000/tarefas/_design/des'% db_url,json=json1)
    print(response)
    return "Status : Success\n"


@app.route('/Tarefa/', methods=['GET'])
def get_tarefas():
    return requests.get('http://%s:5000/tarefas/_design/des/_views/get_data' % (db_url)).json()


@app.route('/Tarefa/', methods=['POST'])
def post_tarefas():
    dados_a_serem_salvos = request.form.to_dict(flat=False)
    uuid = requests.get('http://%s:5000/_uuids' % (db_url)).json()['uuids'][0]
    resp = requests.put('http://admin:admin@%s:5000/tarefas/_design/des/%s' % (db_url, uuid), data=dados_a_serem_salvos)
    return resp.json()
    


@app.route('/Tarefa/<int:id>', methods=['GET'])
def lista_especiifca(id):
    resp = requests.get('http://%s:5000/tarefas/_design/des/_views/get_data/%s' % (db_url,id)).json()
    return resp
    


@app.route('/Tarefa/<int:id>', methods=['DELETE'])
def apaga_especiifca(id):
    rev = requests.get('http://%s:5000/tarefas/_design/des/_views/get_data/%s' % (db_url,id)).json()['_rev']
    resp = requests.delete('http://admin:admin@%s:5000/tarefas/%s?rev=%s' % (db_url,id,rev))
    return resp.json()


@app.route('/Tarefa/<int:id>', methods=['PUT'])
def altera_especiifca(id):
    data = request.form.to_dict(flat=False)
    rev = requests.get('http://%s:5000/tarefas/_design/des/_views/get_data/%s' % (db_url,id)).json()['_rev']
    data1 = '{"quando":"%s","tarefa":"%s","_rev":"%s"}' % (data['quando'],data['tarefa'],rev)
    resp = requests.put('http://%s:5000/tarefas/_design/des/%s' % (db_url, id), data=data1)
    return resp.json()


@app.route('/healthcheck/', methods=['GET'])
def helath():
    return "Oi\n"




if __name__ == "__main__":
    app.run(debug=False,host='0.0.0.0',port='5000')
