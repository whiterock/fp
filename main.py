import string


def interpret(s):
    s = s.strip()
    if s.startswith("{"):
        # todo: handle empty records
        # todo: find ending }
        record = interpret_record(s[1:])


def interpret_record(s):
    record = dict()
    i = 0
    while i < len(s):
        s = s.strip()
        name = ""
        while s[i] in string.ascii_lowercase:
            name += s[i]
            i += 1

        while s[i] == " ":
            i += 1

        assert s[i] == "="

        while s[i] == " ":
            i += 1



        record[name] = interpret(s[i:])

        # # find out which function to call
        # if s[i] == "{":
        #     record[name] = interpret_record(s[i:])
        # elif s[i] in string.digits:
        #     end = min(s[i:].find(","), s[i:].find("}"))
        #     record[name] = int(s[i:end])  # fixme: maybe +1 error
        # elif s[i]



    # {a=5,b={c=3, d=4},e=7}


interpret("((x->(y->+(* x x)y))2)3")