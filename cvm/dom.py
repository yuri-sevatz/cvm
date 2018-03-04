#!/usr/bin/env python
from enum import Enum

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.wait import WebDriverWait

from cvm import ui


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


class Node:
    def __init__(self, driver: WebDriver, node):
        self._driver = driver
        self._node = node

    def element(self, selector: Selector, value: str, timeout: float = 0):
        try:
            def func(driver):
                return Selector.one(selector)(self._node, value)
            element = WebDriverWait(self._driver, timeout).until(func) if timeout else func(self._driver)
        except NoSuchElementException:
            return None
        except TimeoutException:
            return None
        return Element(self._driver, element) if element else None

    def elements(self, selector: Selector, value: str, timeout: float = 0):
        try:
            def func(driver):
                return Selector.all(selector)(self._node, value)
            elements = WebDriverWait(self._driver, timeout).until(func) if timeout else func(self._driver)
        except NoSuchElementException:
            return []
        except TimeoutException:
            return []
        return [Element(self._driver, element) for element in elements]

    def unload(self, timeout: float = 300):
        WebDriverWait(self._driver, timeout).until(
            staleness_of(self._node)
        )

    @property
    def children(self):
        return self.elements(Selector.XPATH, './*')

    @property
    def tuples(self):
        return [(child.tag, child.tuples) for child in self.children]

    def screenshot(self, path) -> bool:
        return self._node.screenshot(path)


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
        text = self._node.get_attribute('textContent')
        return text.strip() if text else text

    @property
    def html(self) -> str:
        return self._node.get_attribute('outerHTML')

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
        return ui.Size.of(self._node.location())

    @property
    def position(self):
        return ui.Position.of(self._node.location())

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
        return self._node.get_attribute(item)

    def __eq__(self, node: Node):
        return self._node == node._node

    def __ne__(self, node: Node):
        return self._node != node._node
