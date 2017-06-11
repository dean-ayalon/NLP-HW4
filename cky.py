from PCFG import PCFG
import math
from collections import defaultdict


def load_sents_to_parse(filename):
    sents = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line:
                sents.append(line)
    return sents


def get_cky_parse_tree(sent, bp, i, j, symbol):
    left, right, split_index = bp[i][j][symbol]

    if left is None and right is None:  # terminal
        return "(" + symbol + " " + sent[i] + ")"

    if left is None:                    # Unary Rules
        return "(" + symbol + " " + get_cky_parse_tree(sent, bp, i, j, right) + ")"

    return "(" + symbol + " " + get_cky_parse_tree(sent, bp, i, split_index, left) + " " \
                        + get_cky_parse_tree(sent, bp, split_index + 1, j, right) + ")"


def cky(pcfg, sent):
    sent = sent.split()

    # Initialization
    pi = defaultdict(lambda: defaultdict(dict))
    bp = defaultdict(lambda: defaultdict(dict))

    for pre_terminal in pcfg.get_pre_terminals():
        for i in range(len(sent)):
            pi[i][i][pre_terminal] = 0
            for r, w in pcfg.get_rules_for_symbol(pre_terminal):
                if len(r) == 1:  # for unary rules
                    if r[0] == sent[i]:
                        pi[i][i][pre_terminal] = w / pcfg.get_sum_for_symbol(pre_terminal)
                        bp[i][i][pre_terminal] = [None, None, -1]
    # handle unary rules
    for i in range(len(sent)):
        while True:
            can_continue = False
            for non_terminal in pcfg.get_all_lhs():
                best_prob = pi.get(i, {}).get(i, {}).get(non_terminal, 0)       # Current probability
                for r, w in pcfg.get_rules_for_symbol(non_terminal):
                    if len(r) == 1:
                        rule_prob = w / pcfg.get_sum_for_symbol(non_terminal)
                        branch_prob = pi.get(i, {}).get(i, {}).get(r[0], 0)
                        total_prob = rule_prob * branch_prob
                        if total_prob > best_prob:
                            best_prob = total_prob
                            pi[i][i][non_terminal] = total_prob
                            bp[i][i][non_terminal] = [None, r[0], -1]
                            can_continue = True
            if not can_continue:
                break
    # main
    for j in range(1, len(sent)):
        for i in range(max(j-1, 0), -1, -1):
            for non_terminal in pcfg.get_all_lhs():
                pi[i][j][non_terminal] = 0
                best_prob = 0
                for s in range(i, j):
                    for r, w in pcfg.get_rules_for_symbol(non_terminal):
                        if len(r) > 1:  # No need to check unary rules
                            rule_prob = w / pcfg.get_sum_for_symbol(non_terminal)
                            left_branch_prob = pi.get(i, {}).get(s, {}).get(r[0], 0)
                            right_branch_prob = pi.get(s+1, {}).get(j, {}).get(r[1], 0)
                            total_prob = rule_prob * left_branch_prob * right_branch_prob
                            if total_prob > best_prob:
                                best_prob = total_prob
                                pi[i][j][non_terminal] = total_prob
                                bp[i][j][non_terminal] = [r[0], r[1], s]

            # Checking Unary Rules for current cell
            while True:
                can_continue = False
                for non_terminal in pcfg.get_all_lhs():
                    best_prob = pi.get(i, {}).get(j, {}).get(non_terminal, 0)
                    for r, w in pcfg.get_rules_for_symbol(non_terminal):
                        if len(r) == 1:
                            rule_prob = w / pcfg.get_sum_for_symbol(non_terminal)
                            branch_prob = pi.get(i, {}).get(j, {}).get(r[0], 0)
                            total_prob = rule_prob * branch_prob
                            if total_prob > best_prob:
                                best_prob = total_prob
                                pi[i][j][non_terminal] = total_prob
                                bp[i][j][non_terminal] = [None, r[0], -1]
                                can_continue = True
                if not can_continue:
                    break

    if pi[0][len(sent)-1]["ROOT"] == 0:
        return "FAILED TO PARSE!"

    return get_cky_parse_tree(sent, bp, 0, len(sent)-1, "ROOT")


if __name__ == '__main__':
    import sys
    pcfg = PCFG.from_file_assert_cnf(sys.argv[1])
    sents_to_parse = load_sents_to_parse(sys.argv[2])
    for sent in sents_to_parse:
        print cky(pcfg, sent)
