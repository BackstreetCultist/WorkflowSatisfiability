# Workflow Satisfiability Problem Solver
## Source Code
The source code is implemented in Python using Google's OR-Tools solver suite.
It requires python3, and OR-Tools must be installed with the following command:

    pip install ortools

When running the program from the src/ directory, it will read files from the
instances/ directory. Running from here will demonstrate that the program is
able to test if a solution is unique:

    python WorkflowSatisfiability.py example1.txt

    python WorkflowSatisfiability.py 3-constraint/0.txt

A version with slightly different file management can also be run
under test from the CourseworkTester directory:

    python coursework-tester.py WorkflowSatisfiability.py

## Report
The report is included both in LaTeX source format and .pdf compiled format,
under the report/ directory.
