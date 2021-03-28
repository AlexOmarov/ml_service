from app.commons.singleton.singleton_meta import SingletonMeta
from app.ml.service.train_service import TrainService
import atexit

from apscheduler.schedulers.background import BackgroundScheduler
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainScheduler(metaclass=SingletonMeta):
    service: TrainService
    scheduler: BackgroundScheduler

    def __init__(self, service):
        """Init scheduler
        """

        logger.info("Starting up the Train Engine: ")
        self.service = service
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=service.train(), trigger="interval", seconds=3600)
        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())
        scheduler.start()
