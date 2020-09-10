import string, sys, re, copy
from pprint import pprint

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
    if '=' in e: e = e.replace(',', ',)').replace('=', '=(').replace('}', ')}')
    e = add_parentheses(e)
    if e[0] != '(' or e[-1] != ')': e = '(' + e + ')'
    if '}' in e and '=' in e:       #TODO: turning { .. }minus(b 5)4 into { .. }(minus(b 5)4) might not be the best way to go about this.
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


def evaluate(e, env=environment):
    print(e)
    if e == []:
        return e
    if isinstance(e, list) and len(e) == 1:
        return evaluate(e[0], env)
    if isinstance(e, str):
        if '->' in e:
            return e[0:e.index('->')]
        elif e in env and e not in environment:
            return env[e]
        return
    if isinstance(e, list) and len(e) == 2:
        try: #NOTE: this is how i set the environment rn :/
            if '=' in e[0][0]: #is there a more general rule
                new_env = evaluate(e[0], env) #this feels hacks
                return evaluate(e[1], {**env, **new_env})
        except:
            pass
    if isinstance(e, int) or isinstance(e, Lamb) or isinstance(e, dict):
        return e
    if isinstance(e[0], Lamb) and isinstance(e[1], int):
        body_copy = copy.deepcopy(e[0].body)
        new_body = recursive_replace(body_copy, e[0].variable_name, e[1])
        return evaluate([evaluate(new_body, env)] + e[2:], env)
    if isinstance(e[0], str):
        if '->' in e[0]:
            variable_name = evaluate(e[0])
            body = e[1]
            return Lamb(variable_name, body, env)
        elif e[0] in environment:
            if len(e) == 3:
                return environment[e[0]](evaluate(e[1], env), evaluate(e[2], env))              
            if e[0] == 'cond' and len(e) == 4:
                c = evaluate(e[1])
                if c == 0 or c == []:
                    return evaluate(e[3])
                return evaluate(e[2])
        elif '=' in e[0]:
            assert len(e)%2 == 0
            r = {}
            for i in range(0, len(e), 2):
                name = e[i][:-1]
                value = evaluate(e[i+1], {**env, **r})
                r[name] = value
            return r
    if isinstance(e, list):
        a = []
        for b in e:
            a.append(evaluate(b, env))
        return evaluate(a)



if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #   exit()
    # p = sys.argv[1]
    # test = "{a=5,b={c=3, d=4},e=7}((x->(y->+(* x x)y))2)3"

    #check this out :)
    # print(evaluate(parse("(x->y->plus(mult x x)y) 2 3")))
    # print(evaluate(parse("((x->(y->plus(mult x x)y))2)3")))
    # print(evaluate(parse("{a=x->y->plus(mult x x)y, b=a 2, c=b 3}")))

    assert(evaluate(parse("(x->y->plus(mult x x)y) 2 3")) == 7)
    assert(evaluate(parse("((x->(y->plus(mult x x)y))2)3")) == 7)
    assert(evaluate(parse("minus ((y->plus(mult 2 2)y)5)7")) == 2)
    assert(evaluate(parse("{a=x->y->plus(mult x x)y, b=a 2, c=b 3}minus(b 5)c")) == 2)
    assert(evaluate(parse("cond 14 2 3")) == 2)
    assert(evaluate(parse("cond 0 2 3")) == 3)
    assert(evaluate(parse("cond {} 2 3")) == 3)

    # print(evaluate(parse("""{
    #     append = x->y->cond x {head=x head, tail=append(x tail)y} y,
    #     gen = x->cond x (append(gen(minus x 1)) {head=x, tail={}}) {}
    #     }
    #     gen 3""")))

    #print(evaluate(parse("{fac=x->(cond x (mult x(fac (minus x 1))) 1)} fac 4")))

    #print()
    #debug("{fac=x->(cond x (mult x(fac (minus x 1))) 1)} fac 4")

    # print(evaluate(parse("""   
    # (x->
    #     (y->
    #         (
    #             plus(mult x 2)(mult y y)
    #         )
    #     )1
    # )4
    # """)))



