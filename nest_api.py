#! /usr/bin/python

from flask import Flask
app = Flask(__name__)
import ConfigParser
from nest_thermostat import Nest


class Config(object):

    def __init__(self):
        conf_file = 'nest.cfg'
        conf = ConfigParser.ConfigParser()
        conf.readfp(open(conf_file))
        self.user = str(conf.get('Nest', 'username')))
        self.password = str(conf.get('Nest', 'password'))
        self.serial = str(conf.get('Nest', 'Serial'))
        self.index = str(conf.get('Nest', 'Index'))

def get_nest():
    opts = Config()
    n = Nest(opts.user, opts.password, opts.serial, opts.index, units=units)
    n.login()
    return n

@app.route('/')
def nest_status():
    n = get_nest()
    return n.get_status()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
