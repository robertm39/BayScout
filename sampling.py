# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 15:48:39 2017

@author: rober
"""

from IPython.display import display
from sympy.interactive import printing

import sympy as sm
from sympy import oo
import numpy as nm

import BayesianUtils as bay

PROB_DOMAIN = sm.Interval(0, 1)

def max_univariate_value(expr, symbol, domain=sm.S.Reals):
    printing.init_printing(use_latex='png')
    
    diff = sm.diff(expr, symbol).simplify()
    
    if not symbol in diff.free_symbols: #for constant exprs
        return sm.Interval(0,0);
    
    solution = sm.solveset(sm.Eq(diff, 0), symbol, domain).intersection(domain)
    display(solution)
    #new_solutions = []
    #for new_sol in solution:
    #    for old_sol in solutions:
    #        in_sol = sm.solveset(sm.Eq(symbol, new_sol), symbol, domain)
    #        new_solutions.append(in_sol.intersection(old_sol))
            
    #solutions = new_solutions
    
    maximum = sm.imageset(symbol, expr, solution).sup
    result = sm.solveset(sm.Eq(expr, maximum), symbol, domain)
    
    return result

def burn_and_thin_markov(markov, val=0, burn=1, thin=10, samples=1):
    """
    Return samples samples gotten from the markov method given, after burning burn samples and thinning.
    """
    val = thin_markov(markov, val, burn) #burn-in
    samples = [val]
    for i in range(0, samples - 1): #there's already one sample from after the burn-in
        val = thin_markov(markov, val, thin)
        samples.append(val)
    return samples

def thin_markov(markov, val=None, iters=1): #returns the last value
    for i in range(0, iters):
        val = markov(val)
    return val

def random_from_set(s): #make faster
    inf = s.inf.evalf()
    sup = s.sup.evalf()
    val = rand_between(inf, sup)
    while not val in s:
        val = rand_between(inf, sup)
    return val.evalf()
    
def rand_between(minimum, maximum):
    return (maximum - minimum)*nm.random.rand() + minimum
    
def bound_slice_sample(symbol, distr, domain=sm.S.Reals):
    return lambda x: slice_sample(symbol, distr, prev_x=x, domain=domain)
    
SLICE_X = sm.symbols('SLICE_X')
SLICE_Y = sm.symbols('SLICE_Y')

def slice_sample(symbol, distr, prev_x=None, domain=sm.S.Reals, __cache={}):
    """
    Return a randomly chosen value of x in domain from distr.
    """
    
    distr = distr.subs(symbol, SLICE_X)
    sm.pretty_print(distr)
    
    if prev_x == None:
        prev_x = random_from_set(max_univariate_value(distr, SLICE_X, domain))
    
    free_symbols = distr.free_symbols
    
    if len(free_symbols) > 1:
        others = []
        others.extend(free_symbols)
        others.remove(SLICE_X)
        distr = bay.without(distr, others) #get marginal distribution
    
    if not (distr, domain) in __cache:
        __cache[distr, domain] = sm.solveset(distr >= SLICE_Y, SLICE_X, domain=domain)
    at_least_set = __cache[distr, domain]
    
    max_y = distr.subs(SLICE_X, prev_x).evalf()
    y = nm.random.rand() * max_y
    x_slice = at_least_set.subs(SLICE_Y, y).reduce().intersection(domain)
    sm.pretty_print(x_slice)
    #x_slice = sm.solveset(distr >= y, symbol, domain=domain).intersection(domain)
    return random_from_set(x_slice)
    
def bound_gibbs_sample(distr, sample=bound_slice_sample):
    """
    Return a partially bound gibbs sample function that only takes the values.
    """
    return lambda v: gibbs_sample(v, distr, sample)
    
def gibbs_sample(values, distr, sample=bound_slice_sample, internal_sample_iters=5):
    n_values = values.copy()
    for symbol in values:
        cond_distr = distr
        for other in values:
            if other != symbol:
                cond_distr = cond_distr.subs(other, n_values[other])
        n_values[symbol] = thin_markov(sample(symbol, distr), iters=internal_sample_iters)
    return n_values
