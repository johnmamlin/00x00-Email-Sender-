import os

class TextProcessors:

    def load_dictionary(self, dict_file="dictionary.txt"):
        words = []
        if os.path.exists(dict_file):
            with open(dict_file, "r") as f:
                words = [line.strip() for line in f if line.strip()]
    
        if not words:
        # Create default dictionary if file doesn't exist
            default_words = [
            "important", "urgent", "update", "notification", "alert", "news", "information",
            "special", "exclusive", "limited", "offer", "deal", "promotion", "sale",
            "john", "sarah", "mike", "lisa", "david", "anna", "robert", "emily",
            "support", "team", "service", "manager", "admin", "system", "security"
        ]
            with open(dict_file, "w") as f:
                for word in default_words:
                    f.write(word + "\n")
            words = default_words
            self.logger.info(f"Created default dictionary file: {dict_file}")
    
        return words