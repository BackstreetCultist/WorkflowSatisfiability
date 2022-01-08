I implemented an experimental tool to help you debug your solvers.  It automatically runs your solver on multiple instances and checks that it gives correct answers.  For unstatisfiable instances, it checks that your solver identifies that the instance is unsatisfiable.  For satisfiable instances, it checks that your solver returns some solution and also tests that the solution satisfies the instance.  The latter function is particularly useful because checking such solutions by hand is often impractical.

The tool expects that, if the instance is unsatisfiable, your solver will print 'unsat' at some point.  If the instance is satisfiable, it expects that your solver will print the solution in multiple lines, each line assigning one user to one step.  Users should be referred as 'u<index>' or 'user <index>' and steps as 's<index>' or 'step <index>'.  Indexing is 1-based.  (There were no strict requirements for the output format of your solver, however if you want to use the tool then you will have to make sure the output of your solver is compatible with it.)

If the tool finds a mistake in your solution, it explains the mistake.  It shows only one mistake per solution, even if there are multiple mistakes.

You can use the tool to debug your solvers, however you are not allowed to use fragments of the tool code without referencing it.

If your solver passes all the tests, it does not automatically mean that it is correct but if it does not pass some tests then it certainly is incorrect.  Also note that the tool does not test the functionality related to checking whether the solution is unique.

To use the tool, place your solver in the same folder as coursework-tester.py, navigate to this folder in the console and run the folling command:
python coursework-tester.py test-solver.py
(Replace 'test-solver.py' with the filename of your solver.)

You can also test your solver on specific instances only, for example
python coursework-tester.py test-solver.py 3-constraint

If you have any problems with using the tool, please let me know.