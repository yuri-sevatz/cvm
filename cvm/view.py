#!/usr/bin/env python
from abc import abstractmethod
from inspect import getmembers

from cvm import dom


class Result(dict):
    def __init__(self, *args, **kwargs):
        super(Result, self).__init__(*args, **kwargs)
        self.__dict__ = self


class Content:
    @abstractmethod
    def find(self, node: dom.Node):
        return


class Container:
    def content(self, node: dom.Node):
        return Result((key, content.find(node)) for (key, content) in getmembers(self) if isinstance(content, Content))


class Scope(Content):
    def __init__(self, selector: dom.Selector, value: str):
        self.selector = selector
        self.value = value

    @abstractmethod
    def find(self, node: dom.Node):
        return

    @abstractmethod
    def parse(self, node: dom.Node):
        return


class Group(Content):
    def __init__(self, scope: Scope):
        self.scope = scope

    def find(self, node: dom.Node):
        return [self.scope.parse(element) for element in node.elements(self.scope.selector, self.scope.value)]\
            if node else []


class Field(Scope):
    def __init__(self, selector: dom.Selector, value: str):
        super().__init__(selector, value)

    def find(self, node: dom.Node):
        node = node.element(self.selector, self.value)
        return self.parse(node) if node else None

    def parse(self, node: dom.Node):
        return node


class View(Scope, Container):
    def __init__(self, selector: dom.Selector, value: str):
        super().__init__(selector, value)

    def find(self, node: dom.Node):
        node = node.element(self.selector, self.value)
        return self.parse(node) if node else None

    def parse(self, node: dom.Node):
        return self.content(node)


class Page(Container):
    def get(self, node: dom.Node):
        return self.content(node)
