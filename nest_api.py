#! /usr/bin/python

from flask import Flask, Response, json
app = Flask(__name__)
import ConfigParser
from nest_thermostat import Nest


class Config(object):

    def __init__(self):
        conf_file = 'nest_api.cfg'
        conf = ConfigParser.ConfigParser()
        conf.readfp(open(conf_file))
        self.user = str(conf.get('Nest', 'username'))
        self.password = str(conf.get('Nest', 'password'))
        self.serial = str(conf.get('Nest', 'serial'))
        self.units = str(conf.get('Nest', 'units'))


def get_nest():
    opts = Config()
    n = Nest(opts.user, opts.password, serial=opts.serial, units=opts.units)
    n.login()
    return n


@app.route('/')
def nest_status():
    n = get_nest()
    return Response(json.dumps(n.get_status()), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
