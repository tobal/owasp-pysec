# Python Security Project (PySec) and its related class files.
#
# PySec is a set of tools for secure application development under Linux
#
# Copyright 2014 PySec development team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -*- coding: ascii -*-
"""Module to make checkers.

from pysec.expr import var

a, b = var.a, var.b


@check(
    a.__int__,
    a > 1,
    a + b != 10,
    a * b < a / b
)
def foo(a, b):
    ...


@check(
    # first check
    (a > 1,
     a + b != 10,
     a * b < a / b),
     # second check (if first fails)
     # parsers
    a=int,
    b=float
)
def foo(a, b):
    ...
"""
import inspect

from pysec.core import Object, Error
from pysec.expr import Expression


NO_CHECK = Object()


class CheckError(Error):
    pass


class CheckRuleError(Error, ValueError):

    def __init__(self, check, values):
        self.check = check
        self.values = values

    def __str__(self):
        return str(self.check)


def do_check(check, value):
    raise NotImplementedError


def check(*rules, **parsers):
    def _check(func):
        def __check(*args, **kwds):
            kwds = inspect.getcallargs(func, *args, **kwds)
            for name, parse in parsers.iteritems():
                kwds[name] = parse(kwds[name])
            for rule in rules:
                if isinstance(rule, Expression):
                    if not rule.compute(**kwds):
                        raise CheckError(rule, kwds)
                elif isinstance(rule, tuple):
                    for rl in rule:
                        if isinstance(rl, Expression):
                            if not rl.compute(**kwds):
                                raise CheckError(rl, kwds)
                        else:
                            raise TypeError("wrong subrule's type %r" % type(rl))
                else:
                    raise TypeError("wrong rule's type %r" % type(rule))
            return func(**kwds)
        return __check
    return _check