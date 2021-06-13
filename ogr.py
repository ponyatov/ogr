#!./bin/python3
## @file

import config

import os, sys, time, re
import datetime as dt

## Abstract Syntax (hyper)Graph node = Minsky's Frame
class Object:
    def __init__(self, V):
        ## scalar value: name, string, number,..
        self.value = V
        ## associative array: map = env/namespace = attributes
        self.slot = {}
        ## ordered container: vector = stack = queue = AST subtree
        self.nest = []
        ## select & differ equal objects by global id
        self.gid = f' @{id(self):x}'

    ## Python types wrapper
    def box(self, that):
        if isinstance(that, Object): return that
        raise TypeError(['box', type(that), that])

    ## @name text dump

    ## `print` callback
    def __repr__(self):
        return self.dump(test=False)

    ## test w/o gid
    def test(self):
        return self.dump(test=True)

    ## full text tree dump
    def dump(self, cycle=[], depth=0, prefix='', test=False):
        # head
        ret = self.pad(depth) + self.head(prefix, test)
        # block cycles
        if not depth: cycle = []
        if self in cycle: return ret + ' _/'
        else: cycle.append(self)
        # slot{}s
        for i in self.keys():
            ret += self[i].dump(cycle, depth + 1, f'{i} = ', test)
        # nest[]ed
        for j, k in enumerate(self.nest):
            ret += k.dump(cycle, depth + 1, f'{j}: ', test)
        # subgraph
        return ret

    ## tree tab padding
    def pad(self, depth):
        return '\n' + '\t' * depth

    ## short `<T:V>` header
    def head(self, prefix='', test=False):
        gid = '' if test else self.gid
        return f'{prefix}<{self.tag()}:{self.val()}>{gid}'

    ## `<T:` type/class tag
    def tag(self):
        return self.__class__.__name__.lower()

    ## `:V>` value as string
    def val(self):
        return f'{self.value}'

    ## @name operator

    ## `A.keys()`
    def keys(self):
        return sorted(self.slot.keys())

    ## `len(A)`
    def __len__(self):
        return len(self.nest)

    ## `bool(A)`
    def __bool__(self):
        raise NotImplementedError(['bool', self.head()])

    ## `A[key]`
    def __getitem__(self, key):
        assert isinstance(key, str)
        return self.slot[key]

    ## `A[key] = B`
    def __setitem__(self, key, that):
        assert isinstance(key, str)
        that = self.box(that)
        self.slot[key] = that; return self

    ## `A << B -> A[B.type] = B`
    def __lshift__(self, that):
        that = self.box(that)
        return self.__setitem__(that.tag(), that)

    ## `A >> B -> A[B.value] = B`
    def __rshift__(self, that):
        that = self.box(that)
        return self.__setitem__(that.val(), that)

    ## `A // B -> A.push(B)`
    def __floordiv__(self, that):
        that = self.box(that)
        self.nest.append(that); return self

    ## @name evaluate

    ## evaluate in environment
    def eval(self, env):
        raise NotImplementedError(['eval', self.head()])

    ## apply to `that`
    def apply(self, env, that):
        raise NotImplementedError(['apply', self.head(), that.head()])


class Primitive(Object):

    ## evaluates to itself
    def eval(self, env):
        return self

## unique symbolic name
class Atom(Primitive):

    ## evaluates via lookup
    def eval(self, env):
        return env[self.val()]

## source code string /nested tree/
class S(Primitive):
    pass

## floating point number
class Num(Primitive):
    def __init__(self, N):
        Primitive.__init__(self, float(N))

## integer number
class Int(Num):
    def __init__(self, N):
        Primitive.__init__(self, int(N))

## boolean
class Bool(Primitive):
    def __bool__(self):
        if self.value == 'T': return True
        elif self.value == 'F': return False
        else:
            raise TypeError(['bool', self.val()])

true = Bool('T')
false = Bool('F')


## data container
class Container(Object):
    pass

## ordered container
class Vector(Container):
    pass

## associative array
class Map(Container):
    pass


## minimal input/output (only for code generation)
class IO(Object):
    pass

class Dir(IO):
    pass

class File(IO):
    pass


## Executable Data Structure (c)
class Active(Object):
    pass

## environment = namespace
class Env(Active, Map):
    pass

glob = Env('global'); glob << glob >> glob

## operator
class Op(Active):
    def tag(self): return 'op'

class Quote(Op):
    def __init__(self):
        super().__init__('`')

    def eval(self, env):
        assert len(self) == 1; return self.nest[0]

class If(Op):
    def __init__(self):
        super().__init__('')

    def tag(self):
        return Object.tag(self)

    def eval(self, env):
        assert len(self) == 3
        if self.nest[0].eval(glob):
            return self.nest[1].eval(glob)
        else:
            return self.nest[2].eval(glob)

## function
class Fn(Active):
    def __init__(self, F, *args):
        if callable(F):
            super().__init__(F.__name__)
            self.fn = F
        else:
            super().__init__(F)
        for i in args: self[i] = Nil()

    def eval(self, env):
        return self

def quit(env=glob, that=Int(0)):
    os._exit(int(that.value))

glob \
    >> Fn(quit) \
    >> Fn('noop')

# \ system init
print(glob)
# / system init
