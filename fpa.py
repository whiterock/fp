import string, sys
from copy import deepcopy
from functools import reduce
from pprint import pprint


strip = lambda s: s.strip()
DEBUG = True


class Lambda(object):
    def __init__(self, var_obj, ast):
        self.var_obj = var_obj
        self.ast = ast

    def __repr__(self):
        return f"λ<{self.var_obj!r}>({self.ast!r})"

    def eval(self, call_stack=None, env=None, level=0):
        if call_stack:
            # this does recursive replace in the ast
            top = call_stack.pop(0)
            if DEBUG:
                print(" |" * level + " =", f"Evaluating {self.ast!r} with {self.var_obj!r}")
            self.var_obj.value = top.eval(None, env, level=level + 1)
            return self.ast.eval(call_stack, env, level=level + 1)
        else:
            return self


class Var(object):
    def __init__(self, name):
        self.name = name
        self.value = None

    def __repr__(self):
        if self.value:
            return f"var(\u001b[31m{self.name}\u001b[0m @ {id(self) & 0xffff:04x} = {self.value})"
        else:
            return f"var(\u001b[31m{self.name}\u001b[0m @ {id(self) & 0xffff:04x})"

    def eval(self, call_stack, env, level=0):
        assert not call_stack
        return self.value


class Ident(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"\u001b[33m{self.name}\u001b[0m"

    def eval(self, call_stack, env, level=0):
        if DEBUG:
            print(" |" * level + " =", "Fetching", repr(self), "from", env)
        if not call_stack:
            return deepcopy(env[self.name])
        else:
            return deepcopy(env[self.name]).eval(call_stack, env, level=level + 1)


class Call(object):
    def __init__(self, callee, *args):
        self.callee = callee
        self.args = args

    def __repr__(self):
        return f"call({self.callee}, {', '.join(map(repr, self.args))})"

    def eval(self, call_stack=None, env=None, level=0):
        if isinstance(self.callee, BuiltInOp):
            assert not call_stack
            # call_stack = [arg.eval(None, env, level=level + 1) for arg in self.args]
            call_stack = self.args
            if DEBUG:
                print(" |" * level + " =", "Calling", self.callee, "with", call_stack)
            return self.callee.eval(call_stack, env, level=level + 1)
        elif isinstance(self.callee, Lambda) or isinstance(self.callee, Call):
            if not call_stack:
                call_stack = []
            # call_stack = [*[arg.eval(None, env, level=level + 1) for arg in self.args], *call_stack]
            call_stack = [*self.args, *call_stack]
            if DEBUG:
                print(" |" * level + " =", "Calling", self.callee, "with", call_stack)
            return self.callee.eval(call_stack, env, level=level + 1)
        elif isinstance(self.callee, Env):
            assert len(self.args) == 1
            if DEBUG:
                print(" |" * level + " =", "Let", self.args[0], "in", self.callee)
            new_env = self.callee.eval(None, env=env, level=level + 1)
            return self.args[0].eval(call_stack, env=new_env, level=level + 1)
        elif isinstance(self.callee, Ident) or isinstance(self.callee, Var):
            if not call_stack:
                call_stack = []
            # call_stack = [*[arg.eval(None, env, level=level + 1) for arg in self.args], *call_stack]
            call_stack = [*self.args, *call_stack]
            if DEBUG:
                print(" |" * level + " =", "Calling", repr(self.callee), "with", call_stack)
            resolved_identifier = self.callee.eval(None, env, level=level + 1)
            # pass it here so assert in Env holds.
            new_call = Call(resolved_identifier, *call_stack)
            return new_call.eval(None, env, level=level + 1)
            # return resolved_identifier.eval(call_stack, env, level=level + 1)
        else:
            # this is tricky
            # we should probably construct a new call obj here with resolved as callee
            raise SyntaxError()
        # elif isinstance(self.callee, Var):
        #     if not call_stack:
        #         call_stack = []
        #     # call_stack = [*[arg.eval(None, env, level=level + 1) for arg in self.args], *call_stack]
        #     call_stack = [*self.args, *call_stack]


class Env(dict):
    def eval(self, call_stack=None, env=None, level=0):
        assert not call_stack
        if not env:
            env = {}
        for key, item in self.items():
            if DEBUG:
                print(" |" * level + " =", f"Setting key {key} with {item}")
            self[key] = item.eval(None, env={**env, **self}, level=level + 1)

        return self


class BuiltInOp(object):
    def __init__(self, op):
        self.op = op

    def __repr__(self):
        return f"\u001b[33m{self.op}\u001b[0m"

    def eval(self, call_stack, env, level=0):
        if DEBUG:
            print(" |" * level + " =", "Operator", repr(self), "called with", call_stack)
        if self.op == "*":
            return Integer(reduce(lambda x, y: x*y, map(lambda c: c.eval(None, env, level=level + 1), call_stack)))
        elif self.op == "+":
            return Integer(sum(map(lambda c: c.eval(None, env, level=level + 1), call_stack)))
        elif self.op == "/":
            assert len(call_stack) == 2
            return Integer(call_stack[0].eval(None, env, level=level + 1) / call_stack[1].eval(None, env, level=level + 1))
        elif self.op == "-":
            assert len(call_stack) == 2
            return Integer(call_stack[0].eval(None, env, level=level + 1) - call_stack[1].eval(None, env, level=level + 1))
        elif self.op == "?":
            assert len(call_stack) == 3
            # Lazy eval
            if call_stack[0].eval(None, env, level=level + 1):
                return call_stack[1].eval(None, env, level=level + 1)
            else:
                return call_stack[2].eval(None, env, level=level + 1)


class Integer(int):
    # def __init__(self, num):
    #    self.num = num

    def __repr__(self):
        return f"\u001b[32mi'{self:d}\u001b[0m"

    def eval(self, call_stack, env, level=0):
        if DEBUG:
            print(" |" * level + " =", "Retrieving", self)
        assert not call_stack
        return self #.num


def next_closing_parenthesis(s, i, open, close):
    level = 0
    while i < len(s):
        if s[i] == close:
            level -= 1
            if level == 0:
                return i
        elif s[i] == open:
            level += 1

        i += 1
    # should not be reached
    raise SyntaxError(f"Unbalanced parenthesis '{open}' '{close}' at {i}")


def aware_split(s, on=string.whitespace):
    items = []
    buffer = ""
    level = 0
    for c in s:
        if c in on and level == 0:
            if buffer:
                items.append(buffer)
                buffer = ""
        else:
            if c in {'(', '{'}:
                level += 1
            elif c in {')', '}'}:
                level -= 1
            buffer += c
    if buffer:
        items.append(buffer)
    return items


def parse_recursively(s, vars, level=0):
    if DEBUG:
        print("#"*(level*2+2), s)
    if s.startswith("<"):
        var_name, rest = s.split(">", 1)
        var_name = var_name[1:].strip()
        var_obj = Var(var_name)
        vars[var_name] = var_obj

        # Parse body
        body = parse_recursively(rest, vars=vars, level=level + 1)

        return Lambda(var_obj, body)
    elif s.startswith("("):
        n = next_closing_parenthesis(s, 0, open="(", close=")")
        first, *args = aware_split(s[1:n])  # maybe this changes envs in the process?
        if args:
            callee = parse_recursively(first, vars=vars, level=level + 1)
            params = [parse_recursively(arg, vars=vars, level=level + 1) for arg in args]
            return Call(callee, *params)
        else:
            return parse_recursively(first, vars=vars, level=level + 1)  # omitting + 1 is a style pref.
        # return Func(fun, *[parse(arg, env, vars=vars, level=level + 1) for arg in args])
    elif s.startswith("{"):
        n = next_closing_parenthesis(s, 0, open="{", close="}")
        items = [*map(strip, aware_split(s[1:n], ","))]

        env = Env()
        for item in items:
            ident, body = [ms.strip() for ms in item.split("=", 1)]
            env[ident] = parse_recursively(body, vars=vars, level=level + 1)
        return env
    elif all(map(lambda d: d in string.digits, s)):
        num = int(s)
        return Integer(num)
    elif all(map(lambda c: c in string.ascii_lowercase, s)):
        assert s.islower()
        if s in vars:
            return vars[s]
        else:
            return NameError(f"var({s}) has not been passed.")
    elif all(map(lambda c: c in string.ascii_uppercase, s)):
        return Ident(s)
    elif s in "*/+-?":
        return BuiltInOp(s)
    else:
        raise SyntaxError(f"Unexpected symbol {s}, {ord(s)}")


def parse(s):
    return parse_recursively(s.replace("\n", " ").replace("\t", " "), vars={})


def parse_and_eval(s):
    parsed = parse(s)
    if DEBUG:
        print("Parsing", s)
        pprint(parsed)
        print("Evaluating...")
    evaluated = parsed.eval()
    pprint(evaluated)


tests = True
if tests:
    assert parse("(+ 5 (* 3 9))").eval() == 32
    assert parse("(((+ 5 ((((* ((3)) 9)))))))").eval() == 32
    assert parse("(<x>(* 5 x) 3)").eval() == 15
    assert parse("(<y>(<x>(- y x)) 5 3)").eval() == 2
    assert parse("(<y>(((<x>(- y x)))) 3 5)").eval() == -2
    assert parse("((<y>(<x>(- y x)) 5) 3)").eval() == 2
    assert parse("((<y>(<x>(- y x)) 3) 5)").eval() == -2
    assert parse("({A = 5, B = <x>(+ A x)} (B 11))").eval() == 16
    assert parse("({A = 5, B = <x>(+ A x)} (B A))").eval() == 10
    assert parse("({FAC=<x>(? x (* x (FAC (- x 1))) 1)} (FAC 4))").eval() == 24
    assert parse("(({FAC=<x>(? x (* x (FAC (- x 1))) 1)} FAC) 4)").eval() == 24
    assert parse("({A=8, B={C=3}} (B C))").eval() == 3
    assert parse("(<x>(x A) {A=5})").eval() == 5

# print("-- TEST BED --")
# "<x>(* (? {A = x, B = <y>(+ A y)} 0 1) x)"
#pprint(parse("(<x>(* (? {x = 5, b = (x <y>(+ 7 y))} 0 1) x) 3)", env={}, vars={}))
#pprint(parse("(<x>(<y>(* x y)) 3 2)", env={}, vars={}))
#parse_and_eval("(<x>(* 5 x) 3)")

#parse_and_eval("({A = 5, B = <x>(+ A x)} (B A))")

# sys.setrecursionlimit(100)

# gen 0 -> {}
# gen 1 ->
# x->cond x (append(gen(minus x 1)) {head=x, tail={}}) {}
# cond 1 (append(gen(minus 11)) {head=1, tail={}}) {}
# (append(gen(minus 11)) {head=1, tail={}})
# (append(gen(0)) {head=1, tail={}})
# (append {} {head=1, tail={}})
# {head=1, tail={}}

if len(sys.argv) != 2:
    print("Please provide a file name to open!")
    exit()
p = sys.argv[1]
with open(p, "r") as fh:
    parse_and_eval(fh.read())

#parse_and_eval("({APPEND=<x>(<y>(? x {HEAD=(x HEAD), TAIL=(APPEND (x TAIL) y)} y)), GEN=<x>(? x (APPEND (GEN (- x 1)) {HEAD=x, TAIL={}}) {})} (GEN 3))")
# 

#parse_and_eval("((<y>(<x>(- y x)) 5) 3)")