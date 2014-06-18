# mindfulity

`mindfulity` is a program to block specified servers within defined
time ranges.

## Installation

`mindfulity` requires Python 2 (tested on Python 2.7). If Python is
not currently installed on your system, you should be able to install
it through your package manager. On a Debian-based system (including
Ubuntu and Mint), execute the command:

    sudo apt-get install python

Then, change into the directory into which you installed `mindfulity`,
and run:

    sudo ./install.sh

This will install the `mindfulity` script into `/usr/local/bin/mindfulity`,
the configuration file into `/usr/local/etc/mindfulity.conf`, and a
crontab fragment to run mindfulity into `/etc/cron.d`.

## Quick Start

To use the program, you will want to define some blocking rules. Run

    sudo nano /usr/local/etc/mindfulity.conf

(replacing `nano` with your preferred editor).

Reading the comments, you can probably copy and modify one of the example
rules to suit your needs.

## Configuration

Each line in the configuration file is either:

- A blank line or comment (starting with `#`), which is ignored
- A rule

A rule consists of six fields:

- The domain to block
- The hour and minute at which to start blocking 
  (these are separate fields)
- The hour and minute at which to stop blocking
  (these are separate fields)
- The day types on which to block

So a single rule looks something like this:

    example.com 19 00 08 15 weekdays

Taking that apart:

`example.com` is the domain to block.

`19` is the hour-part of when to start blocking

`00` is the minute-part of when to start blocking

Taken together, those give 19:00 (7pm)

`08` and `15` are similarly the hour and minute part
of when to stop blocking (8:15am).

`weekdays` specifies that the rule should only apply on
weekdays (Monday-Friday). You could also write `weekends`,
to specify that the rule only applies on Saturday and
Sunday, or `weekdays,weekends`, to specify that the rule
applies to all days of the week.

For more examples, see the comments in the provided
configuration file.

## Cron setup

Each time the script is run, it applies the blocks
that should be currently active. To keep these up-to-date,
the script needs to be regularly re-run.

This is accomplished automatically by a cron job, specified
by the crontab fragment in `mindfulity.cron`, which is copied
to `/etc/cron.d/mindfulity` by the install script.

The provided crontab fragment will apply the rules every
fifteen minutes.

## Startup setup



## Troubleshooting

If you think that the script is not working correctly,
the first thing to check is that there are no problems
with the configuration file. Try running

    mindfulity check

That will read the configuration file, and print out
all the rules it finds. If there are any syntax errors
in the file, this will print out an error message with
a brief description of the error, and the line number
on which it was found.

If that looks good, try running

    sudo mindfulity

That will apply the currently-active rules. If the blocking
behaviour is wrong before running this command, but correct
afterwards, then the cron job is not running the script at
the approppriate time---see above, in the section "Cron setup".

Finally, you can look in the file `/etc/hosts`. This is
the file that mindfulity modifies to block particular
domains. If blocks should be currently active, there
should be a line for each domain to be blocked, which
ends with a comment containing just `mindfulity`. So if you
were blocking `example.com`, there would be a line

    127.0.0.1   example.com # mindfulity

At the end of `/etc/hosts`.

If you are having trouble with mindfulity, you can run

    sudo mindfulity clear

to remove any rules that mindfulity has applied. This
is also what mindfulity will do if it is run automatically
and encounters an error with the configuration file.

Of course, if mindfulity is being run by a cron job, that will
quickly revert the situation back to that specified by the
configuration file unless you disable it.
