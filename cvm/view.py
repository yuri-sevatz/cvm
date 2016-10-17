#!/usr/bin/env python
from abc import abstractmethod
from inspect import getmembers

from cvm.controller import Selector, Node, Browser


class Content:
    @abstractmethod
    def load(self, node: Node):
        return


class Scope(Content):
    def __init__(self, selector: Selector, value: str):
        self.selector = selector
        self.value = value

    @abstractmethod
    def load(self, node: Node):
        return

    @abstractmethod
    def parse(self, node: Node):
        return


class Group(Content):
    def __init__(self, scope: Scope):
        self.scope = scope

    def load(self, node: Node):
        print("Group.load(): " + str(self.scope.selector) + " " + self.scope.value)
        return [self.scope.parse(element) for element in node.elements(self.scope.selector, self.scope.value)]


class Field(Scope):
    def __init__(self, selector: Selector, value: str):
        super().__init__(selector, value)

    def load(self, node: Node):
        print("Field.load(): " + str(self.selector) + " " + self.value)
        return node.element(self.selector, self.value)

    def parse(self, node: Node):
        return node


class View(Scope):
    def __init__(self, selector: Selector, value: str):
        super().__init__(selector, value)

    def load(self, node: Node):
        print("View.load(): " + str(self.selector) + " " + self.value)
        return self.parse(node.element(self.selector, self.value))

    def parse(self, node: Node):
        return dict((key, content.load(node)) for (key, content) in getmembers(self) if isinstance(content, Content))


class Page:
    def load(self, browser: Browser):
        return dict((key, content.load(browser)) for (key, content) in getmembers(self) if isinstance(content, Content))
