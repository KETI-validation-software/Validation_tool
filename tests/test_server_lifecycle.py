import unittest
from http.server import BaseHTTPRequestHandler
from unittest.mock import Mock, patch


class TestServerLifecycle(unittest.TestCase):
    def test_reusable_http_server_enables_address_reuse(self):
        from api.server_thread import ReusableHTTPServer

        self.assertTrue(ReusableHTTPServer.allow_reuse_address)

    @patch("api.server_thread.HTTPServer.shutdown")
    def test_reusable_http_server_shutdown_also_closes_socket(self, mock_super_shutdown):
        from api.server_thread import ReusableHTTPServer

        server = ReusableHTTPServer.__new__(ReusableHTTPServer)
        server.server_close = Mock()

        ReusableHTTPServer.shutdown(server)

        mock_super_shutdown.assert_called_once()
        server.server_close.assert_called_once()

    @patch("api.webhook_api.HTTPServer.shutdown")
    def test_webhook_reusable_http_server_shutdown_also_closes_socket(self, mock_super_shutdown):
        from api.webhook_api import ReusableHTTPServer

        server = ReusableHTTPServer.__new__(ReusableHTTPServer)
        server.server_close = Mock()

        ReusableHTTPServer.shutdown(server)

        mock_super_shutdown.assert_called_once()
        server.server_close.assert_called_once()

    @patch("api.server_thread.ssl.wrap_socket", side_effect=lambda sock, **kwargs: sock)
    @patch("api.server_thread.ReusableHTTPServer")
    def test_server_thread_stop_server_closes_socket(self, mock_server_cls, _mock_wrap_socket):
        from api.server_thread import server_th

        mock_httpd = Mock()
        mock_httpd.socket = Mock()
        mock_server_cls.return_value = mock_httpd

        thread = server_th(handler_class=BaseHTTPRequestHandler, address="127.0.0.1", port=0)
        thread.stop_server(wait_ms=0)

        mock_httpd.shutdown.assert_called_once()
        mock_httpd.server_close.assert_called_once()

    def test_webhook_thread_stop_closes_socket(self):
        from api.webhook_api import WebhookThread

        mock_httpd = Mock()
        thread = WebhookThread(url="https://localhost", port=8443, message={})
        thread.httpd = mock_httpd

        ok = thread.stop()

        self.assertTrue(ok)
        mock_httpd.shutdown.assert_called_once()
        mock_httpd.server_close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
