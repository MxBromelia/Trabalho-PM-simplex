def simplex(constraints, objective):
    matrix = [
        normalized_objective(len(constraints), objective),
        *normalized_constraints(constraints)
    ]
    print_simplex_matrix(matrix)

def normalized_constraints(constraints):
    return_value = []
    for index, constraint in enumerate(constraints):
        *variables, result = constraint
        slack = [ 1 if i == index else 0 for i  in range(len(constraints))]
        return_value.append([0, *variables, *slack, result])
    return return_value

def normalized_objective(num_constraints, objective):
    return [
        1,
        *(-x for x in objective),
        *([0] * num_constraints),
        0
    ]

def print_simplex_matrix(simplex_matrix):
    for row in simplex_matrix:
        *variables, result = formatted_row(row)
        print('|', *variables, '|', result, '|')

def formatted_row(row):
    return ['{:2d}'.format(var) for var in row]

if __name__ == '__main__':
    simplex([[7, 11, 24], [6, 5, 19], [1, 9, 33]], [6, 5])
