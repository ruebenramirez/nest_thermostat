#! /usr/bin/python
import os
from flask import Flask, Response, json
app = Flask(__name__)
import ConfigParser
from nest_thermostat import Nest
from redis_cache import cache_it, SimpleCache

redis_host = os.environ['REDIS-HOST_PORT_6379_TCP_ADDR']
nest_config = SimpleCache(limit=1000, expire=None,
                          hashkeys=True, host=redis_host,
                          port=6379, db=1, namespace='nest')


class Config(object):

    def __init__(self):
        conf_file = 'nest_api.cfg'
        conf = ConfigParser.ConfigParser()
        conf.readfp(open(conf_file))
        self.user = str(conf.get('Nest', 'username'))
        self.password = str(conf.get('Nest', 'password'))
        self.serial = str(conf.get('Nest', 'serial'))
        self.units = str(conf.get('Nest', 'temperature_units'))


@cache_it(cache=nest_config)
def get_nest():
    opts = Config()
    n = Nest(opts.user, opts.password, serial=opts.serial, units=opts.units)
    n.login()
    return n


@app.route('/')
def nest_status():
    n = get_nest()
    return Response(json.dumps(n.get_status()), mimetype='application/json')


@app.route('/temperature')
def nest_temperature():
    n = get_nest()
    temps = {'current_temperature': n.show_curtemp(),
             'target_temperature': n.show_target(),
             'mode': n.show_curmode()}
    return Response(json.dumps(temps), mimetype='application/json')


@app.route('/humidity')
def nest_humidity():
    n = get_nest()
    humidity = {'current': n.show_humidity()}
    return Response(json.dumps(humidity), mimetype='application/json')
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
