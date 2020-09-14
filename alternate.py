import string
from copy import deepcopy
from pprint import pprint


strip = lambda s: s.strip()


class Lambda(object):
    def __init__(self, var_name, ast):
        self.var_name = var_name
        self.ast = ast

    def __repr__(self):
        return f"lambda<{self.var_name!r}>({self.ast!r})"


class Var(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"var({self.name} at 0x{id(self):08x})"


class Call(object):
    def __init__(self, callee, *args):
        self.callee = callee
        self.args = args

    def __repr__(self):
        return f"call({self.callee}, {', '.join(map(repr, self.args))})"


class BuiltInOp(object):
    def __init__(self, op):
        self.op = op

    def __repr__(self):
        return f"op({self.op})"


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


def parse(s, env, vars, level=0):
    print("#"*(level*2+2), s)
    if s.startswith("<"):
        var_name, rest = s.split(">", 1)
        # end = next_closing_parenthesis(s, len(var_name) + 1, open="(", close=")") + 1

        var_name = var_name[1:].strip()
        var_obj = Var(var_name)
        vars[var_name] = var_obj

        # Parse body
        body = parse(rest, env, vars=vars, level=level + 1)

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
            callee = parse(first, env, vars=vars, level=level + 1)
            params = [parse(arg, env, vars=vars, level=level + 1) for arg in args]
            return Call(callee, *params)
        else:
            return parse(first, env, vars=vars, level=level + 1)
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
            new_env[ident] = parse(body, new_env, vars=vars, level=level + 1)
        return new_env
    elif s[0] in string.digits:
        assert all(map(lambda d: d in string.digits, s))
        num = int(s)
        return num
    elif s[0] in string.ascii_lowercase:
        assert s.islower()
        if s in vars:
            return vars[s]
        else:
            return NameError(f"var({s}) has not been passed.")
    elif s in "*/+-?":
        return BuiltInOp(s)
    else:
        print("UNHANDLED:", s[0])

    # print("+"*30 + "Unreachable" + "+"*30)


# "<x>(* (? {x = 5, b = <y>(+ 7 y)} 0 1) x)[3]"
pprint(parse("(<x>(* (? {x = 5, b = <y>(+ 7 y)} 0 1) x) 3)", env={}, vars={}))
pprint(parse("(<x>(<y>(* x y)) 3 2)", env={}, vars={}))