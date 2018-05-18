#!/usr/bin/env python
import os
from http.cookiejar import MozillaCookieJar, Cookie
from urllib.parse import urlparse

import requests
from selenium.webdriver.remote.webdriver import WebDriver

from cvm import dom, ui, view


class Cookies:
    def __init__(self, driver: WebDriver):
        self._driver = driver

    def clear(self):
        self._driver.delete_all_cookies()

    def jar(self):
        jar = MozillaCookieJar()
        for cookie_dict in self._driver.get_cookies():
            jar.set_cookie(Cookies.create(cookie_dict))
        return jar

    def get(self, name: str) -> Cookie:
        cookie_dict = self._driver.get_cookie(name)
        return Cookies.create(cookie_dict) if cookie_dict else None

    def add(self, cookie: Cookie):
        self._driver.add_cookie({
            'name': cookie.name,
            'value': cookie.value,
            'domain': cookie.domain,
            'path': cookie.path,
            'secure': cookie.secure,
            'expiry': cookie.expires
        })

    def remove(self, name: str):
        self._driver.delete_cookie(name)

    @staticmethod
    def create(cookie_dict: dict) -> Cookie:
        return Cookie(
            version=0,
            name=cookie_dict['name'],
            value=cookie_dict['value'],
            port=None,
            port_specified=False,
            domain=cookie_dict['domain'],
            domain_specified=True,
            domain_initial_dot=False,
            path=cookie_dict['path'],
            path_specified=True,
            secure=cookie_dict['secure'],
            expires=cookie_dict.get('expiry', None),
            discard=False,
            comment=None,
            comment_url=None,
            rest=None,
            rfc2109=False
        )


class Browser(dom.Node):
    def __init__(self, driver: WebDriver):
        super().__init__(driver, driver)
        self._agent = None

    def load(self, page: view.Page):
        return page.get(self)

    @property
    def url(self) -> str:
        return self._driver.current_url

    @url.setter
    def url(self, url: str):
        self._driver.get(urlparse(url, 'http').geturl())

    def refresh(self):
        self._driver.refresh()

    @property
    def scheme(self) -> str:
        return urlparse(self.url).scheme

    @property
    def hostname(self) -> str:
        return urlparse(self.url).hostname

    @property
    def port(self) -> str:
        return urlparse(self.url).port

    @property
    def username(self) -> str:
        return urlparse(self.url).username

    @property
    def password(self) -> str:
        return urlparse(self.url).password

    @property
    def path(self) -> str:
        return urlparse(self.url).path

    @property
    def html(self) -> str:
        return self._driver.page_source

    @property
    def cookies(self) -> Cookies:
        return Cookies(self._driver)

    @property
    def agent(self) -> str:
        if not self._agent:
            self._agent = self._driver.execute_script('return navigator.userAgent;')
        return self._agent

    def get(self, url: str, params=None):
        return requests.get(url, params, headers={'User-Agent': self.agent}, cookies=self.cookies.jar())

    def post(self, url: str, data=None, json=None):
        return requests.post(url, data, json, headers={'User-Agent': self.agent}, cookies=self.cookies.jar())

    def put(self, url: str, data=None):
        return requests.put(url, data, headers={'User-Agent': self.agent}, cookies=self.cookies.jar())

    def delete(self, url: str):
        return requests.delete(url, headers={'User-Agent': self.agent}, cookies=self.cookies.jar())

    def write(self, url: str, fd: int):
        src = urlparse(url, 'http')
        file = self.get(src.geturl())
        fd.write(file.content)

    def save(self, url: str, path: str):
        src = urlparse(url, 'http')
        dst = path if os.path.basename(path) else os.path.join(path, os.path.basename(src.path))
        file = self.get(src.geturl())
        with open(dst, 'wb') as fd:
            fd.write(file.content)

    def back(self):
        self._driver.back()

    def forward(self):
        self._driver.forward()

    def refresh(self):
        self._driver.refresh()

    def eval(self, script, *args):
        return self._driver.execute_script(script, args)

    def scroll(self, position: ui.Position):
        return self._driver.execute_script('window.scrollTo(' + str(position.x) + ',' + str(position.y) + ')')

    def scroll_top(self):
        self._driver.execute_script(
            'window.scrollTo(0,0);'
        )

    def scroll_bottom(self):
        self._driver.execute_script(
            'window.scrollTo(0,document.body.scrollHeight);'
        )

    def scroll_element(self, node: dom.Node):
        self._driver.execute_script(
            'var r=arguments[0].getBoundingClientRect();'
            'var x=r.left+(r.right-r.left)/2;'
            'var y=r.top+(r.bottom-r.top)/2;'
            'window.scrollTo(x+window.innerWidth/2,y+window.innerHeight/2);',
            node._node
        )

    def close(self):
        self._driver.close()

    def quit(self):
        self._driver.quit()
