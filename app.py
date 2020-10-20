#!flask/bin/python
from flask import Flask, jsonify, render_template, request
from celery import Celery
import glob
import json
import re
import copy
import subprocess

app = Flask(__name__)
celery = Celery(app.name, backend='rpc://', broker='pyamqp://worker:fnurkgurk@tweet-analyzr.local:5672/twhost')

mesh_files = "data/*"

result_data = {} 
results = []

num_tasks = 0

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route("/run", methods=['POST'])
def run():
    global results
    global num_tasks

    result_data['total_files'] = 0
    result_data['proggress'] = 0

    files = glob.glob(mesh_files)
    num_tasks = len(files)

    with app.app_context():

        for filepath in files:
            results.append(process_file.delay(filepath))

    return ('', 204)

@app.route("/stop", methods=["POST"])
def stop():
    global results
    for result in results:
        result.revoke()

    results = []

    return ('', 204)

@app.route('/data', methods=['GET'])
def get_result_data():
    global results
    global num_tasks

    for result in results:
        if result.ready():
		dir = result.get()
		lift_res = os.popen(['cat',dir).readlines()
    result_data['proggress'] = (1 - len(results)/num_tasks)*100
    return jsonify(result_data)

@celery.task
def process_file(angle):
    cmd = "./airfoil 2 0.01 10. 1 " + angle + " 20 0"
    subp = subprocess.run(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8")
    if subp.returncode == 0:
        return "./murtazo/navier_stokes_solver/results/r0a" + angle + "n200.m"
    else:
        return -1


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80 ,debug=True)

