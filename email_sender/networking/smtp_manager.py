# SMTP connection management and configuration
import smtplib
import random
import time
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from contextlib import contextmanager
from .smtp_health_checker import check_smtp_health
from config.config_loader import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SMTPServer:
    host: str
    port: int
    username: str
    password: str
    sender_email: str
    max_connections: int = 5
    timeout: int = 30
    use_ssl: bool = False
    use_tls: bool = True

class SMTPManager:
    def __init__(self):
        self.smtp_servers = self._load_servers()
        self.current_index = 0
        self.connection_pool = {}  # {server_id: [connection1, connection2]}
        
    def _load_servers(self) -> list[SMTPServer]:
        """Load and validate SMTP server configurations"""
        servers = []
        raw_configs = load_config().get('smtp_servers', [])
        
        for config in raw_configs:
            try:
                server = SMTPServer(
                    host=config['host'],
                    port=int(config['port']),
                    username=config['username'],
                    password=config['password'],
                    sender_email=config.get('sender_email', config['username']),
                    use_ssl=config.get('ssl', False),
                    use_tls=config.get('tls', True),
                    max_connections=int(config.get('max_connections', 5)),
                    timeout=int(config.get('timeout', 30))
                )
                servers.append(server)
            except (KeyError, ValueError) as e:
                logger.error(f"Invalid SMTP config: {e}")
                
        if not servers:
            raise ValueError("No valid SMTP configurations found")
        return servers

    @contextmanager
    def get_connection(self) -> smtplib.SMTP:
        """Context manager for handling SMTP connections with pooling"""
        server = self._get_healthy_server()
        connection = None
        
        try:
            # Try to get from pool first
            if server in self.connection_pool and self.connection_pool[server]:
                connection = self.connection_pool[server].pop()
                logger.debug(f"Reusing connection from pool for {server.host}")
            else:
                connection = self._create_connection(server)
                logger.info(f"Created new connection to {server.host}")
            
            yield connection
            
            # Return to pool if still valid
            if connection and not connection.noop()[0] == 250:
                logger.debug(f"Connection to {server.host} no longer valid, discarding")
                connection.quit()
            else:
                if server not in self.connection_pool:
                    self.connection_pool[server] = []
                self.connection_pool[server].append(connection)
                
        except Exception as e:
            logger.error(f"SMTP operation failed: {str(e)}")
            if connection:
                connection.close()
            raise
        finally:
            if connection and connection.sock is None:
                connection.close()

    def _get_healthy_server(self) -> SMTPServer:
        """Get next available healthy SMTP server with round-robin"""
        for _ in range(len(self.smtp_servers)):
            server = self.smtp_servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.smtp_servers)
            
            if check_smtp_health(server):
                return server
                
            logger.warning(f"SMTP server {server.host} failed health check")
            time.sleep(1)  # Brief pause before retrying
            
        raise ConnectionError("No healthy SMTP servers available")

    def _create_connection(self, server: SMTPServer) -> smtplib.SMTP:
        """Create new SMTP connection with proper configuration"""
        try:
            if server.use_ssl:
                conn = smtplib.SMTP_SSL(
                    host=server.host,
                    port=server.port,
                    timeout=server.timeout)
            else:
                conn = smtplib.SMTP(
                    host=server.host,
                    port=server.port,
                    timeout=server.timeout)
                
            if server.use_tls and not server.use_ssl:
                conn.starttls()
                
            conn.login(server.username, server.password)
            return conn
            
        except Exception as e:
            logger.error(f"Connection failed to {server.host}: {str(e)}")
            raise

    def test_all_servers(self):
        """Test connectivity for all configured servers"""
        results = {}
        for server in self.smtp_servers:
            try:
                with self.get_connection() as conn:
                    results[server.host] = conn.noop()[0] == 250
            except Exception as e:
                results[server.host] = False
                logger.error(f"Test failed for {server.host}: {str(e)}")
        return results

    def cleanup(self):
        """Clean up all connections in pool"""
        for server, connections in self.connection_pool.items():
            for conn in connections:
                try:
                    conn.quit()
                except:
                    pass
        self.connection_pool = {}