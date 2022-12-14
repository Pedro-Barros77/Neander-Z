class Infix:
    def __init__(self, function):
        self.function = function
    def __ror__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))
    def __or__(self, other):
        return self.function(other)
    def __rlshift__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))
    def __rshift__(self, other):
        return self.function(other)
    def __call__(self, value1, value2):
        return self.function(value1, value2)

sum_tuple_infix=Infix(lambda a, b: (a[0] + b[0], a[1] + b[1]))



def space_to_center(obj: tuple[int, int], container: tuple[int,int]):
    return ((container[0] - obj[0]) // 2, (container[1] - obj[1]) // 2)

def clamp(value, min_value, max_value): 
    return max(min_value, min(value, max_value))

def between(value, min, max, inclusive = True):
    if inclusive:
        return value >= min and value <= max
    return value > min and value < max

def value_or_one(value):
    return value if value != 0 else 1

def try_parse_int(text):
    try:
        return int(text)
    except Exception:
        return 0 