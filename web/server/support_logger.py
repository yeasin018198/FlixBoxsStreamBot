import logging
import sys
import traceback

SUPPORT = "https://t.me/AV_SUPPORT_GROUP"

# ANSI Colors for Terminal Highlighting
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    CYAN = "\033[96m"

class SupportFormatter(logging.Formatter):
    """
    Custom Logger to add Support Link and Box around errors
    """
    def format(self, record):
        # Standard Log Formatting
        log_msg = super().format(record)
        
        # Only modify if it's an ERROR or CRITICAL
        if record.levelno >= logging.ERROR:
            return self.add_support_box(log_msg)
        return log_msg

    def add_support_box(self, message):
        border = "=" * 60
        support_msg = (
            f"\n{Colors.RED}{border}\n"
            f"🛑 CRITICAL ERROR DETECTED\n"
            f"{border}{Colors.RESET}\n"
            f"{message}\n"
            f"{Colors.RED}-{border}{Colors.RESET}\n"
            f"{Colors.YELLOW}🛠  NEED HELP? FIX THIS ERROR HERE:{Colors.RESET}\n"
            f"{Colors.CYAN}👉 {SUPPORT} 👈{Colors.RESET}\n"
            f"{Colors.RED}{border}{Colors.RESET}\n"
        )
        return support_msg

def setup_support_logger():
    """
    Sets up the logger with the custom formatter
    """
    logger = logging.getLogger("WebavBot_Support")
    logger.setLevel(logging.INFO)

    # Console Handler (Terminal Output)
    c_handler = logging.StreamHandler(sys.stdout)
    
    # Apply the Custom Formatter
    c_format = SupportFormatter("%(asctime)s - %(levelname)s - %(message)s")
    c_handler.setFormatter(c_format)

    # Add Handler to Logger
    if not logger.handlers:
        logger.addHandler(c_handler)

    return logger
    
