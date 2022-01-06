import sys # Used for command-line arguments
import os  # Used for file paths
from time import time
from enum import Enum
from ortools.sat.python import cp_model

class ConstraintType(Enum):
    Authorisation = 0
    Separation = 1
    Binding = 2

class Constraint:
    def __init__(self, constraintType, values):
        self.constraintType = constraintType
        self.values = values

#TODO create At-most-k and One-Team subclasses of Constraint

class Instance:
    def __init__(self, numberOfTasks, numberOfUsers, numberOfConstraints, constraints):
        self.numberOfTasks = numberOfTasks
        self.numberOfUsers = numberOfUsers
        self.numberOfConstraints = numberOfConstraints
        self.constraints = constraints #List of type Constraint (see above)

def readFile(fileName):
    
    # Get path from src directory to chosen file
    filePath = os.path.dirname(__file__)
    fileName = '../instances/' + fileName
    filePath = os.path.join(filePath, fileName)

    file = open(filePath, 'r')

    tasksWords = file.readline().strip().lower().split()
    numberOfTasks = int(tasksWords[len(tasksWords)-1])

    usersWords = file.readline().strip().lower().split()
    numberOfUsers = int(usersWords[len(usersWords)-1])

    constraintsWords = file.readline().strip().lower().split()
    numberOfConstraints = int(constraintsWords[len(constraintsWords)-1])

    constraints = []

    for x in range(numberOfConstraints):
        words = file.readline().strip().lower().split()
        constraintType = words[0]

        if constraintType == "authorisations":
            words.remove(constraintType)
            constraintValues = list(map(int, map(lambda word: word[1], words)))
            constraint = Constraint(ConstraintType.Authorisation, constraintValues)
            constraints.append(constraint)

        elif constraintType == "separation-of-duty":
            words.remove(constraintType)
            constraintValues = list(map(int, map(lambda word: word[1], words)))
            constraint = Constraint(ConstraintType.Separation, constraintValues)
            constraints.append(constraint)

        elif constraintType == "binding-of-duty":
            words.remove(constraintType)
            constraintValues = list(map(int, map(lambda word: word[1], words)))
            constraint = Constraint(ConstraintType.Binding, constraintValues)
            constraints.append(constraint)

        else:
            print("Error: Unrecognised Constraint")
        #TODO at-most-k and one-team

    instance = Instance(numberOfTasks, numberOfUsers, numberOfConstraints, constraints)
    return instance

def solve(instance):
    print("Building model")
    model = cp_model.CpModel()
    
    #Define variables ---------------------------------------------------------
    assignment = []
    print("Tasks: ", instance.numberOfTasks)
    print("Users: ", instance.numberOfUsers)
    for i in range(instance.numberOfTasks):
        assignment.append(model.NewIntVar(1, instance.numberOfUsers, str((i+1))))
        # So assignment[0] contains a variable named 1, representing task 1,
        # whose value is the assigned user

    #Define constraints -------------------------------------------------------

    #Authorisation constraints
    authorisations = filter(lambda x: x.constraintType == ConstraintType.Authorisation, instance.constraints)
    for auth in authorisations:
        print("Adding authorisation constraint")
        values = auth.values
        user = values[0]
        values.remove(user)
        tasks = values
        print(user, tasks)
        for i in range(len(assignment)):
            # if a task in assignment is a list of the tasks permitted for user
            if (i+1) in tasks:
                pass
            else: 
                # user not allowed to perform task
                model.Add(assignment[i] != user)

    #Solve --------------------------------------------------------------------
    print("Solving instance")
    starttime = int(time() * 1000)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    endtime = int(time() * 1000)
    print(f"Instance solved in {endtime - starttime}ms")
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("sat")
        printModel(instance, solver, assignment)
    else:
        print("unsat")

def printModel(instance, solver, assignment):
    #TODO print
    for i in range(instance.numberOfTasks):
        print(f"Task {assignment[i].Name} assigned to User {solver.Value(assignment[i])}")

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        file = sys.argv[1]
        print(f"File selected: {file}")
        print("Reading file")
        instance = readFile(file)
        print("Starting solver")
        solve(instance)
    else:
        print("Please select a problem instance file")
