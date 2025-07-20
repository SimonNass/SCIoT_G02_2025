import logging
from datetime import datetime, timedelta
from flask import current_app
from backend.extensions import db
from backend.models.models import Device
from backend.mqtt.utils.cacheUtils import remove_device_from_cache
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from backend.aiplaning.pddl_converter_main import run_planner_with_db_data
import atexit

mark_devices_offline_after_minutes = 60
delete_after_minutes = 180
run_planner_every_seconds = 60

def _mark_devices_offline():
    """
    Mark devices as offline if they haven't been seen for mark_devices_offline_after_hours hours or more.
    Runs every 30 minutes.
    """
    try:
        with current_app.app_context():
            # Calculate the threshold time (mark_devices_offline_after_hours hours ago)
            threshold_time = datetime.utcnow() - timedelta(minutes=mark_devices_offline_after_minutes)
            
            # Find devices that were last seen more than mark_devices_offline_after_hours hours ago and are currently online
            offline_devices = Device.query.filter(
                Device.last_seen < threshold_time,
                Device.is_online == True
            ).all()
            
            if offline_devices:
                # Mark them as offline
                for device in offline_devices:
                    device.is_online = False
                    logging.info(f"Marking device {device.device_id} as offline (last seen: {device.last_seen})")
                
                # Commit all changes at once
                db.session.commit()
                logging.info(f"Successfully marked {len(offline_devices)} devices as offline")
            else:
                logging.info("No devices to mark as offline")
                
    except Exception as e:
        logging.error(f"Error in mark_devices_offline cronjob: {str(e)}")
        # Only rollback if we're still within the app context
        try:
            with current_app.app_context():
                db.session.rollback()
        except RuntimeError:
            # If we can't get app context, just log the error
            logging.error("Could not rollback database session - no application context available")


def _cleanup_old_devices():
    """
    Delete devices that haven't been seen for {delete_after_hours} hours or more.
    Also removes them from the device cache.
    Runs every hour.
    """
    try:
        with current_app.app_context():
            # Calculate the threshold time (delete_after_hours hours ago)
            threshold_time = datetime.utcnow() - timedelta(minutes=delete_after_minutes)
            
            # Find devices that were last seen more than delete_after_hours hours ago
            old_devices = Device.query.filter(
                Device.last_seen < threshold_time
            ).all()
            
            if old_devices:
                device_ids_to_remove = []
                
                for device in old_devices:
                    device_ids_to_remove.append(device.device_id)
                    logging.info(f"Deleting old device {device.device_id} (last seen: {device.last_seen})")
                    
                    # Remove from cache first
                    try:
                        remove_device_from_cache(device.device_id)
                        logging.debug(f"Removed device {device.device_id} from cache")
                    except Exception as cache_error:
                        logging.warning(f"Failed to remove device {device.device_id} from cache: {cache_error}")
                    
                    # Delete from database
                    db.session.delete(device)
                
                # Commit all deletions at once
                db.session.commit()
                logging.info(f"Successfully deleted {len(old_devices)} old devices")
                
            else:
                logging.info("No old devices to cleanup")
                
    except Exception as e:
        logging.error(f"Error in cleanup_old_devices cronjob: {str(e)}")
        # Only rollback if app context is available 
        try:
            with current_app.app_context():
                db.session.rollback()
        except RuntimeError:
            logging.error("Could not rollback database session - no application context available")


def start_scheduler(app):
    """
    Initialize and start the APScheduler with the cronjobs
    """
    
    scheduler = BackgroundScheduler()
    
    # Wrapper functions that ensure app context is available
    def mark_devices_offline():
        with app.app_context():
            _mark_devices_offline()
    
    def cleanup_old_devices():
        with app.app_context():
            _cleanup_old_devices()

    def run_planning():
        with app.app_context():
            run_planner_with_db_data(True)
    
    # Job 1: Mark devices offline
    scheduler.add_job(
        func=mark_devices_offline,
        trigger=IntervalTrigger(minutes=mark_devices_offline_after_minutes),
        id='mark_devices_offline',
        name=f'Mark devices offline if not seen for {mark_devices_offline_after_minutes} minutes',
        replace_existing=True
    )
    
    # Job 2: Cleanup old devices
    scheduler.add_job(
        func=cleanup_old_devices,
        trigger=IntervalTrigger(minutes=delete_after_minutes),
        id='cleanup_old_devices',
        name=f'Delete devices not seen for {delete_after_minutes} minutes',
        replace_existing=True
    )

    # Job 3:
    scheduler.add_job(
         func=run_planning,
         trigger=IntervalTrigger(seconds=run_planner_every_seconds),
         id='run_planning',
         name=f'Runs AI Plannin every {run_planner_every_seconds} seconds',
         replace_existing=True
    )
    scheduler.start()
    logging.info("Device management scheduler started")
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
    return scheduler