import sys # Used for command-line arguments
import os  # Used for file paths
from time import time
from enum import Enum
from ortools.sat.python import cp_model

class ConstraintType(Enum):
    Authorisation = 0
    Separation = 1
    Binding = 2
    AtMostK = 3
    OneTeam = 4

class Constraint:
    def __init__(self, constraintType, values):
        self.constraintType = constraintType
        self.values = values

class AtMostK(Constraint):
    def __init__(self, constraintType, values, k):
        self.k = k
        super().__init__(constraintType, values)

class OneTeam(Constraint):
    def __init__(self, constraintType, values, teams):
        self.teams = teams
        super().__init__(constraintType, values)

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
            constraintValues = list(map(int, map(lambda word: word[1:], words)))
            constraint = Constraint(ConstraintType.Authorisation, constraintValues)
            constraints.append(constraint)

        elif constraintType == "separation-of-duty":
            words.remove(constraintType)
            constraintValues = list(map(int, map(lambda word: word[1:], words)))
            constraint = Constraint(ConstraintType.Separation, constraintValues)
            constraints.append(constraint)

        elif constraintType == "binding-of-duty":
            words.remove(constraintType)
            constraintValues = list(map(int, map(lambda word: word[1:], words)))
            constraint = Constraint(ConstraintType.Binding, constraintValues)
            constraints.append(constraint)

        elif constraintType == "at-most-k":
            words.remove(constraintType)
            k = int(words.pop(0))
            constraintValues = list(map(int, map(lambda word: word[1:], words)))
            constraint = AtMostK(ConstraintType.AtMostK, constraintValues, k)
            constraints.append(constraint)

        elif constraintType == "one-team":
            words.remove(constraintType)

            #Set tasks to values
            constraintValues = []
            for word in words:
                if 'u' not in word:
                    constraintValues.append(int(word[1:]))
            for value in constraintValues:
                words.remove(("s"+str(value)))

            #Create sub-lists for teams
            teams = []
            for i in range(str(words).count(')')):
                team = []
                for word in words:
                    if word[len(word)-1] == ')':
                        if word[0] == '(':
                            team.append(int(word[2:len(word)-1]))
                        else:
                            team.append(int(word[1:len(word)-1]))
                        break
                    else:
                        if word[0] == '(':
                            team.append(int(word[2:]))
                        else:
                            team.append(int(word[1:]))
                words = words[len(team):]
                teams.append(team)
            constraint = OneTeam(ConstraintType.OneTeam, constraintValues, teams)
            constraints.append(constraint)

        else:
            print("Error: Unrecognised Constraint")
        #TODO one-team

    instance = Instance(numberOfTasks, numberOfUsers, numberOfConstraints, constraints)
    return instance

