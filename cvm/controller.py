#!/usr/bin/env python

from enum import Enum
from http.cookiejar import LWPCookieJar, Cookie

import requests
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait


class Selector(Enum):
    CLASS = 1
    CSS = 2
    ID = 3
    LINK = 4
    NAME = 5
    PLINK = 6
    TAG = 7
    XPATH = 8

    @staticmethod
    def one(selector):
        return {
            Selector.CLASS: lambda src, value: src.find_element_by_class_name(value),
            Selector.CSS: lambda src, value: src.find_element_by_css_selector(value),
            Selector.ID: lambda src, value: src.find_element_by_id(value),
            Selector.LINK: lambda src, value: src.find_element_by_link_text(value),
            Selector.NAME: lambda src, value: src.find_element_by_name(value),
            Selector.PLINK: lambda src, value: src.find_element_by_partial_link_text(value),
            Selector.TAG: lambda src, value: src.find_element_by_tag_name(value),
            Selector.XPATH: lambda src, value: src.find_element_by_xpath(value),
        }[selector]

    @staticmethod
    def all(selector):
        return {
            Selector.CLASS: lambda src, value: src.find_elements_by_class_name(value),
            Selector.CSS: lambda src, value: src.find_elements_by_css_selector(value),
            Selector.ID: lambda src, value: src.find_elements_by_id(value),
            Selector.LINK: lambda src, value: src.find_elements_by_link_text(value),
            Selector.NAME: lambda src, value: src.find_elements_by_name(value),
            Selector.PLINK: lambda src, value: src.find_elements_by_partial_link_text(value),
            Selector.TAG: lambda src, value: src.find_elements_by_tag_name(value),
            Selector.XPATH: lambda src, value: src.find_elements_by_xpath(value),
        }[selector]


class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    @staticmethod
    def of(position: dict):
        return Position(
            x=position['x'],
            y=position['y'],
        )


class Size:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    @staticmethod
    def of(size: dict):
        return Size(
            width=size['width'],
            height=size['height'],
        )


class Node:
    def __init__(self, driver: WebDriver, node):
        self._driver = driver
        self._node = node

    def element(self, selector: Selector, value: str, timeout: float = 0):
        try:
            element = WebDriverWait(self._driver, timeout).until(
                lambda driver: Selector.one(selector)(self._node, value)
            )
        except TimeoutException as e:
            return None
        return Element(self._driver, element) if element else None

    def elements(self, selector: Selector, value: str, timeout: float = 0):
        try:
            elements = WebDriverWait(self._driver, timeout).until(
                lambda driver: Selector.all(selector)(self._node, value)
            )
        except TimeoutException as e:
            return []
        return [Element(self._driver, element) for element in elements]

    def screenshot(self, path) -> bool:
        return self._node.screenshot(path)


class Cookies:
    def __init__(self, driver: WebDriver):
        self._driver = driver

    def clear(self):
        self._driver.delete_all_cookies()

    def jar(self):
        jar = LWPCookieJar()
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
                port='80',
                port_specified=False,
                domain=cookie_dict['domain'],
                domain_specified=True,
                domain_initial_dot=False,
                path=cookie_dict['path'],
                path_specified=True,
                secure=cookie_dict['secure'],
                expires=cookie_dict['expiry'],
                discard=False,
                comment=None,
                comment_url=None,
                rest=None,
                rfc2109=False
            )


class Browser(Node):
    def __init__(self, driver: WebDriver):
        super().__init__(driver, driver)

    @property
    def url(self) -> str:
        return self._driver.current_url

    @url.setter
    def url(self, url: str):
        self.load(url)

    @property
    def html(self) -> str:
        return self._driver.page_source

    @property
    def cookies(self) -> Cookies:
        return Cookies(self._driver)

    def load(self, url: str):
        self._driver.get(url)

    def save(self, url: str, path: str):
        with open(path, 'wb') as fd:
            fd.write(requests.get(url, cookies=self.cookies.jar()).content)

    def back(self):
        self._driver.back()

    def forward(self):
        self._driver.forward()

    def refresh(self):
        self._driver.refresh()

    def eval(self, script, *args):
        return self._driver.execute_script(script, args)

    def scroll(self, position: Position):
        return self._driver.execute_script('window.scrollTo(' + str(position.x) + ',' + str(position.y) + ')')

    def scroll_top(self):
        self._driver.execute_script('window.scrollTo(0,0)')

    def scroll_bottom(self):
        self._driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')

    def close(self):
        self._driver.close()

    def quit(self):
        self._driver.quit()


class Element(Node):
    def __init__(self, driver: WebDriver, element: WebElement):
        super().__init__(driver, element)

    @property
    def tag(self):
        return self._node.tag_name

    @property
    def parent(self):
        return Element(self._driver, self._node.parent)

    @property
    def text(self):
        return self._node.text

    @property
    def enabled(self):
        return self._node.is_enabled()

    @property
    def displayed(self):
        return self._node.is_displayed()

    @property
    def selected(self):
        return self._node.is_selected()

    @property
    def size(self):
        return Size.of(self._node.location())

    @property
    def position(self):
        return Position.of(self._node.location())

    def attribute(self, name):
        return self._node.get_attribute(name)

    def clear(self):
        self._node.clear()

    def click(self):
        self._node.click()

    def input(self, value):
        self._node.send_keys(value)

    def submit(self):
        self._node.submit()

    def __getattr__(self, item):
        return self.attribute(item)

    def __eq__(self, node: Node):
        return self._node == node._node

    def __ne__(self, node: Node):
        return self._node != node._node
