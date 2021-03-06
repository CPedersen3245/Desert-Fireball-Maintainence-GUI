from flask import current_app
from time import sleep
from os import walk

import src.wrappers as wrappers
from src.console import console
from .partitions import disk_partitions


# TODO[BUG]: Need to disk_partitions if any drives are to be powered on / off. Currently just times out and returns the same result.
@wrappers.logger('Polling for drive changes.')
@wrappers.injector
def _poll(log, check_for_increase):
	num_to_change = len(current_app.config['DRIVES'])
	initial = len(next(walk('/sys/block'))[1])
	current = len(next(walk('/sys/block'))[1])
	time = 0
	timeout = 30
	change_detected = False

	if check_for_increase:
		expected = initial + num_to_change
	else:
		expected = initial - num_to_change

	while time < timeout and not change_detected:
		sleep(1)

		time = time + 1
		current = len(next(walk('/sys/block'))[1])

		if expected == current:
			change_detected = True

	sleep(1)
	log.info('{} drives detected.'.format(current))


@wrappers.jwt
@wrappers.endpoint
@wrappers.stats
@wrappers.logger('Turning on external drives.')
@wrappers.injector
def on(handler):
	console('python /opt/dfn-software/enable_ext-hd.py')

	_poll(check_for_increase = True)

	handler.add({ 'partitions': disk_partitions() })


@wrappers.jwt
@wrappers.endpoint
@wrappers.stats
@wrappers.logger('Turning off external drives.')
@wrappers.injector
def off(handler):
	console('python /opt/dfn-software/disable_ext-hd.py')

	_poll(check_for_increase = False)

	handler.add({ 'partitions': disk_partitions() })
