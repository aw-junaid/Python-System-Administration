#!/usr/bin/env python3
"""
remote_log_sender.py
-----------------------
Sends log records to a remote server over the network using
logging.handlers.SocketHandler (TCP). This is the standard Python
mechanism for shipping logs to a central logging server.

This script includes BOTH:
  1) A simple demo TCP server that receives and prints logs
  2) A client that sends log messages to that server

Usage:
    # Terminal 1 - start the receiving server
    python3 remote_log_sender.py --mode server --port 9020

    # Terminal 2 - run the client to send sample logs
    python3 remote_log_sender.py --mode client --host 127.0.0.1 --port 9020

Note: For real production use, point --host/--port at your actual
central logging server (e.g. rsyslog, Logstash, Graylog) and secure
the connection (e.g. via a VPN or TLS-terminating proxy) since
SocketHandler by itself sends data unencrypted.
"""

import argparse
import logging
import logging.handlers
import pickle
import socketserver
import struct


def run_server(host, port):
    class LogRecordStreamHandler(socketserver.StreamRequestHandler):
        def handle(self):
            while True:
                chunk = self.connection.recv(4)
                if len(chunk) < 4:
                    break
                slen = struct.unpack(">L", chunk)[0]
                chunk = self.connection.recv(slen)
                while len(chunk) < slen:
                    chunk += self.connection.recv(slen - len(chunk))
                obj = pickle.loads(chunk)
                record = logging.makeLogRecord(obj)
                print(f"[REMOTE LOG] {record.levelname}: {record.getMessage()}")

    class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
        allow_reuse_address = True

    server = LogRecordSocketReceiver((host, port), LogRecordStreamHandler)
    print(f"Log server listening on {host}:{port} (Ctrl+C to stop)")
    server.serve_forever()


def run_client(host, port):
    logger = logging.getLogger("remote_log_sender_client")
    logger.setLevel(logging.DEBUG)

    socket_handler = logging.handlers.SocketHandler(host, port)
    logger.addHandler(socket_handler)

    logger.info("Client started - sending sample log messages")
    logger.warning("This is a sample warning sent to the remote server")
    logger.error("This is a sample error sent to the remote server")
    print(f"Sent 3 sample log messages to {host}:{port}")


def main():
    parser = argparse.ArgumentParser(description="Send/receive logs over TCP to a remote server")
    parser.add_argument("--mode", choices=["server", "client"], required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9020)
    args = parser.parse_args()

    if args.mode == "server":
        run_server(args.host, args.port)
    else:
        run_client(args.host, args.port)


if __name__ == "__main__":
    main()
