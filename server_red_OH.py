from flask import Flask
import requests




app = Flask(__name__)


@app.route('/Tarefa/', methods=['GET'])
def get_tarefas():
    
    return requests.get('').json()


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

