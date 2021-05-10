import atexit
import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from app.modules.ml import ioc
from app.modules.ml.service.train_service import TrainService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

service: TrainService = ioc.get_bean(TrainService.__class__.__name__)


class TrainScheduler:
    scheduler: BackgroundScheduler

    def __init__(self):
        """Init scheduler"""

        logger.info("Starting up the Train Engine: ")
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=service.train, trigger="interval", seconds=15, next_run_time=datetime.now())
        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())
        scheduler.start()
