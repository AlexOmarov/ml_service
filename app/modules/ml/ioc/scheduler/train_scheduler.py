import atexit
import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from app.modules.ml.ioc.service.train_service import TrainService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

seconds = 60


class TrainScheduler:
    service: TrainService
    scheduler: BackgroundScheduler = BackgroundScheduler()

    def __init__(self, service: TrainService):
        """Init scheduler"""

        logger.info("Starting up the Train Engine: ")
        self.service = service
        self.scheduler.add_job(func=service.train, trigger="interval", seconds=seconds, next_run_time=datetime.now())
        # Shut down the scheduler when exiting the app
        atexit.register(lambda: self.scheduler.shutdown())

    def start(self):
        self.scheduler.start()
