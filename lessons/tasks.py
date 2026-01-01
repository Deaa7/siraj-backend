from celery import shared_task
from videos.models import Videos
import logging
from services.backblaze_bucket_manager import delete_video_from_bucket
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def delete_video_from_cloud_and_db(self, video_public_id):
    try:
        video = Videos.objects.get(public_id=video_public_id)
        # logger.info(f"STARTED: Deleting video {video.name}")
        # logger.info(f"STARTED: Deleting video url {video.url}")
        if video is None:
            return
        delete_video_from_bucket(video.url)
        # logger.info(f"COMPLETED: Deleted video {video_public_id} from cloud")
        video.delete()
        # logger.info(f"COMPLETED: Deleted video {video_public_id} from database")
    except Exception as exc:
        # Retry if Backblaze is down or network fails
        # logger.error(f"ERROR: Failed to delete video {video_public_id}: {exc}")
        raise self.retry(exc=exc, countdown=60) # Retry after 1 minute