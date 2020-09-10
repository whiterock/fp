import string, sys, re, copy
from pprint import pprint

parens = {
    "(": ")",
    "{": "}"
}

def next_char(e, i):
    while e[i] in string.whitespace:
        i += 1
    return i

def next_closing_parenthesis(e, i):
    level = 0
    while i < len(e):
        if e[i] == ')' and level == 0: return i
        if e[i] == '(': level += 1
        if e[i] == ')': level -= 1
        i+=1
    assert(1==2)

def add_parentheses(e):
    k = 0
    for i in [m.start()+2 for m in re.finditer('->', e)]:
        if e[next_char(e,i+k)] != '(':
            j = next_closing_parenthesis(e,i+k)
            e = e[:i+k] + '(' + e[i+k:j] + ')' + e[j:]
            k+=1
    return e

def parse(e):
    e = e.replace(',', ',)').replace('=', '=(').replace('}', ')}')
    e = add_parentheses(e)
    if e[0] != '(' or e[-1] != ')': e = '(' + e + ')'
    if '}' in e:
        i = e.rfind('}')+1
        if i < len(e)-1: e = e[:i] + '(' + e[i:] + ')'
    e = e.replace('(', ' ( ').replace(')', ' ) ').replace('{', ' { ').replace('}', ' } ').replace(',', ' ').replace('=', '= ').replace('\n', ' ').replace('\t', ' ').split()
    return parse_tokens(e)

def parse_tokens(e):
    t = e.pop(0)
    if t == '{':
        r = []
        while e[0] != '}':
            r.append(parse_tokens(e))
        e.pop(0)
        return r
    elif t == '(':
        r = []
        while e[0] != ')':
            r.append(parse_tokens(e))
        e.pop(0)
        return r
    else:
        try: return int(t)
        except: return t



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

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Lambda: " + self.variable_name + "->" + str(self.body)


def recursive_replace(l, a, b):
    for n, i in enumerate(l):
        if type(i) is list:
            l[n] = recursive_replace(l[n], a, b)
        elif type(i) is str and i == a:
            l[n] = b
    return l


def evaluate_new(e, env=environment):
    print(e)
    if isinstance(e, list) and len(e) == 1:
        return evaluate_new(e[0], env)
    if isinstance(e, str):
        if '->' in e:
            return e[0:e.index('->')]
        elif e in env and e not in environment:
            return env[e]
        return
    if isinstance(e, list) and len(e) == 2:
        try: #NOTE: this is how i set the environment rn :/
            if '=' in e[0][0]: #is there a more general rule
                new_env = evaluate_new(e[0], env) #this feels hacks
                return evaluate_new(e[1], {**env, **new_env})
        except:
            pass
    if isinstance(e, int) or isinstance(e, Lamb) or isinstance(e, dict):
        return e
    if isinstance(e[0], Lamb) and isinstance(e[1], int):
        body_copy = copy.deepcopy(e[0].body)
        new_body = recursive_replace(body_copy, e[0].variable_name, e[1])
        return evaluate_new([evaluate_new(new_body, env)] + e[2:], env)
    if isinstance(e[0], str):
        if '->' in e[0]:
            variable_name = evaluate_new(e[0])
            body = e[1]
            return Lamb(variable_name, body, env)
        elif e[0] in environment:
            if len(e) == 3:
                return environment[e[0]](evaluate_new(e[1], env), evaluate_new(e[2], env))              
            #TODO: handle cond. decide whether to do so separately 
        elif '=' in e[0]:
            assert len(e)%2 == 0
            r = {}
            for i in range(0, len(e), 2):
                name = e[i][:-1]
                value = evaluate_new(e[i+1], {**env, **r})
                r[name] = value
            return r
    if isinstance(e, list):
        a = []
        for b in e:
            a.append(evaluate_new(b, env))
        return evaluate_new(a)


