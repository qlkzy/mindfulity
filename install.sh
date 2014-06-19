#!/bin/bash

cp mindfulity.py /usr/local/bin/mindfulity
cp mindfulity.conf /usr/local/etc/mindfulity.conf
cp mindfulity.cron /etc/cron.d/mindfulity
chmod 755 /usr/local/bin/mindfulity
chmod 644 /usr/local/etc/mindfulity.conf
chmod 644 /etc/cron.d/mindfulity
