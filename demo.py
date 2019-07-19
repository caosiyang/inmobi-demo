#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests


class InmobiJsonClient(object):
    """ Inmobi JSON client.
    """

    userName = 'TODO'
    password = 'TODO'
    secretKey = 'TODO'

    def __init__(self):
        self.__credential = None
        self.__sessionId = None
        self.__accountId = None

    def request_session(self):
        """ Request a valid session.
        """
        headers = {
                'userName': self.userName,
                'password': self.password,
                'secretKey': self.secretKey
                }
        resp = requests.get('https://api.inmobi.com/v1.0/generatesession/generate', headers=headers)
        resp.close()
        if resp.status_code == 200:
            jsonobj = resp.json()
            print jsonobj
            if not jsonobj['error']:
                self.__credential = jsonobj
                self.__sessionId = jsonobj['respList'][0]['sessionId']
                self.__accountId = jsonobj['respList'][0]['accountId']
                return True
        return False

    def call(self, query):
        """ Query.
        """
        if self.__credential is None:
            raise RuntimeError('no valid session')
        headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'secretKey': self.secretKey,
                'sessionId': self.__sessionId,
                'accountId': self.__accountId,
                }
        resp = requests.post('https://api.inmobi.com/v3.0/reporting/publisher', headers=headers, data=query)
        resp.close()
        if resp.status_code == 200:
            return resp.json()
        return None


if __name__ == '__main__':
    cli = InmobiJsonClient()
    if cli.request_session():
        print 'OK: request a valid session'
    else:
        print 'ERR: request a valid session'

    query = {}  # TODO
    res = cli.call(query)
    print res

    sys.exit(0)
