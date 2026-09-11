import logging


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        from flask import g, has_request_context

        if has_request_context():
            record.request_id = getattr(g, "request_id", "-")
        else:
            record.request_id = "-"

        return True


def configure_logging():
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | request_id=%(request_id)s | %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if not root_logger.handlers:
        root_logger.addHandler(logging.StreamHandler())

    for handler in root_logger.handlers:
        handler.setFormatter(formatter)
        handler.addFilter(RequestContextFilter())
