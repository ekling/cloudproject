import os
import subprocess
from subprocess import call
from celery import Celery

celery = Celery('airfoil', broker='amqp://worker:pw@{}/host'.format(os.environ['BROKER_IP']), backend='amqp')

def calcRatio():
    numOfRatios = 0
    totRatio = 0.0
    for filename in os.listdir('/home/emil/Project/naca_airfoil/result/'):
        if filename.endswith(".m"):
            with open(filename, "r") as f:
                lines = f.readlines()[1:]
                for results in lines:
                    words = results.split()
                    drag = words[1]
                    lift = words[2]
                    numOfRatios += 1
                    totRatio += float(drag)/float(lift)
    if numOfRatios == 0:
        numOfRatios = 1
    return totRatio/numOfRatios


def gen_msh(angle, nodes, ref):
    name = "./run.sh " + str(angle) + " " + str(angle) + " 1 " + str(nodes) + " " + str(ref)
    print name
    subprocess.call(name, shell=True)

def convert():
        for filename in os.listdir('/home/emil/Project/naca_airfoil/msh'):
                if filename.endswith(".msh"):
                        name = "dolfin-convert " + "/home/emil/Project/naca_airfoil/msh/" + filename + " /home/emil/Project/naca_airfoil/msh/" + filename + ".xml"
                        subprocess.call(name, shell=True)


@celery.task()
def airfoil(angle, nodes, ref, samples, viscosity, speed, time):
    print "got here"
    gen_msh(angle, nodes, ref)

    convert()

    for filename in os.listdir('/home/emil/Project/naca_airfoil/msh'):
        if "r" + str(ref) in filename and filename.endswith(".xml"):
            name = './navier_stokes_solver/airfoil ' + str(samples) + ' ' + str(viscosity) + ' ' + str(speed) + ' ' + str(time) + ' msh/' + filename
            #print name
            subprocess.call(name, shell=True)
