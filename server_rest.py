from flask import Flask, request,redirect
import requests
import os

db_url = server = os.environ.get('IPSERVIDOR')

app = Flask(__name__)


@app.route('/Tarefa/', methods=['GET'])
def get_tarefas():
    return requests.get('http://%s:5000/Tarefa/' % (db_url)).json()


@app.route('/Tarefa/', methods=['POST'])
def post_tarefas():
    dados_a_serem_salvos = request.form.to_dict(flat=False)
    resp = requests.post('http://%s:5000/Tarefa/' % (db_url), json=dados_a_serem_salvos)
    return resp.json()
    


@app.route('/Tarefa/<int:id>', methods=['GET'])
def lista_especiifca(id):
    resp = requests.get('http://%s:5000/Tarefa/%s' % (db_url,id)).json()
    return resp
    


@app.route('/Tarefa/<int:id>', methods=['DELETE'])
def apaga_especiifca(id):
    rev = requests.delete('http://%s:5000/Tarefa/%s' % (db_url,id)).json()
    return resp.json()


@app.route('/Tarefa/<int:id>', methods=['PUT'])
def altera_especiifca(id):
    data = request.form.to_dict(flat=False)
    esp = requests.put('http://%s:5000/Tarefa/%s' % (db_url, id), data=data1)
    return resp.json()


@app.route('/healthcheck/', methods=['GET'])
def helath():
    return ""

@app.route('/')
def aaa():
    return requests.get('http://%s:5000/' % (db_url)).json()


if __name__ == "__main__":
    app.run(debug=False,host='0.0.0.0',port='5000')
