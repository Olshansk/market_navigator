import os

def rm_f(filename):
    if os.path.isfile(filename):
        os.remove(filename)