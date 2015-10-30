import os
import subprocess
from subprocess import call
from celery import Celery

celery = Celery('airfoil', broker='amqp://worker:pw@{}/host'.format(os.environ['BROKER_IP']), backend='amqp')

def calc_ratio():
    numOfRatios = 0
    totRatio = 0.0
    for filename in os.listdir('/home/ubuntu/project/results/'):
        if filename.endswith(".m"):
            name = "sudo chmod ugo+wrx " + filename
            subprocess.call(name, shell=True)
            with open('results/' + filename, "r") as f:
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
    for filename in os.listdir('/home/ubuntu/project/msh'):
        if filename.endswith(".msh"):
            name = "sudo chmod ugo+wrx " + filename
            subprocess.call(name, shell=True)
            name = "sudo dolfin-convert " + "/home/ubuntu/project/msh/" + filename + " /home/ubuntu/project/msh/" + filename + ".xml"
            subprocess.call(name, shell=True)


@celery.task()
def airfoil(angle, nodes, ref, samples, viscosity, speed, time):
    gen_msh(angle, nodes, ref)

    convert()

    for filename in os.listdir('/home/ubuntu/project/msh'):
        if "r" + str(ref) in filename and filename.endswith(".xml"):
            name = "sudo chmod ugo+wrx " + filename
            subprocess.call(name, shell=True)
            name = 'sudo ./navier_stokes_solver/airfoil ' + str(samples) + ' ' + str(viscosity) + ' ' + str(speed) + ' ' + str(time) + ' msh/' + filename
            #print name
            subprocess.call(name, shell=True)

    return calc_ratio()
