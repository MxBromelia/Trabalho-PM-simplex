from dataclasses import InitVar, dataclass, field
from typing import Collection, Optional
from simplex import Simplex, print_solution
from math import floor
from json import load
import sys

Objective = Collection[float]
Constraints = Collection[Collection[float]]

def node_constraints(index, value, num_constraints):
    base_value = floor(value)
    return [
        [ *( 1 if i == index else 0 for i in range(num_constraints)),  base_value],
        [ *(-1 if i == index else 0 for i in range(num_constraints)), -base_value -1]
    ]

@dataclass
class BABNode:
    objective: Objective
    constraints: Constraints
    simplex: Simplex = field(init=False)

    def __post_init__(self):
        self.simplex = Simplex(objective=self.objective, constraints=self.constraints)

    def test_node(self):
        solution = self.simplex.solution()

        if solution is None:
            return []
        
        for index, value in enumerate(solution[1].values()):
            if not value.is_integer():
                lt_constraint, gt_constraint = node_constraints(index, value, len(solution[1]))
                return [
                    BABNode(objective=self.objective, constraints = [*self.constraints, lt_constraint]),
                    BABNode(objective=self.objective, constraints = [*self.constraints, gt_constraint])
                ]
        return self

@dataclass
class BABTree:
    constraints: Constraints
    objective: Objective
    subproblems: Collection =  field(init=False, default_factory=list)
    candidate_solution: Simplex = field(init=False, default=None)

    def __post_init__(self):
        start_problem = BABNode(objective=self.objective, constraints=self.constraints)
        self.subproblems.append(start_problem)

    def solve(self):
        while len(self.subproblems) > 0:
            current = self.subproblems.pop(0)
            result: BABNode = current.test_node()
            if isinstance(result, list):
                for subproblem in result:
                    [*rest, last] = subproblem.simplex.constraints
                    if last not in rest:
                        self.subproblems.append(subproblem)
            elif isinstance(result, BABNode):
                if self.candidate_solution is None or \
                   self.candidate_solution.solution()[0] < result.simplex.solution()[0]:
                    self.candidate_solution = result.simplex
        return self.candidate_solution.solution()

def branch_and_bound(constraints, objective):
    solver = BABTree(constraints=constraints, objective=objective)
    return solver.solve()

def main():
    if len(sys.argv) < 2:
        print("Documento não repassado")
        return
    with open(sys.argv[1]) as file:
        model = load(file)
    solution = branch_and_bound(
        model['constraints'],
        model['objective']
    )
    if solution is not None:
        print_solution(solution)

if __name__ == '__main__':
    main()
