from flask import Flask
import requests
import os

db_url = server = os.environ.get('IPSERVIDOR')

app = Flask(__name__)

@app.route('/SETUP_ALL/',methods=['POST'])
def setuping():
    requests.put('http://admin:admin@%s:5000/tarefas'% db_url)
    json1 = '{"id": "_design/des","key": "_design/des","value": {"rev": "2-ef919c2734435196499689d9112b9599"},"doc": {"_id": "_design/des","_rev": "2-ef919c2734435196499689d9112b9599","views": {"getMaxID": {"reduce": "function (keys, values, rereduce) {\n  if (rereduce) {\n    return max(values);\n  } else {\n    return 0;\n  }\n}","map": "function (doc) {\n  emit(doc._id, 1);\n}"},"get_data": {"map": "function (doc) {\n  emit(doc._id, deb.tarefa, doc.quando);\n}"}},"language": "javascript"}}' 
    requests.put('http://admin:admin@%s:5000/tarefas/_design/des'% db_url,data=json1)

    return "Status : Success\n"


@app.route('/Tarefa/', methods=['GET'])
def get_tarefas():
    
    return requests.get('http://%s:5000/' % (db_url)).json()


@app.route('/Tarefa/', methods=['POST'])
def post_tarefas():
    data = request.form.to_dict(flat=False)
    if(len(dict_main) > 0):
        id_atual = max(dict_main.keys())+1
    else:
        id_atual = 0
    taref = Tarefas(id_atual, data['quando'], data['atividade'])
    dict_main[id_atual] = taref
    return "O id da atividade foi adicionado em %d" % (id_atual)


@app.route('/Tarefa/<int:id>', methods=['GET'])
def lista_especiifca(id):
    return dict_main[id].dicttify()


@app.route('/Tarefa/<int:id>', methods=['DELETE'])
def apaga_especiifca(id):
    del dict_main[id]
    return "Item de Id %d não existe mais" % (id)


@app.route('/Tarefa/<int:id>', methods=['PUT'])
def altera_especiifca(id):
    data = request.form.to_dict(flat=False)

    taref = Tarefas(id, data['quando'], data['atividade'])
    dict_main[id] = taref
    return "A atividade de ID %d  foi alterada" % (id)


@app.route('/healthcheck/', methods=['GET'])
def helath():
    return ""




if __name__ == "__main__":
    app.run(debug=False,host='0.0.0.0',port='5000')
