# -*- coding: UTF-8 -*-
import unittest
import time

from bs4 import BeautifulSoup
import requests

import datetime
import re
import sys


class Yopmail(object):
    def __init__(self, userid):
        self.jar = requests.cookies.RequestsCookieJar()
        self.ses = requests.Session()
        self.localtime = None
        self.userid = userid

    def request(self, url, params=None):
        if not self.localtime is None:
            # after first time we use it, we start to update it everytime
            self.add_localtime()
        rq = self.ses.get(url, params=params, cookies=self.jar)
        # print r.status_code
        # for cookie in r.cookies:
        #     print cookie
        return rq

    def r1(self):
        self.request('http://www.yopmail.com')

    def extract_yp(self, req):
        bs = BeautifulSoup(req.text, 'html.parser')
        # search for:
        #   <input type="hidden" name="yp" id="yp" value="OAwt2BGN5AGD4AQp2ZmDmZt" />
        input_el = bs.find('input', {'name': 'yp', 'id': 'yp'})
        self.yp = input_el['value']
        # print 'yp is:', self.yp

    def r2(self):
        self.extract_yp(
            self.request('http://www.yopmail.com/zh/'))

    def add_localtime(self):
        now = datetime.datetime.now().time()
        self.localtime = '%d:%d' % (now.hour, now.minute)
        self.jar.set('localtime', self.localtime,
                     domain='yopmail.com', path='/')

    def r3(self):
        self.username = self.userid
        self.add_localtime()
        #yp = self.jar.get("yp", domain="yopmail.com")
        data = {'yp': self.yp, 'login': self.username}
        rq = self.ses.post(
            'http://www.yopmail.com/zh/',
            data,
            cookies=self.jar)
        # print rq.status_code
        # for cookie in rq.cookies:
        #     print cookie

    YJ_RE = re.compile(r"value\+\'\&yj\=([0-9a-zA-Z]*)\&v\=\'", re.MULTILINE)

    def extract_yj(self, req):
        # serach for:
        #   value+'&yj=QBQVkAQVmZmZ4BQR0ZwNkAN&v='
        match = self.YJ_RE.search(req.text)
        self.yj = match.groups()[0]

    def r7(self):
        self.extract_yj(
            self.request("http://www.yopmail.com/style/2.6/webmail.js"))

    def extract_inbox(self, req):
        """<div  class=\"m\" onclick=\"g(6,0);\" id=\"m6\">
                <div   class=\"um\"><a class=\"lm\" href=\"mail.php?b=pelado&id=me_ZGpjZGVkZGpmZmZ2ZQNjAmZ2AwtjBN==\">
                <span class=\"lmfd\">
                <span class=\"lmh\">14:33</span>"""
        bs = BeautifulSoup(req.text, 'html.parser')
        results = {}
        for idx in range(10):
            div_mX = bs.find('div', {'class': 'm', 'id': 'm%d' % idx})
            if div_mX is None:
                continue
            a = div_mX.find('a', {'class': 'lm'})

            href = a['href'].rsplit('&id=', 1)[1]
            results[idx] = href

        self.mailids = results

    def r8(self, mail_idx=None, page=1):
        if mail_idx is None:
            mailid = ''
        else:
            mailid = self.mailids[mail_idx]
        params = {
            'login': self.username,
            'p': str(page),  # page
            'd': '',  # mailid? to delete?
            'ctrl': mailid,  # mailid or ''
            'scrl': '',  # always?
            'spam': True,  # false
            'yf': '005',
            'yp': self.yp,
            'yj': self.yj,
            'v': "2.9",
            'r_c': '',  # ""
            # idaff / sometimes "none" / nextmailid='last' / mailid =
            # id('m%d'%mail_nr)
            'id': "",
        }
        self.extract_inbox(
            self.request("http://www.yopmail.com/zh/inbox.php", params=params))

    def fetch(self, mail_idx):
        if mail_idx is None:
            mailid = ''
        else:
            mailid = self.mailids[mail_idx]
        params = {'b': self.username,
                  'id': mailid}  # mailid 'me_ZGpjZGV1ZwRkZwD0ZQNjAmx0AmpkAj=='
        return self.request(
            'http://www.yopmail.com/zh/m.php', params=params)

    def __iter__(self):
        return iter(self.mailids.keys())

    def login(self):
        self.r1()
        self.r2()
        self.r3()
        self.r7()
        self.r8()
        return self


"""
class TestSomething(unittest.TestCase):
    def test_yj_re(self):
        value = 'QBQVkAQVmZmZ4BQR0ZwNkAN'
        sample = "value+'&yj=QBQVkAQVmZmZ4BQR0ZwNkAN&v='"
        self.assertIsNotNone(Yopmail.YJ_RE.match(sample))
        self.assertEqual(Yopmail.YJ_RE.match(sample).groups()[0], value)
"""


def main(username):
    em = Yopmail(username)
    em.login()
    for _id in em:
        print('--------------------------------------')
        resp = em.fetch(_id)
        with open(username + '_' + str(_id) + ".html", "wb") as f:
            try:
                f.write(resp.content)
                print(repr(resp.text)[:30], '..')
            except UnicodeEncodeError as e:
                try:
                    f.write(resp.text.encode('utf-8'))
                except Exception as e2:
                    f.write("error found:")
                    f.write(repr(e2))
                    f.write("\r\n")
                    f.write(repr(resp.text))
        print()
        time.sleep(1)

if __name__ == "__main__":
    main("test")
