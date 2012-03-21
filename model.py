from random import randint

class Model (object):
    def __init__(self, a = 0, b = 0, c = 0):
        self.a = a
        self.b = b
        self.c = c
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def changed(self):
        for o in self.observers:
            o.update(self)

    def set_a(self, a):
        if (a >= 0):
            self.a = a
            self.changed()

    def set_b(self, b):
        if (b >= 0):
            self.b = b
            self.changed()

    def set_c(self, c):
        if (c >= 0):
            self.c = c 
            self.changed()

    def set(self, a, b, c):
        if (a >= 0):
            self.a = a
        if (b >= 0):
            self.b = b
        if (c >= 0):
            self.c = c
        self.changed()
        
    def random(self):
        self.a, self.b, self.c = [randint(0,300) for i in range(3)]
        self.changed()
