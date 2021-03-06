#!flask/bin/python
from flask import Flask, jsonify, render_template, request, send_from_directory
from celery import Celery
import glob
import json
import re
import copy
import math
import os
import subprocess

app = Flask(__name__)
celery = Celery(app.name, backend='rpc://', broker='pyamqp://worker:fnurkgurk@g2-airfoil-main.local:5672/twhost')

mesh_files = "data/*"
results_path = 'data/'

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

    # Initialize result data
    result_data['proggress'] = 0
    result_data['files'] = []
    result_data['total_jobs'] = 0

    # Get parameters
    min_angle = int(request.form['min_angle'])
    max_angle = int(request.form['max_angle'])
    num_angles = int(request.form['num_angles'])

    num_tasks = num_angles

    with app.app_context():

        # Push all angles to the queue

        # Calculate angle step
        angle_step = (max_angle - min_angle) / (num_angles-1)

        angle = min_angle
        for n in range(num_angles):
            results.append(process_file.delay(int(angle)))
            angle += angle_step
    # TODO run webhooks to scale out

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
            # TODO process results and append to result_data
            res_dir = result.get()
            #if res_dir:
            result_data['files'].append(res_dir)
            #filename = res_dir.split('/')[-1]
            results.remove(result)
            result_data['total_jobs'] += 1

            # TODO run webhooks to scale in

    result_data['proggress'] = (1 - len(results)/num_tasks)*100
    return jsonify(result_data)

# Serve result files
@app.route('/files/<path:filename>', methods=['GET'])
def get_file(filename):
    return send_from_directory(results_path, filename, as_attachment=True)

@celery.task
def process_file(angle):
    global results_path
    cmd = "docker exec -i -w /home/fenics/shared/murtazo/cloudnaca/ fenics_cont ./runair.sh 10 0.001 10. 1 " + str(angle) +" 200 0"

    subp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subp.wait()
    if subp.poll() <= 0:
        results_filename = "r0a" + str(angle) + "n200.m"
        cpcmd = "docker cp fenics_cont:/home/fenics/shared/murtazo/navier_stokes_solver/results/" + results_filename + " " + results_path
        print(cpcmd)
        subprocess.run(cpcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return results_filename
    else:
        return 0


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000 ,debug=True)

