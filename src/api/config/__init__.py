"""The config api module."""

import src.wrappers as wrappers
from src.imported.config_handler import load_config, save_config_file


@wrappers.jwt
@wrappers.endpoint
@wrappers.stats
@wrappers.logger('Retrieving config file.')
@wrappers.injector
def get(handler, log, config):
	log.debug('config_path: {}'.format(config.config_path))
	log.info('Loading config.')

	config_file = load_config(config.config_path)

	log.info('Checking config file.')
	if not config_file:
		raise IOError('Cannot load config file with path: {0}'.format(config.config_path))

	handler.add({ 'config': config_file })


@wrappers.jwt
@wrappers.endpoint
@wrappers.stats
@wrappers.logger('Updating config file entry.')
@wrappers.injector
def put(row, handler, log, config):
	log.info('Parsing row parameter.')

	category = row[0]
	field = row[1]
	value = row[2]

	log.debug('config_path: {}'.format(config.config_path))
	log.info('Loading config.')

	updated_conf_dict = load_config(config.config_path)

	oldValue = updated_conf_dict[category][field]
	updated_conf_dict[category][field] = value

	log.info('Saving config file.')
	if save_config_file(config.config_path, updated_conf_dict):
		handler.add({ 'output': 'Overwritten {0}:{1}:{2} as {3}'.format(category, field, oldValue, value) })
		handler.set_status(204)
	else:
		raise IOError('Unable to write {0}:{1}:{2} to config file'.format(category, field, value))
