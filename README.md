# Workflow Satisfiability Problem Solver
## Source Code
The source code is implemented in Python using Google's OR-Tools solver suite. It requires python3, and OR-Tools must be installed with the following command:

    pip3 install ortools

Please include the file path to the chosen problem instance under the instances/
directory as a command-line argument when running the program, for example (from
src directory):

    python3 WorkflowSatisfiability.py example1.txt

    python3 WorkflowSatisfiability.py 3-constraint/0.txt
