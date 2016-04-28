import os
import ConfigParser


CONFIG_FILE_NAME = 'config.ini'
"""str: Configuration file name
Config files are searched inside module directory and current working directory, and then merged
Current working directory config values have priority
See: get_config_path() and get_default_config_path()
"""


def get(section, param=None):
    """Get given param value, or all params from config section

    Args:
        section (str) Config section name
        param (str=None) Parameter name from given section (if None, return all section params)

    Returns:
        (str or bool or int or float) or (dict of (str: str or bool or int or float))

    Example:
        from twiwri import config
        config.get('mysection')         -> {'foo': 'bar', 'baz': 42, 'qux': True}
        config.get('mysection', 'foo')  -> 'bar'
    """
    if param is None:
        return get_section(section)
    else:
        return get_param(section, param)


def get_param(section, param):
    """Get given param value from config section

    Args:
        section (str) Config section name
        param (str) Section parameter name

    Returns:
        str or bool or int or float

    Raises:
        ValueError: Config section not found
        ValueError: Config param not found in section
        Exception: Cannot get config param for some other reason
    """
    try:
        value = get_parser().get(section, param)
    except ConfigParser.NoSectionError:
        raise ValueError('Config section "%s" not found' % section)
    except ConfigParser.NoOptionError:
        raise ValueError('Config param "%s" not found in section "%s"' % (param, section))
    except BaseException as ex:
        raise Exception('Cannot get config param value: %s' % ex)

    return value


def get_section(section):
    """Get all params from config section as dict

    Args:
        section (str) Config section name

    Returns:
        dict of (str: str or bool or int or float): {'foo': 'bar', 'baz': 42, 'qux': True}

    Raises:
        ValueError: Config section not found
        Exception: Cannot get config section for some other reason
    """
    try:
        params = dict(get_parser().items(section))
    except ConfigParser.NoSectionError:
        raise ValueError('Config section "%s" not found' % section)
    except BaseException as ex:
        raise Exception('Cannot get config param value: %s' % ex)

    return params


def save_param(section, param, value):
    """Set given param value and save results back to config file

    Args:
        section (str) Config section name
        param (str) Parameter name
        value (str or bool or int or float) New value for the parameter given

    Aliases:
        save
        set_param

    Raises:
        Exception: Cannot create config parser instance
        ValueError: Wrong config section name
        Exception: Cannot create config section for some other reason
        Exception: Cannot set config param value
        IOError: Cannot open config file for writing
        IOError: Cannot write config file
        Warning: Cannot close config file descriptor
    """
    # Create parser instance
    try:
        parser = get_parser()
    except BaseException as ex:
        raise Exception('Cannot create config parser instance: %s' % ex)

    # Create section if not exists
    if not parser.has_section(section):
        try:
            parser.add_section(section)
        except ValueError as ex:
            raise ValueError('Wrong config section name: "%s": %s' % (section, ex))
        except BaseException as ex:
            raise Exception('Cannot config create section: %s' % ex)

    # Save new value for the parameter
    try:
        parser.set(section, param, value)
    except BaseException as ex:
        raise Exception('Cannot set config param value: %s' % ex)

    # Open config file for writing
    try:
        fd = open(get_config_path(), 'wb')
    except BaseException as ex:
        raise IOError('Cannot open config file for writing: %s' % ex)

    # Write config file
    try:
        parser.write(fd)
    except BaseException as ex:
        raise IOError('Cannot write config file: %s' % ex)

    # Close file descriptor
    try:
        fd.close()
    except BaseException as ex:
        raise Warning('Cannot close config file descriptor: %s' % ex)

save = set_param = save_param
"""Aliases for `save_param` method"""


def get_parser():
    """Read and merge configuration files, then return parser instance

    Returns:
        ConfigParser.RawConfigParser

    Raises:
        Exception: Cannot read configuration file
    """
    config = ConfigParser.RawConfigParser()

    try:
        config.read([get_default_config_path(), get_openshift_config_path(), get_config_path()])
    except BaseException as ex:
        raise IOError('Cannot read configuration file: %s' % ex)

    return config


def get_config_path():
    """Get configuration file path (searched in current working directory)"""
    return os.path.join(os.getcwd(), CONFIG_FILE_NAME)


def get_openshift_config_path():
    """Get OpenShift configuration file path (searched in app-root/data/ directory)"""
    return os.path.join(os.getcwd(), 'app-root/data', CONFIG_FILE_NAME)


def get_default_config_path():
    """Get default configuration file path (searched in module directory)"""
    return os.path.join(os.path.dirname(__file__), CONFIG_FILE_NAME)
