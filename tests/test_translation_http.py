"""Exercise the real HTTP client against a local model-protocol fixture."""
import json
import sys
import threading
import unittest
from unittest.mock import patch
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from translate import translate_items, TranslationError
from sources import request_bytes


class ModelProtocolTests(unittest.TestCase):
    def test_truncated_http_response_is_retried_and_converted_to_safe_failure(self):
        attempts = []
        class TruncatedResponse(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def do_GET(self):
                attempts.append(1)
                self.send_response(200)
                self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()
                self.wfile.write(b"80\r\npartial upstream content")
                self.close_connection = True
        server = ThreadingHTTPServer(("127.0.0.1", 0), TruncatedResponse)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with patch("sources.time.sleep"), self.assertRaises(RuntimeError) as failure:
                request_bytes(f"http://127.0.0.1:{server.server_port}/truncated")
            self.assertEqual(len(attempts), 3)
            self.assertNotIn("partial upstream content", str(failure.exception))
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_real_http_translation_batches_validate_and_keep_source_fields(self):
        received = []

        class Model(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                received.append((self.path, self.headers.get("Authorization"), request["model"]))
                source_items = json.loads(request["messages"][1]["content"])["items"]
                payload = {"items": [{"sourceId": entry["sourceId"], "titleZh": "测试中文标题", "summaryZh": "基于给定资料整理的中文摘要。", "tags": ["工具"]} for entry in source_items]}
                body = json.dumps({"choices": [{"message": {"content": json.dumps(payload)}}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)

        server = ThreadingHTTPServer(("127.0.0.1", 0), Model)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            entries = [{"sourceId": f"hn-{index}", "title": f"Tool {index}", "summary": "A developer tool.", "url": f"https://example.com/{index}", "score": index} for index in range(7)]
            result = translate_items(entries, [], {"LLM_API_KEY": "local-test-only", "LLM_BASE_URL": f"http://127.0.0.1:{server.server_port}/v1", "LLM_MODEL": "protocol-fixture"})
            self.assertEqual(len(result), 7)
            self.assertEqual(len(received), 2)
            self.assertEqual(received[0], ("/v1/chat/completions", "Bearer local-test-only", "protocol-fixture"))
            self.assertEqual(result[6]["url"], "https://example.com/6")
            self.assertEqual(result[6]["score"], 6)
            self.assertEqual(result[6]["translationStatus"], "translated")
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_remote_http_model_endpoint_is_rejected(self):
        with self.assertRaises(TranslationError):
            translate_items([{"sourceId": "hn-1", "title": "Tool", "summary": "A tool"}], [], {"LLM_API_KEY": "local-test-only", "LLM_BASE_URL": "http://public.example/v1"})


if __name__ == "__main__":
    unittest.main()
