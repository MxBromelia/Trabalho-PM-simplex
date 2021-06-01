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

def solve_simplex(simplex, normalized=[]):
    if(all(el >=0 for el in simplex.matrix[0])):
        print_simplex_matrix(simplex.matrix)
        return simplex.matrix

    target_index = findindex(simplex.matrix[0], lambda el: el == -maxnpabs(simplex.matrix[0]))
    
    raw_ratios = (
        float(vector[-1]) / vector[target_index]
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

    return solve_simplex(simplex, [*normalized, target_index])

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

def print_simplex_matrix(simplex_matrix):
    for row in simplex_matrix:
        *variables, result = formatted_row(row)
        print('|', *variables, '|', result, '|')
    print('\n')

def formatted_row(row):
    return ['{:7.3f}'.format(var) for var in row]

if __name__ == '__main__':
    do_simplex([[1, 1, 100], [1, 3, 270]], [10, 12])
    do_simplex([
        [-4, 1, 4],
        [2, -3, 6]
    ], [1, 2])
    do_simplex(
        [
            [5, 1, 6, 24],
            [1, 1, 3, 8],
            [11, 3, 4, 95]
        ], [ 5, 1, 9]
    )