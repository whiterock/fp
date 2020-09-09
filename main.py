import string, sys
from pprint import pprint

parens = {
    "(": ")",
    "{": "}"
}


def partition_rec(s, stop_on=None):
    result = []
    i = 0
    buffer = ""
    while i < len(s):
        cc = s[i]
        if cc == stop_on:
            if stripped_buffer := buffer.strip():
                result.append(stripped_buffer)
            return result, i + 1
        elif cc in parens:
            # empty previous buffer if non-empty
            if stripped_buffer := buffer.strip():
                result.append(stripped_buffer)
                buffer = ""

            # recursion here
            a_partition, i_advance = partition_rec(s[i + 1:], stop_on=parens[cc])
            i += i_advance + 1
            result.append(a_partition)
        elif cc == ",":
            if stripped_buffer := buffer.strip():
                result.append(stripped_buffer)
                buffer = ""
            i += 1
        else:
            buffer += cc
            i += 1

    if stripped_buffer := buffer.strip():
        result.append(stripped_buffer)

    return result, i


def partition(s):
    s = s.replace('\n', ' ').replace('\t', ' ')
    part, length = partition_rec(s)
    assert length == len(s)
    return part


def split_my_thing(l):
    for n, item in enumerate(l):
        if type(item) is list:
            l[n] = split_my_thing(item)
        elif type(item) is str and ' ' in item:
            l = item.split()
    return l


environment = {
    'plus': lambda a, b: a + b,
    'minus': lambda a, b: a - b,
    'mult': lambda a, b: a * b,
    'div': lambda a, b: a / b,
    'cond': lambda a, b, c: b if a else c
}


class Lamb:
    def __init__(self, variable_name, body, env):
        self.variable_name = variable_name
        self.body = body
        self.env = env

    def __str__(self):
        return "Lambda: " + self.variable_name + "->" + str(self.body)


def recursive_replace(l, a, b):
    for n, i in enumerate(l):
        if type(i) is list:
            l[n] = recursive_replace(l[n], a, b)
        elif type(i) is str:
            l[n] = i.replace(a, b)
    return l


def evaluate(e, env=environment):
    # print(e)
    if isinstance(e[0], list):
        a = evaluate(e[0], env)
        e[0] = a
        return evaluate(e, env)
    elif isinstance(e[0], str):
        try:
            return int(e[0])
        except:
            pass
        if "->" in e[0]:
            variable_name = e[0][0:e[0].index('->')]
            body = e[1]

            if len(e) >= 3:
                assert len(e) == 3
                called_with = e[2]
                new_body = recursive_replace(body, variable_name, called_with)
                return evaluate(new_body, env)

            return Lamb(variable_name, body, env)
        elif '=' in e[0]:
            # we are in a record
            record = dict()
            for i in range(len(e)):
                if isinstance(e[i], str):
                    var_name, value = e[i].split("=")
                    if not value:
                        record[var_name] = evaluate(e[i+1], env={**env, **record})
                    else:
                        record[var_name] = evaluate(value, env={**env, **record})

            pprint(record)
            return record
        else:
            # function call
            name = e[0]
            if name not in env:
                raise SyntaxError("Error: unrecognised token " + name)
            if name != "cond":
                return env[name](evaluate(e[1]), evaluate(e[2]))
            else:
                return env[name](e[1], e[2], e[3])
    elif isinstance(e[0], Lamb):
        # call lambda
        # try:
        #     called_with = e[1]
        #     new_body = recursive_replace(e[0].body, e[0].variable_name, called_with)
        #     return evaluate(new_body, env)
        # except:
        #     pass
        if len(e) >= 2:
            assert len(e) == 2
            called_with = e[1]
            new_body = recursive_replace(e[0].body, e[0].variable_name, called_with)
            return evaluate(new_body, env)
        else:
            return e[0]


if __name__ == "__main__":
    def debug(s):
        print(s)
        part = partition(s)
        print(part)
        split = split_my_thing(part)
        print(split)
        result = evaluate(split)
        print(result)

    # if len(sys.argv) != 2:
    # 	exit()
    # p = sys.argv[1]
    # test = "{a=5,b={c=3, d=4},e=7}((x->(y->+(* x x)y))2)3"
    # pprint(test)
    # pprint(partition(test)[0])
    # print(partition("((x->(y->(plus(mult x x)y))2)3"))

    print(partition("{a=5,b={c=3, d=4},e=7}((x->(y->+(* x x)y))2)3"))
    print(evaluate(split_my_thing(partition("((x->(y->(plus(mult x x)y))2)3")[0])))

    debug("{a=5,b={c=3, d=4},e=7}((x->(y->+(* x x)y))2)3")
    debug("""   
    (x->
        (y->
            (
                plus(mult x 2)(mult y y)
            )
        )1
    )4
    """)
