import os


def load_smtp_servers(self, smtp_file):
        """Load SMTP servers from file"""
        smtp_servers = []
        if os.path.exists(smtp_file):
            with open(smtp_file, "r") as f:
                for line in f:
                    if line.strip() and not line.strip().startswith("#"):
                        parts = line.strip().split("|")
                        if len(parts) >= 4:
                            smtp_servers.append({
                                "server": parts[0],
                                "port": int(parts[1]),
                                "username": parts[2],
                                "password": parts[3]
                            })
        
        if not smtp_servers:
            self.logger.warning("No valid SMTP servers found in file. Using config defaults.")
            if self.config.get("smtp_server") and self.config.get("smtp_port"):
                smtp_servers.append({
                    "server": self.config.get("smtp_server"),
                    "port": int(self.config.get("smtp_port")),
                    "username": self.config.get("username"),
                    "password": self.config.get("password")
                })
        return smtp_servers

def get_next_smtp(self):
        """Get the next SMTP server in rotation"""
        if not self.smtp_servers:
            self.logger.error("No SMTP servers available")
            return None
            
        smtp_info = self.smtp_servers[self.current_smtp_index]
        self.current_smtp_index = (self.current_smtp_index + 1) % len(self.smtp_servers)
        return smtp_info
