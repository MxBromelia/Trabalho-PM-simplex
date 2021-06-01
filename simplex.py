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

def solve_simplex(simplex):
    print_simplex_matrix(simplex.matrix)

    pivot = simplex.matrix[0].index(-max(abs(x) for x in simplex.matrix[0] if x <= 0))
    
    ratios = [
        float(vector[-1]) / vector[pivot]
        for vector in simplex.matrix[1:]
    ]
    minratio = ratios.index(min(value for value in ratios if value >= 0)) + 1

    simplex.matrix[minratio] = simplex.matrix[minratio] * (1/float(simplex.matrix[minratio][pivot]))
    print_simplex_matrix(simplex.matrix)

    for index, vector in enumerate(simplex.matrix):
        if index == minratio:
            continue
        aux = vector[pivot]
        simplex.matrix[index] -= aux * simplex.matrix[minratio]
    
    print_simplex_matrix(simplex.matrix)

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
