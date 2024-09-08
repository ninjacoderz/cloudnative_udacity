from argparse import ArgumentParser

from aiohttp.web import Application
from aiohttp_jinja2 import setup as setup_jinja
from jinja2.loaders import PackageLoader
from trafaret_config import commandline

from sqli.middlewares import session_middleware, csrf_middleware, error_middleware
from sqli.schema.config import CONFIG_SCHEMA
from sqli.services.db import setup_database
from sqli.services.redis import setup_redis
from sqli.utils.jinja2 import csrf_processor, auth_user_processor
from .routes import setup_routes


def init(argv):
    ap = ArgumentParser()
    commandline.standard_argparse_options(ap, default_config='./config/dev.yaml')
    options = ap.parse_args(argv)

    # 1. Missing Configuration Validation
    # The configuration loaded with commandline.config_from_options(options, CONFIG_SCHEMA) may not be validated properly. While CONFIG_SCHEMA is presumably used for validation, it's important to ensure that the configuration is validated against all required schema fields and constraints.

    # Solution: Ensure that CONFIG_SCHEMA is comprehensive and includes validation for all critical configuration aspects. For instance, check that required fields are present and values are within expected ranges.

    # # Assuming CONFIG_SCHEMA is a trafaret_config schema
    # from trafaret_config import ConfigError

    # try:
    #     config = commandline.config_from_options(options, CONFIG_SCHEMA)
    # except ConfigError as e:
    #     raise ValueError(f"Configuration error: {e}")
    
    config = commandline.config_from_options(options, CONFIG_SCHEMA)

    # 2. Hardcoded Debug Mode
    # The Application instance is created with debug=True. Leaving debug mode enabled in a production environment can expose sensitive information and provide attackers with more detailed error messages and stack traces.
    # Solution: Configure the debug mode based on the environment. For instance, use a configuration value to determine whether debugging should be enabled.
    # debug = config.get('debug', False) then replace debug=True, to  debug=debug,

    app = Application(
        debug=True,
        middlewares=[
            session_middleware,
            csrf_middleware,
            error_middleware,
        ]
    )

    # 3. Lack of Error Handling in Middleware Setup
    # The middlewares (session_middleware, csrf_middleware, error_middleware) are added without any checks or validation of their configuration or functionality. If these middlewares are not configured correctly or if they fail to initialize properly, they could introduce security vulnerabilities.

    # Solution: Implement error handling and logging during the middleware setup to catch and handle potential issues.


    # try:
    #     app.middlewares.extend([
    #         session_middleware,
    #         csrf_middleware,
    #         error_middleware,
    #     ])
    # except Exception as e:
    #     # Log the error and handle accordingly
    #     print(f"Error while setting up middlewares: {e}")
    #     raise

    app['config'] = config

    setup_jinja(app, loader=PackageLoader('sqli', 'templates'),
                context_processors=[csrf_processor, auth_user_processor],
                autoescape=True)
    setup_database(app)
    setup_redis(app)
    setup_routes(app)

    return app