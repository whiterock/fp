import string
from pprint import pprint


parens = {
    "(": ")",
    "{": "}"
}


def partition(s, stop_on=None):
    result = []
    i = 0
    buffer = ""
    while i < len(s):
        cc = s[i]
        if cc == stop_on:
            if buffer:
                result.append(buffer)
            return result, i
        elif cc in parens:
            # empty previous buffer if non-empty
            if buffer:
                result.append(buffer)
                buffer = ""

            # recursion here
            a_partition, i_advance = partition(s[i+1:], stop_on=parens[cc])
            i += i_advance + 2
            result.append(a_partition)
        elif cc == ",":
            if buffer:
                result.append(buffer)
                buffer = ""
            i += 1
        else:
            buffer += cc
            i += 1

    if buffer:
        result.append(buffer)

    return result, i


# {a=5,b={c=3, d=4},e=7}
test = "{a=5,b={c=3, d=4},e=7}((x->(y->+(* x x)y))2)3"
pprint(test)
pprint(partition(test)[0])