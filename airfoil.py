import os
import subprocess
from subprocess import call
from celery import Celery

celery = Celery('airfoil', broker='amqp://', backend='amqp')

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

    
