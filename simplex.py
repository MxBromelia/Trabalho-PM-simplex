from collections import UserList
from dataclasses import dataclass

class Vector(UserList):
    def __mul__(self, other):
        return Vector(el * other for el in self)

    def __rmul__(self, other):
        return self * other

    def __add__(self, other):
        if len(self) != len(other):
            raise AttributeError
        return Vector(operandA + operandB for operandA, operandB in zip(self, other))

    def __sub__(self, other):
        if len(self) != len(other):
            raise AttributeError
        return Vector(operandA - operandB for operandA, operandB in zip(self, other))

@dataclass
class Simplex:
    matrix: list
    num_variables: int
    num_constraints: int

    def current_solution(self):
        return (self.matrix[0][-1], self._variables())

    def _variables(self):
        return dict(((self._varname(key), self._varvalue(key)) for key in range(self.num_variables)))

    def _varname(self, key):
        return f'x{key+1}'

    def _varvalue(self, key):
        values = [vec[key] for vec in self.matrix[1:]]
        try:
            index = findindex(values, lambda x: x == 1.00) + 1
            return self.matrix[index][-1]
        except StopIteration:
            return 0
        


def do_simplex(constraints, objective):
    matrix = [
        normalized_objective(len(constraints), objective),
        *normalized_constraints(constraints)
    ]
    simplex = Simplex(matrix, len(objective), len(constraints))
    return solve_simplex(simplex)

def findindex(iterable, condition):
    return next(
        index for index, element in enumerate(iterable)
        if condition(element)
    )

def maxnpabs(iterable):
    return max(abs(el) for el in iterable if el <= 0)

def solve_simplex(simplex, normalized=set()):
    if(
        all(el >=0 for el in simplex.matrix[0])
        or len(normalized) == simplex.num_variables
    ):
        return simplex.current_solution()

    target_index = findindex(simplex.matrix[0], lambda el: el == -maxnpabs(simplex.matrix[0]))

    raw_ratios = (
        float(vector[-1]) / vector[target_index] if vector[target_index] != 0 else -1
        for vector in simplex.matrix[1:]
    )
    ratios = [ratio for ratio in raw_ratios if ratio > 0]
    if(len(ratios) == 0):
        print("O sistema possui múltiplas soluções\n")
        return None

    minratio_index = ratios.index(min(value for value in ratios if value >= 0)) + 1
    normalized_vector = simplex.matrix[minratio_index]
    normalized_vector = normalized_vector * (1/float(normalized_vector[target_index]))

    for index, vector in enumerate(simplex.matrix):
        if index == minratio_index:
            continue
        aux = vector[target_index]
        simplex.matrix[index] -= aux * normalized_vector
    simplex.matrix[minratio_index] = normalized_vector

    return solve_simplex(simplex, {*normalized, target_index})

def normalized_constraints(constraints):
    return_value = []
    for index, constraint in enumerate(constraints):
        *variables, result = constraint
        slack = [ 1 if i == index else 0 for i  in range(len(constraints))]
        return_value.append(Vector([*variables, *slack, result]))
    return return_value

def normalized_objective(num_constraints, objective):
    return Vector([
        *(-x for x in objective),
        *([0] * num_constraints),
        0
    ])

def print_solution(simplex_solution):
    print(f"Maximun Value: {simplex_solution[0]}")
    for key, value in simplex_solution[1].items():
        print(f'{key}: {value}')

def print_simplex_matrix(simplex_matrix):
    for row in simplex_matrix:
        *variables, result = formatted_row(row)
        print('|', *variables, '|', result, '|')
    print('\n')

def formatted_row(row):
    return ['{:7.3f}'.format(var) for var in row]

if __name__ == '__main__':
    solution = do_simplex([
        [2, 1, 2, 8],
        [2, 2, 3, 12],
        [2, 1, 3, 10]
    ], [20, 15, 25])
    print_solution(solution)
