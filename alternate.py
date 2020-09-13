import string
from pprint import pprint


strip = lambda s: s.strip()


class Lambda(object):
    def __init__(self, var_name, ast, caller=None):
        self.var_name = var_name
        self.ast = ast
        self.caller = caller

    def __repr__(self):
        if self.caller:
            return f"lambda<{self.var_name}>({self.ast!r})[{self.caller!r}]"
        else:
            return f"lambda<{self.var_name}>({self.ast!r})"


class Var(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"var({self.name})"


class Func(object):
    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"func({self.name}, {', '.join(map(repr, self.args))})"


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


def interpret(s, env, level=0):
    print("#"*(level*2+2), s)
    if s.startswith("<"):
        var_name, rest = s.split(">", 1)

        # Parse body
        body = interpret(rest, env, level=level + 1)

        var_name = var_name[1:].strip()
        end = next_closing_parenthesis(s, len(var_name)+1, open="(", close=")") + 1

        # Parse potential caller
        call_str_rest = s[end:]
        caller = None
        if call_str_rest.lstrip().startswith("["):
            end_bracket = next_closing_parenthesis(s, end, open="[", close="]") + 1
            # Remove [ and ] and then strip
            caller_str = s[end:end_bracket].strip()[1:-1].strip()
            caller = interpret(caller_str, env, level=level+1)

        return Lambda(var_name, body, caller)
    elif s.startswith("("):
        n = next_closing_parenthesis(s, 0, open="(", close=")")
        fun, *args = aware_split(s[1:n])  # maybe this changes envs in the process?
        # print(args)
        return Func(fun, *[interpret(arg, env, level=level+1) for arg in args])
    elif s.startswith("{"):
        n = next_closing_parenthesis(s, 0, open="{", close="}")
        items = [*map(strip, aware_split(s[1:n], ","))]
        # print(items)
        # local_env = dict()
        for item in items:
            ident, body = [ms.strip() for ms in item.split("=", 1)]
            # this could cause trouble with recursion
            env[ident] = interpret(body, env, level=level+1)
        return env
    elif s[0] in string.digits:
        assert all(map(lambda d: d in string.digits, s))
        num = int(s)
        return num
    elif s[0] in string.ascii_lowercase:
        assert s.islower()
        return Var(s)
    else:
        print("UNHANDLED:", s[0])

    # print("+"*30 + "Unreachable" + "+"*30)


pprint(interpret("<x>(* (? {x = 5, b = <y>(+ 7 y)} 0 1) x)[3]", env={}))