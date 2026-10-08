import logging
import re

# Sensitive patterns to redact
REDACT_PATTERNS = [
    re.compile(r'(token["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.IGNORECASE),
    re.compile(r'(password["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.IGNORECASE),
    re.compile(r'(secret["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.IGNORECASE),
    re.compile(r"(Bearer\s+)([A-Za-z0-9_\-\.]+)", re.IGNORECASE),
    re.compile(r'(api_key["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.IGNORECASE),
]


class SecretRedactionFilter(logging.Filter):
    """Logging filter that masks sensitive tokens, passwords, and API keys."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.redact(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self.redact(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self.redact(str(v)) for v in record.args)
        return True

    @staticmethod
    def redact(text: str) -> str:
        redacted = text
        for pattern in REDACT_PATTERNS:
            redacted = (
                pattern.sub(r"\1***REDACTED***\3", redacted)
                if r"\3" in pattern.pattern
                else pattern.sub(r"\1***REDACTED***", redacted)
            )
        return redacted


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configures structured application logging with secret redaction."""
    logger = logging.getLogger("twinos")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Clear existing handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S"
        )
        handler.setFormatter(formatter)
        handler.addFilter(SecretRedactionFilter())
        logger.addHandler(handler)

    return logger


logger = setup_logging()
