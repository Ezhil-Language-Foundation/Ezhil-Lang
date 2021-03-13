import Interpreter
q = Interpreter.NoClobberDict()
q['foo'] = 'bar'

try:
    q['foo'] = 'car'
except KeyError as e:
    exit(0)

exit(-1)
