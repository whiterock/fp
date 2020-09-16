import string
from copy import deepcopy
from functools import reduce
from pprint import pprint


strip = lambda s: s.strip()


class Lambda(object):
    def __init__(self, var_obj, ast):
        self.var_obj = var_obj
        self.ast = ast

    def __repr__(self):
        return f"lambda<{self.var_obj!r}>({self.ast!r})"

    def eval(self, call_stack=None, env=None, level=0):
        if call_stack:
            # this does recursive replace in the ast
            self.var_obj.value = call_stack.pop(0)
            print("=" * (level * 2 + 2), f"Evaluating {self.ast!r} with {self.var_obj!r}")
            return self.ast.eval(call_stack, env, level=level + 1)
        else:
            return self


class Var(object):
    def __init__(self, name):
        self.name = name
        self.value = None

    def __repr__(self):
        if self.value:
            return f"var({self.name} at 0x{id(self):08x} = {self.value})"
        else:
            return f"var({self.name} at 0x{id(self):08x})"

    def eval(self, call_stack, env, level=0):
        assert not call_stack
        return self.value


class Ident(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"ident({self.name})"

    def eval(self, call_stack, env, level=0):
        return env[self.name]


class Call(object):
    def __init__(self, callee, *args):
        self.callee = callee
        self.args = args

    def __repr__(self):
        return f"call({self.callee}, {', '.join(map(repr, self.args))})"

    def eval(self, call_stack=None, env=None, level=0):
        if isinstance(self.callee, BuiltInOp):
            assert not call_stack
            call_stack = [arg.eval(None, env, level=level + 1) for arg in self.args]
            print("=" * (level * 2 + 2), "Calling", self.callee, "with", *call_stack)
            return self.callee.eval(call_stack, env, level=level + 1)
        elif isinstance(self.callee, Lambda) or isinstance(self.callee, Call):
            if not call_stack:
                call_stack = []
            call_stack = [*[arg.eval(None, env, level=level + 1) for arg in self.args], *call_stack]
            print("=" * (level * 2 + 2), "Calling", self.callee, "with", call_stack)
            return self.callee.eval(call_stack, env, level=level + 1)
        elif isinstance(self.callee, Env):
            new_env = deepcopy(env)  # todo: potential error?
            if not new_env:
                new_env = Env()
            new_env.update(self.callee.eval(call_stack, env=env, level=level + 1))
            assert len(self.args) == 1  # q: is this right?
            print("=" * (level * 2 + 2), "Let", self.args[0], "in", new_env)
            return self.args[0].eval(call_stack, env=new_env, level=level + 1)
        elif isinstance(self.callee, Ident):
            if not call_stack:
                call_stack = []
            call_stack = [*[arg.eval(None, env, level=level + 1) for arg in self.args], *call_stack]
            print("=" * (level * 2 + 2), "Calling", self.callee, "with", call_stack)
            resolved_identifier = self.callee.eval(None, env, level=level + 1)
            return resolved_identifier.eval(call_stack, env, level=level + 1)
            # for arg in self.args:
            #     resolved_arg = arg.eval()
            #     print("=" * (level * 2 + 2), "Calling", result, "with", resolved_arg)
            #     if isinstance(result, Lambda):
            #         result = result.eval(resolved_arg, level=level + 1)
            # return result


class Env(dict):
    def eval(self, call_stack=None, env=None, level=0):
        for key, item in self.items():
            self[key] = item.eval(None, env=self, level=level + 1)

        return self


class BuiltInOp(object):
    def __init__(self, op):
        self.op = op

    def __repr__(self):
        return f"op({self.op})"

    def eval(self, call_stack, env, level=0):
        print("=" * (level*2+2), self.op, *call_stack)
        if self.op == "*":
            return reduce(lambda x, y: x*y, call_stack)
        elif self.op == "+":
            return sum(call_stack)
        elif self.op == "/":
            assert len(call_stack) == 2
            return call_stack[0] / call_stack[1]
        elif self.op == "-":
            assert len(call_stack) == 2
            return call_stack[0] - call_stack[1]
        elif self.op == "?":
            assert len(call_stack) == 3
            return call_stack[1] if call_stack[0] else call_stack[2]


class Integer(object):
    def __init__(self, num):
        self.num = num

    def __repr__(self):
        return f"i'{self.num}"

    def eval(self, call_stack, env, level=0):
        assert not call_stack
        return self.num


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
        if c in on and level == 0 and buffer:
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


def parse_recursively(s, env, vars, level=0):
    print("#"*(level*2+2), s)
    if s.startswith("<"):
        var_name, rest = s.split(">", 1)
        # end = next_closing_parenthesis(s, len(var_name) + 1, open="(", close=")") + 1

        var_name = var_name[1:].strip()
        var_obj = Var(var_name)
        vars[var_name] = var_obj

        # Parse body
        body = parse_recursively(rest, env, vars=vars, level=level + 1)

        # Parse potential caller
        # call_str_rest = s[end:]
        # caller = None
        # if call_str_rest.lstrip().startswith("["):
        #     end_bracket = next_closing_parenthesis(s, end, open="[", close="]") + 1
        #     # Remove [ and ] and then strip
        #     caller_str = s[end:end_bracket].strip()[1:-1].strip()
        #     caller = parse(caller_str, env, vars=vars, level=level + 1)

        return Lambda(var_obj, body)
    elif s.startswith("("):
        n = next_closing_parenthesis(s, 0, open="(", close=")")
        first, *args = aware_split(s[1:n])  # maybe this changes envs in the process?
        if args:
            callee = parse_recursively(first, env, vars=vars, level=level + 1)
            params = [parse_recursively(arg, env, vars=vars, level=level + 1) for arg in args]
            return Call(callee, *params)
        else:
            return parse_recursively(first, env, vars=vars, level=level + 1)  # omitting + 1 is a style pref.
        # return Func(fun, *[parse(arg, env, vars=vars, level=level + 1) for arg in args])
    elif s.startswith("{"):
        # FIXME: Check if called later in a (...) as in {...}()
        n = next_closing_parenthesis(s, 0, open="{", close="}")
        items = [*map(strip, aware_split(s[1:n], ","))]
        # print(items)

        # q: is this the right way to go about this?
        new_env = deepcopy(env)
        for item in items:
            ident, body = [ms.strip() for ms in item.split("=", 1)]
            # q: this could cause trouble with recursion ?
            # a: as I see it now it should be fine as new_env is passed by ref (i think)
            #    so when we evaluate later we should be in the correct "state"
            new_env[ident] = parse_recursively(body, new_env, vars=vars, level=level + 1)
        return new_env
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
        print("UNHANDLED:", s[0])

    # print("+"*30 + "Unreachable" + "+"*30)


def parse(s):
    return parse_recursively(s, env=Env(), vars={})


def parse_and_eval(s):
    parsed = parse(s)
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

print("-- TEST BED --")
# "<x>(* (? {A = x, B = <y>(+ A y)} 0 1) x)"
#pprint(parse("(<x>(* (? {x = 5, b = (x <y>(+ 7 y))} 0 1) x) 3)", env={}, vars={}))
#pprint(parse("(<x>(<y>(* x y)) 3 2)", env={}, vars={}))
#parse_and_eval("(<x>(* 5 x) 3)")

parse_and_eval("({A = 5, B = <x>(+ A x)} (B A))")

#parse_and_eval("((<y>(<x>(- y x)) 5) 3)")