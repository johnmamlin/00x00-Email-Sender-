import os
import logging




def create_required_directories():
    """Create required directories for the enhanced functionality"""
    directories = ["images", "logos", "templates", "attachments"]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"[*] Created {directory} directory")

    if not os.path.exists("dictionary.txt"):
        sample_words = [
            "important", "urgent", "update", "notification", "alert", "news", "information",
            "special", "exclusive", "limited", "offer", "deal", "promotion", "sale",
            "john", "sarah", "mike", "lisa", "david", "anna", "robert", "emily",
            "support", "team", "service", "manager", "admin", "system", "security",
            "business", "company", "client", "customer", "account", "invoice", "payment"
        ]

        with open("dictionary.txt", "w") as f:
            for word in sample_words:
                f.write(word + "\n")
    print("[*] Created sample dictionary.txt file")