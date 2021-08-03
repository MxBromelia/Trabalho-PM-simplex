from collections import UserList
from dataclasses import InitVar, dataclass, field
import sys
from json import load
from types import SimpleNamespace
from typing import Collection
from functools import lru_cache

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
    constraints: Collection[Collection[float]]
    objective: Collection[float]
    matrix: Collection[Collection[float]] = field(init=False)
    num_variables: int = field(init=False)
    num_constraints: int = field(init=False)
    solved: bool = field(init=False, default=False)

    def __post_init__(self):
        self.matrix = simplex_matrix(self.constraints, self.objective)
        self.num_constraints = len(self.constraints)
        self.num_variables = len(self.objective)
        self._solution = None

    def current_solution(self):
        return (self.matrix[0][-1], self._variables())

    def solution(self):
        if self._solution is None:
            self._solution = solve_simplex(self)
        return self._solution

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
    simplex = Simplex(constraints, objective)
    return solve_simplex(simplex)

def simplex_matrix(constraints, objective):
    return [
        normalized_objective(len(constraints), objective),
        *normalized_constraints(constraints)
    ]

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

    raw_ratios = [
        float(vector[-1]) / vector[target_index] if vector[target_index] != 0 else -1
        for vector in simplex.matrix[1:]
    ]
    ratios = [ratio for ratio in raw_ratios if ratio >= 0]
    if(len(ratios) == 0):
        print("O sistema possui múltiplas soluções\n")
        return None

    minratio_index = raw_ratios.index(min(value for value in raw_ratios if value >= 0)) + 1
    normalized_vector = simplex.matrix[minratio_index]

    try:
        normalized_vector = normalized_vector * (1/float(normalized_vector[target_index]))
    except:
        breakpoint()
        raise 'deu ruim'

    for index, vector in enumerate(simplex.matrix):
        if index == minratio_index:
            continue
        aux = vector[target_index]
        simplex.matrix[index] -= aux * normalized_vector
    simplex.matrix[minratio_index] = normalized_vector

    return solve_simplex(simplex, {*normalized, target_index})

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

def main():
    if len(sys.argv) < 2:
        print("Documento não repassado")
        return
    with open(sys.argv[1]) as file:
        model = load(file)
    solution = do_simplex(
        model['constraints'],
        model['objective']
    )
    if solution is not None:
        print_solution(solution)


if __name__ == '__main__':
    main()
