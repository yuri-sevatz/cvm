#!/usr/bin/env python
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
