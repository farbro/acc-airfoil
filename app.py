#!flask/bin/python
from flask import Flask, jsonify, render_template, request, send_from_directory
from celery import Celery
import glob
import os
import json
import re
import copy
import subprocess

app = Flask(__name__)
celery = Celery(app.name, backend='rpc://', broker='pyamqp://worker:fnurkgurk@g2-airfoil-main.local:5672/twhost')

#mesh_files = "data/*"
results_path = "/home/ubuntu/acc-airfoil/data/results/"

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

    # Get parameters
    start_angle = request.form['start_angle']
    end_angle = request.form['end_angle']
    num_angles = request.form['num_angles']

    # Calculate angle set
    angle_step = (end_angle - start_angle) / num_angles

    num_tasks = num_angles

    with app.app_context():

        # Push all angles to the queue
        for angle in range(start_angle, end_angle, angle_step):
            results.append(process_file.delay(angle))
   
    return ('', 204)

@app.route("/stop", methods=["POST"])
def stop():
    global results
    for result in results:
        result.revoke()

    results = []

    return ('', 204)

# @app.route('/data', methods=['GET'])
# def get_result_data():
#     global results
#     global num_tasks
#     lift_res = []
#     for result in results.collect():
#         dir = result.get()
#         lift = os.popen("cat " + dir).readlines()
#         lift_res.append(float(lift[0]))
#     return jsonify(result_data)


@app.route('/data', methods=['GET'])
def get_result_data():
    global results
    global num_tasks

    for result in results:
        if result.ready():
            res_dir = result.get()
            if res_dir:
                result_data['files'].append(res_dir)
                filename = res_dir.split('/')[-1]
                # This function should be called here?
                get_file(filename)
		results.remove(result)
                result_data['total_files'] += 1
    result_data['proggress'] = (1 - len(results)/num_tasks)*100
    return jsonify(result_data)


@celery.task
def process_file(angle):
    cmd1 = "cd /home/ubuntu/acc-airfoil/murtazo/cloudnaca/"
    cmd2 = "./runair.sh 2 0.01 10. 1 " + str(angle) +" 200 0"
    cmd = cmd1 + " && " + cmd2
    subp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subp.wait()
    if subp.poll() == 0:
        cpcmd = "cp /home/ubuntu/acc-airfoil/murtazo/navier_stokes_solver/results/r0a" + str(angle) + "n200.m " + results_path + "r0a" + str(angle) + "n200.m"
        subprocess.run(cpcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        dir = results_path + "r0a" + str(angle) + "n200.m"
        print(dir)
    else:
        print(0)

# Serve result files
# I'm not sure where this function should be called
@app.route('/get-file/<path:filename>', methods=['GET'])
def get_file(filename):
    return send_from_directory(results_path, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80 ,debug=True)



