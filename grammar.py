"""
COMS W4705 - Natural Language Processing - Fall 2023
Homework 2 - Parsing with Context Free Grammars 
Daniel Bauer
"""

import sys
from collections import defaultdict
from math import fsum
import math

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """
        #move through lhs symbols
        for tup_l in self.lhs_to_rules:
            #probability variable
            prob = 0
            #move through rhs of tup_l in list
            for tup_r in self.lhs_to_rules[tup_l]:
                #add probability
                prob += tup_r[2]
                rhs = tup_r[1]
                #checks nonterminal to terminal (A -> b)
                if len(rhs) == 1:
                    if rhs not in self.rhs_to_rules.keys():
                        return False
                #checks nonterminal to two nonterminals (A -> BC)
                elif len(rhs) == 2:
                    if rhs[0] not in self.lhs_to_rules.keys() or rhs[1] not in self.lhs_to_rules.keys():
                        return False
                #returns false if rhs smaller than 1 and larger than 2
                else:
                    return False
            #now, checks if probability is 1
            if math.isclose(prob,1.0) != 1:
                return False
            
        return True


if __name__ == "__main__":
    with open(sys.argv[1],'r') as grammar_file:
        grammar = Pcfg(grammar_file)

    if grammar.verify_grammar():
        print("congrats! your grammar is a valid pcfg in cnf.")
    else:
        print("sorry, your grammar is not in cnf :(")
