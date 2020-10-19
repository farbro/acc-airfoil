#!flask/bin/python
from flask import Flask, jsonify, render_template, request
from celery import Celery
import glob
import json
import re
import copy

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

    # Initialize result data
    result_data['total_files'] = 0
    result_data['proggress'] = 0

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

            # TODO run webhooks to scale in

    result_data['proggress'] = (1 - len(results)/num_tasks)*100
    return jsonify(result_data)

@celery.task
def process_file(angle):

    # TODO run process file with airfoil and return result

    return something


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80 ,debug=True)

