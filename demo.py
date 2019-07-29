#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import argparse
import requests


class InmobiJsonClient(object):
    """ Inmobi JSON client.
    """

    def __init__(self, config_file, session_file):
        self.__config_file = config_file
        self.__session_file = session_file

        self.__sessionId = None
        self.__accountId = None
        self.__secretKey = None

    def load_session(self):
        """ Load session.
        """
        expired = True
        if os.path.isfile(self.__session_file):
            with open(self.__session_file, 'r') as f:
                session = json.load(f)
                if time.time() - session['createTime'] < 3600 * 24:
                    expired = False

        if expired:
            print 'pending to request a new session'
            if not os.path.isfile(self.__config_file):
                raise RuntimeError('config file is missing')
            with open(self.__config_file, 'r') as f:
                creds = json.load(f)
                username = creds['userName']
                password = creds['password']
                secretkey = creds['secretKey']

            res = InmobiJsonClient.request_session(username, password, secretkey)
            if not res:
                raise RuntimeError('http return code is not 200')
            if res['error']:
                raise RuntimeError('request session failed')
            sessionid = res['respList'][0]['sessionId']
            accountid = res['respList'][0]['accountId']

            with open(self.__session_file, 'w') as f:
                session = {
                        'sessionId': sessionid,
                        'accountId': accountid,
                        'secretKey': secretkey,
                        'createTime': int(time.time()),
                        }
                json.dump(session, f, indent=4)

        with open(self.__session_file, 'r') as f:
            session = json.load(f)
            self.__sessionId = session['sessionId']
            self.__accountId = session['accountId']
            self.__secretKey = session['secretKey']
            print 'load session: %s' % session

    @classmethod
    def request_session(cls, username, password, secretkey):
        """ Request a valid session.
        """
        headers = {
                'userName': username,
                'password': password,
                'secretKey': secretkey,
                }
        resp = requests.get('https://api.inmobi.com/v1.0/generatesession/generate', headers=headers)
        resp.close()
        if resp.status_code == 200:
            return resp.json()
        return None

    def call(self, query):
        """ Query.
        """
        print 'query:\n%s' % json.dumps(query)
        headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'accountId': self.__accountId,
                'secretKey': self.__secretKey,
                'sessionId': self.__sessionId,
                }
        resp = requests.post('https://api.inmobi.com/v3.0/reporting/publisher', headers=headers, data=json.dumps(query))
        resp.close()
        if resp.status_code == 200:
            return resp.json()
        return None


def parse_args():
    """ Parse arguments and return a list of date.
    """
    parser = argparse.ArgumentParser(description='Inmobi query tools.')
    parser.add_argument('-d', '--date', dest='date', nargs='*', type=str, required=True, help='specify one day or date range with format "YYYYmmdd"')
    args = parser.parse_args()

    # validate
    if len(args.date) == 0:
        sys.stderr.write("ERROR: '--date' option: no value specified")
        sys.exit(1)
    if len(args.date) > 2:
        sys.stderr.write("ERROR: '--date' option: too many value specified")
        sys.exit(1)
    for s in args.date:
        if len(s) != 8 or not s.isdigit():
            sys.stderr.write("ERROR: '--date' option: invalid value '%s'" % s)
            sys.exit(1)

    return args.date


config_file = './config.json'
session_file = './session.json'


if __name__ == '__main__':
    date = parse_args()
    print 'date: %s' % date

    cli = InmobiJsonClient(config_file, session_file)
    cli.load_session()

    query = {}  # TODO
    # query = {"reportRequest":{"metrics":["adImpressions"],"timeFrame":"2019-07-20:2019-07-23","groupBy":["date"], "filterBy":[{ "filterName":"adImpressions", "filterValue": 0, "comparator":">"}]}}

    res = cli.call(query)
    print "result:\n%s" % res

    sys.exit(0)
