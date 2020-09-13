import string


def build_lambda(s, vars):
    var_name, rest = s.split(">", 1)
    print(var_name, rest)
    i = s.find("(")
    level = 1
    while i < len(s):
        if s[i] == "<":
            func, i_advance = build_lambda(s[i:])
            i += i_advance
        elif s[i] in "*/+-":
            pass

        i += 1


def interpret(s):
    i = 0
    while i < len(s):
        if s[i] == "<":
            func, i_advance = build_lambda(s[i:])
            i += i_advance


interpret("<x>(* 5 x)3")