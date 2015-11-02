import time
import os
import pickledb
from airfoil import airfoil
from celery import group, subtask
from flask import Flask, jsonify, request, redirect, render_template

app = Flask(__name__)

db = pickledb.load('Completed.db',False)


def divide_input(start, stop, steps):
    diff = 0

    if start == stop:
        return [start]

    try:
        diff = int((stop-start)/steps)

    except ZeroDivisionError as e:
        print e, "Number of steps set to 1"

    if diff == 0:
        diff = 1

    angles = []

    for i in range(0, steps+1):
        if start + i * diff > stop:
            break
        angles.append(start + i*diff)

    return angles

def calc_airfoil(msh_input, airfoil_input):



    angles = divide_input(msh_input[0], msh_input[1], msh_input[2])
    
    queue = [airfoil.s(x, msh_input[3], y, airfoil_input[0], airfoil_input[1],
             airfoil_input[2], airfoil_input[3]) for x in angles for y in range(0, msh_input[4]+1)]
    print queue
    g = group(queue)

    res = g()
    while (res.ready() == False):
        print res.ready()
        time.sleep(3)

    result = res.get()

    return result

@app.route("/form", methods=["GET"])
def init():
    return render_template("forms.html")

@app.route('/fetch_form', methods=['POST'])
def forms():
    angle_min = request.form['angle_min']
    angle_max = request.form['angle_max']
    num_angles = request.form['num_angles']
    nodes = request.form['nodes']
    refinement = request.form['refinement']
    samples = request.form['samples']
    viscosity = request.form['viscosity']
    speed = request.form['speed']
    time = request.form['time']

    msh_input = [int(angle_min), int(angle_max), int(num_angles), int(nodes), int(refinement)]
    airfoil_input = [int(samples), float(viscosity), int(speed), int(time)]
    
    if db.get(str(msh_input)+str(airfoil_input)) is None:
        res = calc_airfoil(msh_input, airfoil_input)
        db.set(str(msh_input)+str(airfoil_input),res)
    else:
        res = db.get(str(msh_input)+str(airfoil_input))
    
    return render_template('results.html', data=res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
