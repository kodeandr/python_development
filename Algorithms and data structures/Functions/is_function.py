def is_function(pairs):
    check_set =  set()
    for p in pairs:
        if p[0] in check_set:
            return False
        else:
            check_set.add(p[0])
    return True

print(is_function([(1, 3), (2, 5), (3, 7)]))
print(is_function([(1, 3), (2, 5), (1, 7)]))
print(is_function([(1, 3)]))
print(is_function([(5, 5)]))
print(is_function([(1, 1), (2, 2)]))
print(is_function([(1, 1), (1, 2)]))