#!flask/bin/python
from flask import Flask, jsonify, render_template, request, send_from_directory
from celery import Celery
import glob
import json
import re
import copy

app = Flask(__name__)
celery = Celery(app.name, backend='rpc://', broker='pyamqp://worker:fnurkgurk@g2-airfoil-main.local:5672/twhost')

mesh_files = "data/*"
results_path = 'data/results'

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

