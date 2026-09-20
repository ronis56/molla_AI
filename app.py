
import uuid
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import os
from flask import Flask, request, jsonify, render_template

from pipeline import agent_1_pipeline, post_facebook


# ============================================================
# CONFIG
# ============================================================

CHAT_TIMEOUT_SECONDS = float(os.environ.get("CHAT_TIMEOUT_SECONDS", "45"))
MAX_MESSAGE_LENGTH   = int(os.environ.get("MAX_MESSAGE_LENGTH", "4000"))
LOG_LEVEL            = os.environ.get("LOG_LEVEL", "INFO")


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)

log = logging.getLogger("mollaAI")


# ============================================================
# APP
# ============================================================

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

executor = ThreadPoolExecutor(max_workers=4)

# Serialises pipeline calls so the shared conversation stays consistent
conversation_lock = threading.Lock()


# ============================================================
# HELPERS
# ============================================================

def error_response(message, status=500, request_id=None):
    payload = {"error": message}
    if request_id:
        payload["request_id"] = request_id
    return jsonify(payload), status


def run_pipeline_locked(user_input):
    with conversation_lock:
        return agent_1_pipeline(user_input)


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# HEALTH
# ============================================================

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "timeout_seconds": CHAT_TIMEOUT_SECONDS,
    })


# ============================================================
# CHAT API
# ============================================================

@app.route("/api/chat", methods=["POST"])
def chat():

    request_id = uuid.uuid4().hex[:8]
    t0 = time.time()

    data = request.get_json(silent=True) or {}
    user_input = (data.get("message") or "").strip()

    if not user_input:
        log.warning("[%s] empty message", request_id)
        return error_response("No message provided", 400, request_id)

    if len(user_input) > MAX_MESSAGE_LENGTH:
        log.warning("[%s] message too long (%d chars)", request_id, len(user_input))
        return error_response("Message too long", 413, request_id)

    log.info("[%s] >> %s", request_id, user_input[:120])

    try:
        future = executor.submit(run_pipeline_locked, user_input)
        result = future.result(timeout=CHAT_TIMEOUT_SECONDS)

    except FutureTimeoutError:
        log.error("[%s] pipeline timeout after %.1fs", request_id, CHAT_TIMEOUT_SECONDS)
        return error_response(
            f"Request timed out after {CHAT_TIMEOUT_SECONDS:.0f}s",
            504,
            request_id,
        )

    except Exception as e:
        log.exception("[%s] pipeline error", request_id)
        return error_response(str(e) or "Pipeline error", 500, request_id)

    elapsed = time.time() - t0
    text = str(result or "").strip()

    if not text:
        log.warning("[%s] empty pipeline result (%.2fs)", request_id, elapsed)
        text = "I didn't get a response from the pipeline. Please try again."

    log.info("[%s] << (%d chars, %.2fs) %s",
             request_id, len(text), elapsed, text[:120])

    return jsonify({
        "response": text,
        "elapsed": round(elapsed, 2),
        "request_id": request_id,
    })


# ============================================================
# FACEBOOK — USER APPROVAL REQUIRED
# ============================================================

@app.route("/api/facebook/publish", methods=["POST"])
def facebook_publish():
    """Publish a Facebook post only after explicit UI approval."""
    request_id = uuid.uuid4().hex[:8]
    data = request.get_json(silent=True) or {}
    message = str(data.get("message") or "").strip()
    approved = data.get("approved") is True

    if not message:
        return error_response("No Facebook message provided", 400, request_id)

    if len(message) > MAX_MESSAGE_LENGTH:
        return error_response("Facebook message is too long", 413, request_id)

    if not approved:
        return error_response(
            "Facebook publishing requires explicit user approval.",
            403,
            request_id,
        )

    try:
        log.info("[%s] Facebook publish approved by user", request_id)
        result = post_facebook(message)

        return jsonify({
            "success": True,
            "response": str(result),
            "request_id": request_id,
        })

    except Exception as e:
        log.exception("[%s] Facebook publish error", request_id)
        return error_response(
            str(e) or "Facebook publishing failed",
            500,
            request_id,
        )


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    log.exception("unhandled 500: %s", e)
    return jsonify({"error": "Internal server error"}), 500


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    log.info("mollaAI server starting — timeout=%ss", CHAT_TIMEOUT_SECONDS)
    app.run(
        debug=False,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        threaded=True,
    )