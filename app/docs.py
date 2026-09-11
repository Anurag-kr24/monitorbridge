from flasgger import Swagger


def configure_swagger(app):
    return Swagger(
        app,
        config={
            "specs": [
                {
                    "endpoint": "openapi",
                    "route": "/api/openapi.json",
                    "rule_filter": lambda rule: True,
                    "model_filter": lambda tag: True,
                }
            ],
            "specs_route": "/api/docs/", "headers": [],
        },
        template={
            "swagger": "2.0",
            "info": {
                "title": "MonitorBridge API",
                "description": "Monitoring telemetry and incident management API",
                "version": "1.0.0",
            },
            "basePath": "/api",
        },
    )
