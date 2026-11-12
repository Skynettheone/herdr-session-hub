"""Loopback-only deterministic model/release fixture for manual native acceptance.

Not imported by the mod or run in CI. Native CLIs create and resume their own
disposable histories. Only continuity booleans/counts are logged, never requests.
"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import time
import uuid

NONCE = "HUB_NATIVE_CONTEXT_7e251cf4"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def reply(self, data, status=200):
        raw = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        relative = self.path.split("?", 1)[0].lstrip("/")
        if relative in ("v1/models", "models"):
            self.reply({"data": [{"id": "hub-local", "object": "model", "owned_by": "local-test"}]})
            return
        if relative not in {"app/latest.json", "core/latest.json", "app/0.1.14.tar.gz", "app/0.1.15.tar.gz"}:
            self.reply({"error": "not found"}, 404)
            return
        path = (self.server.root / relative).resolve()
        if path.is_relative_to(self.server.root) and path.is_file():
            data = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.reply({"error": "not found"}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        if not 0 < length <= 16 * 1024 * 1024:
            self.reply({"error": "request budget"}, 413)
            return
        try:
            request = json.loads(self.rfile.read(length))
        except (ValueError, UnicodeError):
            self.reply({"error": "invalid JSON"}, 400)
            return
        messages = request.get("messages", request.get("input", request.get("contents", [])))
        body = json.dumps(messages)
        verifying = "VERIFY_CONTEXT" in body
        # The current verification prompt contains no nonce. A genuine resumed
        # request must carry it in the previous messages, not in a summary prompt.
        history_loaded = NONCE in body
        text = ("CONTINUITY_OK" if history_loaded else "CONTINUITY_MISSING") if verifying else NONCE
        with (self.server.root / "observations.jsonl").open("a", encoding="utf-8") as log:
            log.write(json.dumps({"endpoint": self.path, "verifying": verifying,
                                  "historyLoaded": history_loaded, "messages": len(messages), "at": time.time()}) + "\n")
        model = request.get("model", "hub-local")
        identifier = uuid.uuid4().hex
        google = "generatecontent" in self.path.lower()
        if google:
            result = {"candidates": [{"content": {"role": "model", "parts": [{"text": text}]},
                                      "finishReason": "STOP", "index": 0}],
                      "usageMetadata": {"promptTokenCount": 20, "candidatesTokenCount": 10, "totalTokenCount": 30},
                      "modelVersion": "gemini-2.5-flash"}
            events = [(None, result)]
        elif "messages" in self.path and "chat/completions" not in self.path:
            result = {"id": "msg_" + identifier, "type": "message", "role": "assistant", "model": model,
                      "content": [{"type": "text", "text": text}], "stop_reason": "end_turn",
                      "stop_sequence": None, "usage": {"input_tokens": 20, "output_tokens": 10}}
            events = [("message_start", {"type": "message_start", "message": {**result, "content": [], "stop_reason": None}}),
                      ("content_block_start", {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}),
                      ("content_block_delta", {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": text}}),
                      ("content_block_stop", {"type": "content_block_stop", "index": 0}),
                      ("message_delta", {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None}, "usage": {"output_tokens": 10}}),
                      ("message_stop", {"type": "message_stop"})]
        elif "responses" in self.path:
            item = {"id": "msg_" + identifier, "type": "message", "status": "completed", "role": "assistant",
                    "content": [{"type": "output_text", "text": text, "annotations": []}]}
            result = {"id": "resp_" + identifier, "object": "response", "created_at": int(time.time()),
                      "status": "completed", "model": model, "output": [item],
                      "usage": {"input_tokens": 20, "output_tokens": 10, "total_tokens": 30}}
            events = [("response.created", {"response": {**result, "status": "in_progress", "output": []}}),
                      ("response.output_item.added", {"output_index": 0, "item": {**item, "status": "in_progress", "content": []}}),
                      ("response.content_part.added", {"item_id": item["id"], "output_index": 0, "content_index": 0, "part": {"type": "output_text", "text": "", "annotations": []}}),
                      ("response.output_text.delta", {"item_id": item["id"], "output_index": 0, "content_index": 0, "delta": text}),
                      ("response.output_text.done", {"item_id": item["id"], "output_index": 0, "content_index": 0, "text": text}),
                      ("response.content_part.done", {"item_id": item["id"], "output_index": 0, "content_index": 0, "part": item["content"][0]}),
                      ("response.output_item.done", {"output_index": 0, "item": item}),
                      ("response.completed", {"response": result})]
            events = [(name, {"type": name, "sequence_number": n, **data}) for n, (name, data) in enumerate(events)]
        else:
            result = {"id": "chatcmpl_" + identifier, "object": "chat.completion", "created": int(time.time()), "model": model,
                      "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
                      "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30}}
            events = [(None, {**result, "object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {"role": "assistant", "content": text}, "finish_reason": None}]}),
                      (None, {**result, "object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]})]
        if not request.get("stream") and not (google and "streamGenerateContent" in self.path):
            self.reply(result)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            for name, data in events:
                prefix = "event: " + name + "\n" if name else ""
                self.wfile.write((prefix + "data: " + json.dumps(data) + "\n\n").encode())
            if events[0][0] is None and not google:
                self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_relative_to(Path(__file__).resolve().parents[1] / ".dev"):
        raise SystemExit("Use a repository-local .dev test root")
    root.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.root = root
    (root / "server.json").write_text(json.dumps({"url": f"http://127.0.0.1:{server.server_port}"}), encoding="utf-8")
    print("Loopback native acceptance fixture ready", flush=True)
    server.serve_forever()