def evaluate(e, env=environment):
    if isinstance(e[0], list):
        a = evaluate(e[0], env)
        e[0] = a
        return evaluate(e, env)
    elif isinstance(e[0], str):
        try:
            return int(e[0])
        except:
            pass
        if '=' in e[0]:
            # we are in a record
            record = dict()
            i = 0
            while i < len(e):
                if isinstance(e[i], str):
                    var_name, value = e[i].split("=")
                    if '->' not in value:
                        if not value:
                            record[var_name] = evaluate(e[i+1], env={**env, **record})
                        else:
                            record[var_name] = evaluate(value, env={**env, **record})
                        i += 1
                    else:
                        variable_name = value[0:value.index('->')]
                        body = e[i+1]
                        # TODO: Handle when function is called immediately
                        record[var_name] = Lamb(variable_name, body, {**env, **record})
                        i += 2
                else:
                    i += 1

            pprint(record)
            return record
        elif "->" in e[0]:
            variable_name = e[0][0:e[0].index('->')]
            body = e[1]

            if len(e) >= 3:
                assert len(e) == 3
                called_with = e[2]
                new_body = recursive_replace(body, variable_name, called_with)
                return evaluate(new_body, env)

            return Lamb(variable_name, body, env)
        else:
            # function call
            name = e[0]
            if name not in env:
                raise SyntaxError("Error: unrecognised token " + name + ", env=" + str(env))
            if name in environment:
                if name != "cond":
                    return env[name](evaluate(e[1], env=env), evaluate(e[2], env=env))
                else:
                    return env[name](e[1], e[2], e[3])
            # if we are dealing with a record item
            else:
                return env[name]
    elif isinstance(e[0], dict):
        if len(e) == 3:
            # fixme: no argument? where can records arise?
            # fixme: multiple arguments
            # {.....}()arg
            # variables defined in the record are not available to use in `arg`. bug or feature?
            func = evaluate(e[1], {**env, **e[0]})
            called_with = e[2]
            new_body = recursive_replace(func.body, func.variable_name, called_with)
            print(e)
            return evaluate(new_body, {**env, **e[0]})
        else:
            SystemError("Not supposed to be called like that" + repr(e))
    elif isinstance(e[0], Lamb):
        # call lambda
        if len(e) >= 2:
            print(list(map(str, e)))
            assert len(e) == 2
            called_with = e[1]
            new_body = recursive_replace(e[0].body, e[0].variable_name, called_with)
            return evaluate(new_body, env)
        else:
            return e[0]


if __name__ == "__main__":
    def debug(s):
        print("Input str: ", s)
        part = partition(s)
        print("Partition: ", part)
        split = split_my_thing(part)
        print("Split str: ", split)
        result = evaluate(split)
        print("F. result: ", result)

    # if len(sys.argv) != 2:
    #   exit()
    # p = sys.argv[1]
    # test = "{a=5,b={c=3, d=4},e=7}((x->(y->+(* x x)y))2)3"

    #check this out :)
    # print(evaluate_new(parse("(x->y->plus(mult x x)y) 2 3")))
    # print(evaluate_new(parse("((x->(y->plus(mult x x)y))2)3")))
    # print(evaluate_new(parse("{a=x->y->plus(mult x x)y, b=a 2, c=b 3}")))

    assert(evaluate_new(parse("(x->y->plus(mult x x)y) 2 3")) == 7)
    assert(evaluate_new(parse("((x->(y->plus(mult x x)y))2)3")) == 7)
    assert(evaluate_new(parse("minus ((y->plus(mult 2 2)y)5)7")) == 2)
    assert(evaluate_new(parse("{a=x->y->plus(mult x x)y, b=a 2, c=b 3}minus(b 5)c")) == 2)
 
    print(evaluate_new(parse("{fac=x->(cond x (mult x(fac (minus x 1))) 1)} fac 4")))

    #print()
    #debug("{fac=x->(cond x (mult x(fac (minus x 1))) 1)} fac 4")

    # print(evaluate_new(parse("""   
    # (x->
    #     (y->
    #         (
    #             plus(mult x 2)(mult y y)
    #         )
    #     )1
    # )4
    # """)))



