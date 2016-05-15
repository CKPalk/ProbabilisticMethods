# Probabilistic Methods
*Course work for CIS 410 at University of Oregon*

### Description:
Working with Markov and Bayesian Networks.

### Course Website:
<a href="https://www.cs.uoregon.edu/Classes/16S/cis410pm/" target="_blank">Probabilistic Methods in Artificial Intelligence</a>

### Progress:
In [my first iteration](A4/hw4.py) I computed the partition function using a naive brute force method. This wasn't going to be useful for larger graphs but was a necessary stepping stone.

In [my second iteration](A5/hw5.py) I used variable elimination to reduce the number of calculations needed to find the patition function. I was able to sum out a variable because of the seperation in our graph. I choose the variable which was a member of the least number of cliques. By summing out these variables we were reducing the complexity of ur graph and thus the computation time needed to find the partition function.
