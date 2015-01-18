#! /usr/bin/python

"""
nest_thermostat -- a python interface to the Nest Thermostat
by Scott M Baker, smbaker@gmail.com, http://www.smbaker.com/
updated by Bob Pasker bob@pasker.net http://pasker.net
and Rueben Ramirez ruebenramirez@gmail.com http://ruebenramirez.com
"""

import os
import requests
import json
from redis_cache import cache_it, SimpleCache


redis_host = os.environ['REDIS-HOST_PORT_6379_TCP_ADDR']
twenty_seconds = 20
docker_cache = SimpleCache(limit=1000, expire=twenty_seconds,
                           hashkeys=True, host=redis_host,
                           port=6379, db=1, namespace='nest')


class Nest:

    def __init__(self, username, password, serial=None, index=0, units='F',
                 debug=False):
        self.username = username
        self.password = password
        self.serial = serial
        self.units = units
        self.index = index
        self.debug = debug
        self.status = None

    def login(self):
        response = requests.post("https://home.nest.com/user/login",
                                 data={"username": self.username,
                                       "password": self.password},
                                 headers={"user-agent":
                                          "Nest/1.1.0.10 CFNetwork/548.0.4"})

        response.raise_for_status()

        res = response.json()
        self.transport_url = res["urls"]["transport_url"]
        self.access_token = res["access_token"]
        self.userid = res["userid"]
        # print self.transport_url, self.access_token, self.userid

    def get_status(self):
        auth_url = self.transport_url + "/v2/mobile/user." + self.userid
        headers = {"user-agent": "Nest/1.1.0.10 CFNetwork/548.0.4",
                   "Authorization": "Basic " + self.access_token,
                   "X-nl-user-id": self.userid,
                   "X-nl-protocol-version": "1"}
        response = requests.get(auth_url,
                                headers=headers)

        response.raise_for_status()
        res = response.json()

        self.structure_id = res["structure"].keys()[0]
        self._set_serial(res)
        self.status = res
        # status = ["res.keys", res.keys(),
        #           "res[structure][structure_id].keys",
        #               res["structure"][self.structure_id].keys(),
        #           "res[device].keys", res["device"].keys(),
        #           "res[device][serial].keys",
        #               res["device"][self.serial].keys(),
        #           "res[shared][serial].keys",
        #               res["shared"][self.serial].keys()]
        # return ''.join(status)
        return res

    def temp_in(self, temp):
        if self.units == "F":
            return (temp - 32.0) / 1.8
        else:
            return temp

    def temp_out(self, temp):
        if self.units is 'F':
            return temp*1.8 + 32.0
        else:
            return temp

    @cache_it(cache=docker_cache)
    def show_status(self):
        if not self.status:
            self.get_status()
        shared = self.status["shared"][self.serial]
        device = self.status["device"][self.serial]

        allvars = shared
        allvars.update(device)

        for k in sorted(allvars.keys()):
            print k + "."*(32-len(k)) + ":", allvars[k]

    @cache_it(cache=docker_cache)
    def show_curtemp(self):
        if not self.status:
            self.get_status()
        temp = self.status["shared"][self.serial]["current_temperature"]
        temp = self.temp_out(temp)
        return temp

    @cache_it(cache=docker_cache)
    def show_target(self):
        if not self.status:
            self.get_status()
        temp = self.status["shared"][self.serial]["target_temperature"]
        temp = self.temp_out(temp)
        return temp

    @cache_it(cache=docker_cache)
    def show_curmode(self):
        if not self.status:
            self.get_status()
        mode = self.status["shared"][self.serial]["target_temperature_type"]
        return mode

    @cache_it(cache=docker_cache)
    def show_humidity(self):
        if not self.status:
            self.get_status()
        humidity = self.status["shared"][self.serial]["current_humidity"]
        return humidity

    def _set(self, data, which):
        if (self.debug):
            print json.dumps(data)
        url = "%s/v2/put/%s.%s" % (self.transport_url, which, self.serial)
        if (self.debug):
            print url
        response = requests.post(
            url,
            data=json.dumps(data),
            headers={
                "user-agent": "Nest/1.1.0.10 CFNetwork/548.0.4",
                "Authorization": "Basic " +
                self.access_token,
                "X-nl-protocol-version": "1"})

        if response.status_code > 200:
            if (self.debug):
                print response.content
        response.raise_for_status()
        return response

    def _set_shared(self, data):
        self._set(data, "shared")

    def _set_device(self, data):
        self._set(data, "device")

    def set_temperature(self, temp):
        return self._set_shared({
            "target_change_pending": True,
            "target_temperature": self.temp_in(temp)
            })

    def set_fan(self, state):
        return self._set_device({
            "fan_mode": str(state)
            })

    def set_mode(self, state):
        return self._set_shared({
            "target_temperature_type": str(state)
        })

    def toggle_away(self):
        was_away = self.status['structure'][self.structure_id]['away']
        data = '{"away":%s}' % ('false' if was_away else 'true')
        response = requests.post(
            self.transport_url +
            "/v2/put/structure." +
            self.structure_id,
            data=data,
            headers={
                "user-agent": "Nest/1.1.0.10 CFNetwork/548.0.4",
                "Authorization": "Basic " +
                self.access_token,
                "X-nl-protocol-version": "1"})
        response.raise_for_status()
        return response

    def _set_serial(self, res):
        """
        helper: ensure that serial is set
        """
        if (self.serial is None):
            self.device_id = res["structure"][self.structure_id]["devices"][
                self.index]
            self.serial = self.device_id.split(".")[1]
