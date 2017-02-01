# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 12:35:00 2017

@author: rober
"""

import itertools

import BayesianUtils as bay
import Algorithm as al
import sympy as sm
#succeed-or-fail scoring types
def apply_amount_succeeding_teams_data(teams, at_least, probs, get_prob, scouting={}):
    scouting = bay.certainty_filter_scouting(scouting) 
    non_scouted = []
    non_scouted.extend(teams)
    team_names = []
    teams_from_names = {}
    for team in teams:
        team_names.append(team.name)
        teams_from_names[team.name] = team
    
    scouting = al.filter_match_scouting(scouting, team_names)
    
    for team_name in scouting:
        team = teams_from_names[team_name]
        scouted_result = scouting[team_name][0]
        non_scouted.remove(team)
        if scouted_result == 1.0:
            probs = apply_at_least_succeeding_teams_data([team], 1, probs)
            at_least -= 1
        elif scouted_result == 0.0:
            probs = apply_at_most_succeeding_teams_data([team], 0, probs)
        else:
            raise RuntimeError("scouted_result: " + scouted_result.__str__())
    
    add_probs = []

    if len(non_scouted) > 0:
        nonsc_num = len(non_scouted)
        for i in range(min(nonsc_num, at_least), max(nonsc_num, at_least) + 1):
            for succeeded in itertools.combinations(non_scouted, i):
                failed = non_scouted.copy()
                multiply = []
                for team in succeeded:
                    failed.remove(team)
                    multiply.append(team)
                for team in failed:
                    multiply.append(1-team)
                add_probs.append(bay.mult(multiply))
    
        prob_if_a = get_prob(bay.add(add_probs))
        probs = (prob_if_a)*probs
    return bay.make_better(probs)

def apply_at_most_succeeding_teams_data(teams, at_most, probs, scouting={}):
    return apply_amount_succeeding_teams_data(teams, at_most + 1, probs, lambda t: 1-t, scouting)
            
def apply_at_least_succeeding_teams_data(teams, at_least, probs, scouting={}):
    return apply_amount_succeeding_teams_data(teams, at_least, probs, lambda t:t, scouting)
    
def apply_one_non_stack_collab_match(match_teams, match_result, prior, scouting={}):
    """
    Return the new probability distribution.
    match_teams: the team_symbols for the teams in the match
    match_result: the outcome of the match
    prior: the prior probability distribution
    """
    scouting = bay.certainty_filter_scouting(scouting)    
    
    if match_result == 1:
        return apply_at_least_succeeding_teams_data(match_teams, len(match_teams), prior, scouting)
    elif match_result == 0:
        return apply_at_most_succeeding_teams_data(match_teams, len(match_teams)-1, prior, scouting)
    else:
        raise RuntimeError("match_result: " + match_result.__str__())

def get_non_stack_collab_distrs(segment_matches, scouting, get_prior=bay.default_prior_prob):
    return bay.get_distrs(segment_matches, scouting, get_prior, apply_one_non_stack_collab_match)

#end succeed-or-fail scoring types

#chunk scoring types
def scouting_likelihood(scouted, ratio_stdev, contr):
    if len(sm.sympify(ratio_stdev).free_symbols) == 0 and len(sm.sympify(scouted).free_symbols) == 0:
        return sm.exp(-(((contr-scouted)/(scouted*ratio_stdev))**2))/(scouted*ratio_stdev)
        #return sm.exp(-(((contr-scouted)/(contr*ratio_stdev))**2))/(ratio_stdev*contr)
    raise RuntimeError('scouted: ' + scouted.__str__() + 'ratio_stdev: ' + ratio_stdev.__str__())

def binomial_sum_likelihood(teams, ps_from_teams, ns_from_teams):
    

def stacking_match_likelihood(teams, ns_from_teams, ps_from_teams, scouting, ratio_stdev):
    """
    Return the likelihood of the given match.
    ns_from_teams = team -> n
    ps_from_teams = team -> P
    scouting = team -> score
    """
    
    