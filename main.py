import string, sys
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


def split_my_thing(l):
    for n, i in enumerate(l):
        if type(i) is list:
            l[n] = split_my_thing(l[n])
        elif type(i) is str and ' ' in i:
            l = i.split()
    return l

environment = {
	'plus': lambda a,b: a+b,
	'minus': lambda a,b: a-b,
	'mult': lambda a,b: a*b,
	'div': lambda a,b: a/b,
	'cond': lambda a,b,c: b if a else c
}

class lamb():
	def __init__(self,variable_name,body,env):
		self.variable_name = variable_name
		self.body = body
		self.env = env

	def __str__(self):
		return "Lambda: " + self.variable_name + "->" + str(self.body)

def recursive_replace(l, a,b):
    for n, i in enumerate(l):
        if type(i) is list:
            l[n] = recursive_replace(l[n], a,b)
        elif type(i) is str:
            l[n] = i.replace(a,b)
    return l

def evaluate(e, env=environment):
	#print(e)
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

			if len(e) == 3:
				called_with = e[2]
				new_body = recursive_replace(body, variable_name, called_with)
				return evaluate(new_body, env)

			return lamb(variable_name, body, env)
		elif "{" in e[0]:
			pass #unimplemented
		else:
			#function call
			name = e[0]
			if name not in env.keys():
				print("Error: unrecognised token " + name)
				exit()
			if name != "cond":
				return env[name](evaluate(e[1]), evaluate(e[2]))
			else:
				return env[name](e[1],e[2],e[3])
	elif isinstance(e[0], lamb):
		#call lambda
		try:
			called_with = e[1]
			new_body = recursive_replace(e[0].body, e[0].variable_name, called_with)
			return evaluate(new_body, env)
		except:
			pass


if __name__ == "__main__":

	# if len(sys.argv) != 2:
	# 	exit()
	# p = sys.argv[1]
	# test = "{a=5,b={c=3, d=4},e=7}((x->(y->+(* x x)y))2)3"
	# pprint(test)
	# pprint(partition(test)[0])

	print(evaluate(split_my_thing(partition("((x->(y->(plus(mult x x)y))2)3")[0][0])))
	print(evaluate(split_my_thing(partition("(x->(y->(plus(mult x 2)(mult y y)))1)4)")[0])))
