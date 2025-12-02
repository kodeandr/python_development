def calculate(vars, values, exp):
    var_to_value = dict(zip(vars, values))
    return eval(exp, var_to_value)

print(calculate('xyz', [1, 2, 3], 'x-y+z'))
print(calculate('dbcw', [3, 0, -2, -3], '-d-c-b+w'))
print(calculate('abcd', [0, 0, 0, 0], 'a+b+c+d'))
print(calculate('a', [4], 'a'))
print(calculate('v', [-2], 'v')) 
print(calculate('ab', [2, 2], 'a+b'))