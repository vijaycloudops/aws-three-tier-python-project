import os
import json
import time
import boto3
import psycopg2
from flask import Flask, jsonify, render_template
from botocore.exceptions import BotoCoreError, ClientError

app = Flask(__name__)

SECRET_ARN = os.environ.get("DB_SECRET_ARN")
AWS_REGION = os.environ.get("AWS_REGION", "eu-west-1")

def get_db_config():
    """Read database credentials from Secrets Manager at runtime."""
    if not SECRET_ARN:
        raise RuntimeError("DB_SECRET_ARN environment variable is not set")
    client = boto3.client("secretsmanager", region_name=AWS_REGION)
    response = client.get_secret_value(SecretId=SECRET_ARN)
    return json.loads(response["SecretString"])

def get_connection():
    config = get_db_config()
    return psycopg2.connect(
        host=config["host"],
        port=int(config.get("port", 5432)),
        dbname=config["dbname"],
        user=config["username"],
        password=config["password"],
        connect_timeout=5,
        sslmode="require",
    )

def record_visit():
    """Create the counter table if needed and increment it."""
    last_error = None
    for attempt in range(5):
        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS app_visits (
                            id INTEGER PRIMARY KEY,
                            visit_count BIGINT NOT NULL
                        )
                    """)
                    cursor.execute("""
                        INSERT INTO app_visits (id, visit_count)
                        VALUES (1, 1)
                        ON CONFLICT (id)
                        DO UPDATE SET visit_count = app_visits.visit_count + 1
                        RETURNING visit_count
                    """)
                    count = cursor.fetchone()[0]
                connection.commit()
            return count
        except Exception as exc:
            last_error = exc
            time.sleep(2)
    raise RuntimeError(f"Database unavailable after retries: {last_error}")

@app.route("/")
def home():
    try:
        count = record_visit()
        return render_template("index.html", visit_count=count)
    except Exception as exc:
        app.logger.exception("Unable to reach database")
        return render_template("error.html", message=str(exc)), 503

@app.route("/health")
def health():
    # ALB liveness check. This intentionally checks the web process only.
    return jsonify(status="ok", service="flask-web"), 200

@app.route("/ready")
def ready():
    # Readiness check includes a real database connection.
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        return jsonify(status="ready", database="connected"), 200
    except (Exception, BotoCoreError, ClientError) as exc:
        app.logger.warning("Readiness check failed: %s", exc)
        return jsonify(status="not-ready", database="unavailable"), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
