import sys
import re


def get_error(instance, is_sat, solution):
    if not solution:
        if not is_sat:
            return None
        return f'{instance} is satisfiable but your solver returned "unsat"'
        
    with open(instance, 'r') as f:
        n = int(re.match(r'#Steps:\s+(\d+)', f.readline(), re.IGNORECASE).group(1))
        m = int(re.match(r'#Users:\s+(\d+)', f.readline(), re.IGNORECASE).group(1))
        c = int(re.match(r'#Constraints:\s+(\d+)', f.readline(), re.IGNORECASE).group(1))

        if len(solution) != n:
            return f'The solution was supposed to assign users to {n} steps but it assigned users to {len(solution)} steps.'

        for s in range(n):
            if solution[s] < 0 or solution[s] >= m:
                return f'Step s{s+1} is assigned user u{solution[s]} whereas only users u1..u{m} exist'

        S = set(range(n))

        for line_index in range(c):
            line = f.readline().strip().lower()
            values = line.split()

            if values[0] == 'authorisations':
                u = int(values[1][1:]) - 1
                A = [int(v[1:]) - 1 for v in values[2:]]
                for s in S - set(A):
                    if solution[s] == u:
                        return f'Broken constraint: {line}'
            elif values[0] == 'binding-of-duty':
                s1 = int(values[1][1:]) - 1
                s2 = int(values[2][1:]) - 1
                if solution[s1] != solution[s2]:
                    return f'Broken constraint: {line}'
            elif values[0] == 'separation-of-duty':
                s1 = int(values[1][1:]) - 1
                s2 = int(values[2][1:]) - 1
                if solution[s1] == solution[s2]:
                    return f'Broken constraint: {line}'
            elif values[0] == 'at-most-k':
                k = int(values[1])
                T = [int(v[1:]) - 1 for v in values[2:]]
                s = set([solution[t] for t in T])
                if len(s) > k:
                    return f'Broken constraint: {line}'
            elif values[0] == 'one-team':
                steps = re.findall(r's\d+', line, re.IGNORECASE)
                T = [int(step[1:]) - 1 for step in steps]
                teams = re.findall(r'\([u\d\s]+\)', line, re.IGNORECASE)
                teams = [[int(t[1:]) - 1 for t in team[1:-1].split()] for team in teams]

                for team in teams:
                    if solution[T[0]] in team:
                        for s in T:
                            if solution[s] not in team:
                                return f'Broken constraint: {line}'

            else:
                print('Unknown constraint ' + values[0])
                exit(1)

        return None


def run(instance_path, solver_path):
    from subprocess import check_output
    print("Running: ", instance_path, solver_path)
    output = check_output(['python', solver_path, instance_path], shell=True).decode("utf-8")
    return output


def parse_output(output):
    if re.match('unsat', output, re.IGNORECASE):
        return False
    else:
        lines = output.split(sep='\n')
        solution = []
        for line in lines:
            m1 = re.match(r'.*(s|step )(\d+).*', line, re.IGNORECASE)
            m2 = re.match(r'.*(u|user )(\d+).*', line, re.IGNORECASE)
            if m1 and m2:
                step = int(m1.group(2)) - 1
                user = int(m2.group(2)) - 1
                while step >= len(solution):
                    solution.append(-1)
                if solution[step] >= 0:
                    raise Exception(f'Step s{step+1} is assigned twice.')
                solution[step] = user

        for i in range(len(solution)):
            if solution[i] < 0:
                raise Exception(f'Step s{i + 1} is not assigned.')

        return solution

    
def test(instance_name, solver_name):
    import os
    instance_path = os.path.join(sys.path[0], instance_name + '.txt')
    solution_path = os.path.join(sys.path[0], instance_name + '-solution.txt')
    with open(solution_path, 'r') as f:
        if re.match(r'unsat', f.readline(), re.IGNORECASE):
            sat = False
        else:
            sat = True

    try:
        output = run(instance_path, solver_name)
        solution = parse_output(output)
        error = get_error(instance_path, sat, solution)
    except Exception as e:
        error = e
        solution = None

    if error is None:
        print(f"{instance_name}: everything's correct.")
    else:
        print(f'\n{instance_name}: {error}')
        print('OUTPUT:\n------\n' + output + '------')
        if solution is not None:
            print('Interpreted as:')
            if not solution:
                print('unsat')
            else:
                for i in range(len(solution)):
                    print(f's{i+1}: u{solution[i]+1}')
            print()


def test_dir(dir, solver_file):
    from os.path import join, exists
    i = 0
    while exists(join(dir, str(i) + '.txt')):
        test(join(dir, str(i)), solver_file)
        i += 1


if len(sys.argv) not in [2, 3]:
    print('Usage:\n'
          'python coutsework-tester.py <your solver filename> [<instances folder>]\n'
          'If the second parameter is not supplied, the tool loads the instances from all the subfolders;'
          'you can delete some subfolders, such as 4-constraint-hard, to skip those tests.\n\n'
          'Example 1: To test the test-solver.py solver on all the instances, run\n'
          'python test-solver.py\n\n'
          'Example 2: To test it on 4-constraint-small instances, run\n'
          'python test-solver.py 4-constraint-small')
    exit(1)

solver_file = sys.argv[1]
if len(sys.argv) > 2:
    test_dir(sys.argv[2], solver_file)
else:
    print("Looking for files")
    from os import listdir
    print(listdir('.'))
    for folder in listdir('.'):
        print("Testing: ", folder)
        test_dir(folder, solver_file)