def solve(instance):
    print("Building model")
    model = cp_model.CpModel()
    
    #Define variables ---------------------------------------------------------
    print("Tasks: ", instance.numberOfTasks)
    print("Users: ", instance.numberOfUsers)
    assignment = [model.NewIntVar(1, instance.numberOfUsers, str(i+1)) for i in range(instance.numberOfTasks)]
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

    #Separation of Duty
    separations = filter(lambda x: x.constraintType == ConstraintType.Separation, instance.constraints)
    for separation in separations:
        print("Adding separation constraint")
        print(separation.values)
        x = separation.values[0]
        y = separation.values[1]

        model.Add(assignment[(x-1)] != assignment[(y-1)])

    #Binding of Duty
    bindings = filter(lambda x: x.constraintType == ConstraintType.Binding, instance.constraints)
    for binding in bindings:
        print("Adding binding constraint")
        print(binding.values)
        x = binding.values[0]
        y = binding.values[1]

        model.Add(assignment[(x-1)] == assignment[(y-1)])
        
    #At-Most-K
    atMostKs = list(filter(lambda x: x.constraintType == ConstraintType.AtMostK, instance.constraints))
    for i in range(len(atMostKs)):
        print("Adding at-most-k constraint")
        print(atMostKs[i].k, atMostKs[i].values)

        valuesSubset = [assignment[x-1] for x in atMostKs[i].values]

        #This loop creates a list of boolean variables for each user
        #The boolean flag is True if the user appears in the list
        #And otherwise false
        #This solution inspired by a post by OR-Tools dev Laurent Perron
        #https://stackoverflow.com/questions/60447449/how-to-define-a-constraint-in-ortools-to-set-a-limit-of-distinct-values
        #And implemented with regard to
        #https://developers.google.com/optimization/cp/channeling
        usersInSubset = []
        for j in range(instance.numberOfUsers):
            userInSubset = model.NewBoolVar(("atMostK"+str(i)+".user"+str(j+1)))
            for value in valuesSubset:
                var = model.NewBoolVar(("atMostK"+str(i)+".user"+str(j+1)+".forValue"+str(value)))
                model.Add(value == (j+1)).OnlyEnforceIf(var)
                model.Add(value != (j+1)).OnlyEnforceIf(var.Not())
                model.Add(userInSubset == True).OnlyEnforceIf(var)
            usersInSubset.append(userInSubset)

        #In python, True==1 and False==0, so you can sum bools like so
        model.Add(sum(usersInSubset) <= atMostKs[i].k)

    #One Team
    oneTeams = list(filter(lambda x: x.constraintType == ConstraintType.OneTeam, instance.constraints))
    for i in range(len(oneTeams)):
        print("Adding one-team constraint")
        print(oneTeams[i].values, oneTeams[i].teams)

        #Create a bool for each team, saying whether or not all tasks are assigned to that team
        allInTeam = [model.NewBoolVar("OneTeam"+str(i)+".Team"+str(j)) for j in range(len(oneTeams[i].teams))]

        #Add constraints that that bool is true if that is the case
        for j in range(len(oneTeams[i].teams)):
            #Create a set of bools for whether each individual task is assigned to the team
            tasksAssignedToTeam = []
            for k in range(len(oneTeams[i].values)):
                #This bool is true if the task is assigned to an individual user from the team
                taskAssignedToTeam = model.NewBoolVar("OneTeam"+str(i)+".Team"+str(j)+".Value"+str(k))
                #Due to channeling, we must create a bool for whether it is assigned to each user
                taskAssignedToTeamUsers = []
                for l in range(len(oneTeams[i].teams[j])):
                    taskAssignedToTeamUser = model.NewBoolVar("OneTeam"+str(i)+".Team"+str(j)+".Value"+str(k)+".User"+str(l))
                    model.Add(assignment[oneTeams[i].values[k]-1] == oneTeams[i].teams[j][l]).OnlyEnforceIf(taskAssignedToTeamUser)
                    model.Add(assignment[oneTeams[i].values[k]-1] != oneTeams[i].teams[j][l]).OnlyEnforceIf(taskAssignedToTeamUser.Not())
                    taskAssignedToTeamUsers.append(taskAssignedToTeamUser)
                
                #Check whether at least one user in the team has the task assigned to them
                model.Add(sum(taskAssignedToTeamUsers) >= 1).OnlyEnforceIf(taskAssignedToTeam)
                model.Add(sum(taskAssignedToTeamUsers) < 1).OnlyEnforceIf(taskAssignedToTeam.Not())
                #If so, we can say that that task is assigned to the team
                tasksAssignedToTeam.append(taskAssignedToTeam)
            
            #If all in set are true then all tasks are assigned to the team, so we can say allInTeam[j] is true
            model.Add(sum(tasksAssignedToTeam) == len(tasksAssignedToTeam)).OnlyEnforceIf(allInTeam[j])
            model.Add(sum(tasksAssignedToTeam) != len(tasksAssignedToTeam)).OnlyEnforceIf(allInTeam[j].Not())
        
        #Add constraint that at least one in allInTeam must be True
        model.AddBoolOr(allInTeam)

    #Solve --------------------------------------------------------------------f
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
