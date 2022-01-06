import sys
import os
from enum import Enum

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
    def __init__(self, numberOfUsers, numberOfTasks, numberOfConstraints, constraints):
        self.numberOfUsers = numberOfUsers
        self.numberOfTasks = numberOfTasks
        self.numberOfConstraints = numberOfConstraints
        self.constraints = constraints #List of type Constraint (see above)

def readFile(fileName):
    
    # Get path from src directory to chosen file
    filePath = os.path.dirname(__file__)
    fileName = '../instances/' + fileName
    filePath = os.path.join(filePath, fileName)

    file = open(filePath, 'r')

    stepsWords = file.readline().strip().split()
    numberOfSteps = int(stepsWords[len(stepsWords)-1])

    usersWords = file.readline().strip().split()
    numberOfUsers = int(usersWords[len(usersWords)-1])

    constraintsWords = file.readline().strip().split()
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

    instance = Instance(numberOfSteps, numberOfUsers, numberOfConstraints, constraints)
    return instance

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        file = sys.argv[1]
        print(f"File selected: {file}")
        instance = readFile(file)
        print(instance.numberOfUsers, instance.numberOfTasks, instance.numberOfConstraints, len(instance.constraints))
    else:
        print("Please select a problem instance file")
