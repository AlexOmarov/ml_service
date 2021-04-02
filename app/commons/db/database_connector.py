import configparser
import logging
import os

from app.commons.singleton.singleton_meta import SingletonMeta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnector(metaclass=SingletonMeta):
    db_properties = {}

    def __init__(self):
        """Init the database connection"""

        logger.info("Starting up the JDBC connection: ")

        config = configparser.ConfigParser()
        config.read("app/resources/db_properties.ini")
        db_prop = config['postgresql']
        self.db_properties['username'] = db_prop['username']
        self.db_properties['password'] = db_prop['password']
        self.db_properties['url'] = db_prop['url']
        self.db_properties['driver'] = db_prop['driver']
        self.db_properties['partitions'] = 2 * 2
        self.db_properties["lowerBound"] = 0
