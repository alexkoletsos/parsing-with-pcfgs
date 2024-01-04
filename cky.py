"""
COMS W4705 - Natural Language Processing - Fall 2023
Homework 2 - Parsing with Probabilistic Context Free Grammars 
Daniel Bauer
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        parse_table = { }

        #initialization
        for index in range(0,len(tokens)):
            tok = tokens[index]
            tup = tuple((tok,))
            key = (index,index+1)
            parse_table[key] = set()
            for t in self.grammar.rhs_to_rules[tup]:
                parse_table[key].add(t[0])

        #main loop
        for l in range(2,len(tokens)+1):
            for i in range(0,len(tokens)-l+1):
                j = i + l
                key_0 = (i,j)
                sym_set = set()
                for k in range(i+1,j):
                    key_1 = (i,k)
                    key_2 = (k,j)
                    M = set()
                    for rule_1 in parse_table[key_1]:
                        for rule_2 in parse_table[key_2]:
                            rule_tup = (rule_1, rule_2)
                            if rule_tup in self.grammar.rhs_to_rules:
                                for new_rule in self.grammar.rhs_to_rules[rule_tup]:
                                    M.add(new_rule[0])
                    sym_set = sym_set.union(M)
                
                parse_table[key_0] = sym_set
        
        if self.grammar.startsymbol in parse_table[(0,len(tokens))]:
            return True
        else:
            return False
       
    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        table = defaultdict(dict)
        probs = defaultdict(dict)

        #initialization
        for index in range(0,len(tokens)):
            tok = tokens[index]
            tup = tuple((tok,))
            key = (index,index+1)
            table[key] = { }
            for t in self.grammar.rhs_to_rules[tup]:
                table[key][t[0]] = tok #dictionary that stores backpointers
                probs[key][t[0]] = math.log2(t[2]) #dictionary that stores probs

        #main loop
        for l in range(2,len(tokens)+1):
            for i in range(0,len(tokens)-l+1):
                j = i + l
                key_0 = (i,j)
                for k in range(i+1,j):
                    key_1 = (i,k)
                    key_2 = (k,j)
                    for rule_1 in table[key_1]:
                        for rule_2 in table[key_2]:
                            rule_tup = (rule_1, rule_2)
                            if rule_tup in self.grammar.rhs_to_rules:
                                for new_rule in self.grammar.rhs_to_rules[rule_tup]:
                                    combined = math.log2(new_rule[2]) + probs[key_1][rule_1] + probs[key_2][rule_2]
                                    if not probs[key_0].get(new_rule[0]) or combined > probs[key_0][new_rule[0]]:
                                        probs[key_0][new_rule[0]] = combined
                                        table[key_0][new_rule[0]] = ((rule_1, i, k), (rule_2, k, j))
        return table, probs


def get_tree(chart, i,j,nt): 
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    if nt not in chart[(i,j)]:
        raise KeyError
    
    if isinstance(chart[(i, j)][nt], str):
        return (nt,chart[(i, j)][nt])
    
    l, r = chart[(i, j)][nt]

    l_tree = get_tree(chart, l[1], l[2], l[0])
    r_tree = get_tree(chart, r[1], r[2], r[0])

    return (nt, l_tree, r_tree)
 
       
if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file) 
        parser = CkyParser(grammar)

        toks = ['flights', 'from','miami', 'to', 'cleveland','.'] 
        print(parser.is_in_language(toks))

        table,probs = parser.parse_with_backpointers(toks)
        assert check_table_format(table)
        assert check_probs_format(probs)

        print(get_tree(table, 0, len(toks), grammar.startsymbol))
        
