import socket
import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict
from netcore_server import TcpServer, TcpSession

logging.basicConfig(level=logging.INFO)

class ClientSession(TcpSession):
    def __init__(self, server):
        super().__init__(server)

    def connected(self):
        logging.info(f"Session {self.id()} connected")

    def disconnected(self):
        logging.info(f"Session {self.id()} disconnected")

class PolygonStatServer(TcpServer):
    def __init__(self, host: str, port: int):
        super().__init__(host, port)
        self.clean_timer = None
        self.current_count = float('-inf')

    def error(self, error: socket.error):
        logging.error(f"PolygonStatServer caught an error with code {error}")

    def create_session(self) -> TcpSession:
        return ClientSession(self)

    def do_clean_timer(self):
        sessions_to_remove = [session for session in self.sessions.values() if not session.connected()]
        for session in sessions_to_remove:
            session.close()
        if self.current_count != len(self.sessions):
            self.current_count = len(self.sessions)
            logging.info(f"Currently Connected: {self.current_count}")

    def run(self):
        self.clean_timer = threading.Timer(0, self.do_clean_timer)
        self.clean_timer.start()
        try:
            super().run()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        super().stop()
        self.clean_timer.cancel()

if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 5555

    server = PolygonStatServer(HOST, PORT)
    logging.info(f"Server listening on {HOST}:{PORT}")
    server.run()
