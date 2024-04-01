import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import socket
import threading
import signal
from contextlib import contextmanager

# Assuming ConfigurationManager, MySQLConnectionManager, PolygonStatServer, and EncounterManager
# are custom classes or modules you need to implement in Python as they are specific to the original application.

# Setup logging
logging.basicConfig(level=logging.DEBUG if ConfigurationManager.Shared.Config.Debug.Debug else logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(sys.stdout),
                        TimedRotatingFileHandler('logs/main.log', when="D", interval=1)
                    ])
logger = logging.getLogger(__name__)

title = "PolygonStats v" + "VERSION"  # Replace 'VERSION' with the actual version of your application
logger.info(title)

# Start HTTP server if enabled
http_server = None
if ConfigurationManager.Shared.Config.Http.Enabled:
    http_server = HttpServer(ConfigurationManager.Shared.Config.Http.Port)  # Assuming HttpServer is a custom class you need to implement

# Initialize database if enabled
if ConfigurationManager.Shared.Config.MySql.Enabled:
    manager = MySQLConnectionManager()  # Assuming MySQLConnectionManager is a custom class you need to implement
    # Assuming the following methods are part of your custom implementation
    migrator = manager.get_context().database.get_service('migrator')  # Placeholder for actual implementation
    migrator.migrate()
    manager.get_context().database.ensure_created()
    manager.get_context().save_changes()

logger.info(f"TCP server port: {ConfigurationManager.Shared.Config.Backend.Port}")

# Create and start the TCP server
server = PolygonStatServer('0.0.0.0', ConfigurationManager.Shared.Config.Backend.Port)  # Assuming PolygonStatServer is a custom class you need to implement
logger.info("Server starting...")
server.start()
logger.info("Done!")
logger.info("Use CTRL+C to close the software!")

# Graceful shutdown handling
exit_event = threading.Event()

def signal_handler(signum, frame):
    exit_event.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

exit_event.wait()

# Stop the server
logger.info("Server stopping...")
server.stop()
EncounterManager.shared.dispose()  # Assuming EncounterManager is a custom class you need to implement
if http_server is not None:
    http_server.stop()
logger.info("Done!")


