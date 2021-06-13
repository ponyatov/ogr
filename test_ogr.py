from ogr import *
import pytest

def test_any(): assert True

class TestObject:

    def test_hello(self):
        hello = Object("Hello")
        world = Object("World")
        left = Object('left')
        right = Object('right')
        assert hello.test() == '\n<object:Hello>'
        assert world.test() == '\n<object:World>'
        dump = \
            '\n<object:Hello>' +\
            '\n\tobject = <object:left>' +\
            '\n\tright = <object:right>' +\
            '\n\t0: <object:World>'
        assert (hello // world << left >> right).test() == dump
        assert hello.test() == dump

class TestNumbers:

    def test_num(self):
        num = Num(-01.20)
        assert num.test() == '\n<num:-1.2>'
        assert num.eval(glob).test() == '\n<num:-1.2>'

    def test_int(self):
        num = Int(-01.20)
        assert num.test() == '\n<int:-1>'
        assert num.eval(glob).test() == '\n<int:-1>'

class TestActive:

    def test_env(self):
        assert glob.head(test=True) == '<env:global>'
        assert glob['env'].head(test=True) == '<env:global>'
        assert glob['global'].head(test=True) == '<env:global>'

    def test_fn_eval(self):
        noop = glob['noop']
        assert noop.test() == '\n<fn:noop>'
        assert noop.eval(glob).test() == '\n<fn:noop>'

    def test_atom(self):
        noop = Atom('noop')
        assert noop.test() == '\n<atom:noop>'
        assert noop.eval(glob).test() == '\n<fn:noop>'

    def test_quote(self):
        quoted = Quote() // Atom('atom')
        assert quoted.test() == '\n<op:`>\n\t0: <atom:atom>'
        assert quoted.eval(glob).test() == '\n<atom:atom>'
