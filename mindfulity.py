#!/usr/bin/env python2

import re
import sys

from collections import namedtuple

Rule = namedtuple('Rule',
                  ['domain',
                   'start_hour',
                   'start_min',
                   'end_hour',
                   'end_min',
                   'flag'])

def require_int_in_range(value, minval, maxval, fmt):
    try:
        v = int(value)
        assert v >= minval
        assert v <= maxval
    except:
        sys.exit(fmt)

def read_config_file(filename):
    # read config file into list of (linenumber, line) pairs
    lines = [(i, line.strip()) for i, line in enumerate(open(filename, 'r'))]

    # strip out comments
    comment_regex = r'\s*#.*$'
    lines = [(i, re.sub(comment_regex, '', line)) for i, line in lines]

    # strip out blank lines
    blank_regex = r'^\s*$'
    lines = [(i, line) for i, line in lines if not re.match(blank_regex, line)]

    # split all lines into fields
    lines = [(i, line.split()) for i, line in lines]

    # check that all lines have the correct number of fields
    correct_count = len(Rule._fields)
    for i, l in lines:
        actual_count = len(l)
        if actual_count != correct_count:
            msg = "{}:{}: Error: {} fields expected, but {} were found".format(
                filename, i, correct_count, actual_count)
            sys.exit(msg)

    # construct Rules from lines
    rules = [(i, Rule(*line)) for i, line in lines]

    # check that all times are valid
    valid_ranges = {'start_hour': (0, 23),
                    'end_hour': (0, 23),
                    'start_min': (0, 59),
                    'end_min': (0, 59)}

    human_names = {'start_hour': 'Start hour',
                   'end_hour': 'End hour',
                   'start_min': 'Start minute',
                   'end_min': 'End minute'}

    for field in valid_ranges.keys():
        bounds = valid_ranges[field]
        minval = bounds[0]
        maxval = bounds[1]
        name = human_names[field]
        for i, rule in rules:
            fmt = ("{}:{}: Error: the field {} needs to have a value" +
                   "in the range [{}, {}], but the given value was {{}}").format(
                       filename, i, field, minval, maxval)
            require_int_in_range(rule._asdict()[field], minval, maxval, fmt)

    # split day flags
    rules = frozenset.union(*
        {frozenset({(i, Rule(rule.domain,
                             rule.start_hour, rule.start_min,
                             rule.end_hour, rule.end_min,
                             flag))
                    for flag in rule.flag.split(',')}) for i, rule in rules})

    # check that all day flags are valid
    for i, rule in rules:
        if rule.flag != 'weekdays' and rule.flag != 'weekends':
            sys.exit("{}:{}: Error: 'flags' field contains the invalid flag {}".format(
                filename, i, rule.flag))

    # we have now done all syntax checking on config file, so we can drop the line numbers
    rules = [rule for i, rule in rules]

    # all times were represented by proper integers, so we can do the conversion without
    # checking agian
    rules = {Rule(r.domain,
                  int(r.start_hour), int(r.start_min),
                  int(r.end_hour), int(r.end_min),
                  r.flag)
             for r in rules}

    # return the set of all rules
    return rules

def read_hosts_file():
    # read hosts file into list of lines

    # strip out lines previously written by mindfulity

    # return the list of lines
    pass

def write_hosts_file(lines):
    # build a string from the list of lines

    # write the whole string at once into the hosts file
    pass

def normalize_rules(rules):
    # filter out all rules which are already in normal form
    normal_rules = {r for r in rules
                    if (r.start_hour, r.start_min) < (r.end_hour, r.end_min)}
    
    abnormal_rules = rules - normal_rules

    # create 'evening' and 'morning' rules for each rule not
    # in normal form
    morning_rules = {Rule(r.domain,
                          0, 0,
                          r.end_hour, r.end_min,
                          r.flag)
                     for r in rules}
    evening_rules = {Rule(r.domain,
                          r.start_hour, r.start_min,
                          23, 59,
                          r.flag)
                     for r in rules}

    # return the set of all normal-form rules
    return normal_rules | morning_rules | evening_rules

def pretty_print_rules(rules):
    rules = sorted(rules)
    for r in rules:
        print r


def get_active_rules(rules):
    # get the current time

    # filter out all rules which don't apply because it's the
    # wrong kind of day

    # filter out rules which start too late

    # filter out rules which end too early

    # return the set of all active rules
    pass

def lines_for_rules(rules):
    # get the set of all blocked domains
    domains = {rule.domain for rule in rules}

    # return a list of lines resolving blocked domains to localhost
    fmt = "127.0.0.1 {} # mindfulity"
    return [fmt.format(domain) for domain in domains]
