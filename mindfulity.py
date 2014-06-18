#!/usr/bin/env python2

import re
import sys
import time

from collections import namedtuple

# comment signature for /etc/hosts lines added by this program
SIGNATURE = 'mindfulity'

# weekend days days of week are 0-indexed starting from Monday
WEEKEND_DAYS = {5, 6}

# location of the config file
CONFIG_FILE = '/etc/mindfulity.conf'


Rule = namedtuple('Rule',
                  ['domain',
                   'start_hour',
                   'start_min',
                   'end_hour',
                   'end_min',
                   'days'])

def require_int_in_range(value, minval, maxval, fmt):
    try:
        v = int(value)
        assert v >= minval
        assert v <= maxval
    except:
        sys.exit(fmt.format(value))

def read_config_file(filename):
    # read config file into list of (linenumber, line) pairs
    #
    # we carry the line number throughout this function, so we can
    # tell the user the location of any errors
    lines = [(i+1, line.strip()) for i, line in enumerate(open(filename, 'r'))]

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
    rules = {(i, Rule(*line)) for i, line in lines}

    # check that all times are valid
    valid_ranges = {'start_hour': (0, 23),
                    'end_hour': (0, 24),
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
            fmt = ("{}:{}: Error: the field {} needs to have a value " +
                   "in the range [{}, {}], but the given value was {{}}").format(
                       filename, i, field, minval, maxval)
            require_int_in_range(rule._asdict()[field], minval, maxval, fmt)

    # split days
    rules = {(i, Rule(r.domain, r.start_hour, r.start_min,
                      r.end_hour, r.end_min, tuple(r.days.split(','))))
             for i, r in rules}

    # check that all days are valid
    for i, rule in rules:
        for d in rule.days:
            fmt = "{}:{}: Error: invalid day {{}}".format(filename, i)
            require_int_in_range(d, 0, 6, fmt)

    # we have now done all syntax checking on config file, so we can drop the line numbers
    rules = [rule for i, rule in rules]

    # all times were represented by proper integers, so we can do the conversion without
    # checking agian
    rules = {Rule(r.domain,
                  int(r.start_hour), int(r.start_min),
                  int(r.end_hour), int(r.end_min),
                  r.days)
             for r in rules}

    # all days were represented by proper integers, so we can do this conversion without
    # checking again
    rules = {Rule(r.domain, r.start_hour, r.start_min,
                  r.end_hour, r.end_min, tuple((int(d) for d in r.days)))
             for r in rules}

    # return the set of all rules
    return rules

def read_hosts_file():
    # read hosts file into list of lines
    #
    # not really worth being able to customize an option that would have been
    # the same on every unix everywhere 30 years ago
    lines = [line for line in open('/etc/hosts', 'r')]

    # strip out lines previously written by mindfulity
    lines = [line for line in lines if not line.endswith("# {}\n".format(SIGNATURE))]

    # return the list of lines
    return lines

def write_hosts_file(lines):
    # build a string from the list of lines
    contents = ''.join(lines)

    # write the whole string at once into the hosts file
    with open('/etc/hosts', 'w') as f:
        f.write(contents)

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
                          r.days)
                     for r in rules}
    evening_rules = {Rule(r.domain,
                          r.start_hour, r.start_min,
                          23, 59,
                          r.days)
                     for r in rules}

    # return the set of all normal-form rules
    return normal_rules | morning_rules | evening_rules

def pretty_print_rules(rules):
    rules = sorted(rules)
    for r in rules:
        print r


def get_active_rules(rules):
    # get the current time
    now = time.localtime()
    hh  = now.tm_hour
    mm  = now.tm_min
    dow = now.tm_wday

    # filter out all rules which don't apply because it's the
    # wrong day
    rules = {r for r in rules if dow in r.days}

    # filter out rules which start too late
    rules = {r for r in rules if (r.start_hour, r.start_min) <= (hh, mm)}

    # filter out rules which end too early
    rules = {r for r in rules if (hh, mm) < (r.end_hour, r.end_min)}

    # return the set of all active rules
    return rules

def lines_for_rules(rules):
    # get the set of all blocked domains
    domains = {rule.domain for rule in rules}

    # return a list of lines resolving blocked domains to localhost
    fmt = "127.0.0.1\t{} # mindfulity\n"
    return [fmt.format(domain) for domain in domains]


if __name__ == '__main__':
    if len(sys.argv) < 2:
        # default: update rules
        hosts = read_hosts_file()
        try:
            rules = normalize_rules(read_config_file(CONFIG_FILE))
            active = get_active_rules(rules)
            lines = lines_for_rules(active)
            write_hosts_file(hosts + lines)
        except:
            # if any of the above fails, clear all the blocks
            write_hosts_file(hosts)
            raise
    elif sys.argv[1] == 'check':
        # check that the config file is correct
        r = read_config_file(CONFIG_FILE)
        pretty_print_rules(r)
    elif sys.argv[1] == 'clear':
        # clear all blocks
        write_hosts_file(read_hosts_file())
    else:
        sys.exit("Unknown command {}".format(sys.argv[1]))
