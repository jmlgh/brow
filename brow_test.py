import unittest
import io
import sys

from brow import URL
from brow import load


class TestBrow(unittest.TestCase):
    def setUp(self):
        self.output_capture = io.StringIO()
        # output redirection
        sys.stdout = self.output_capture

    def tearDown(self):
        # restore sys.stdout
        sys.stdout = sys.__stdout__
        self.output_capture.close()

    def test_https(self):
        expected_texts = ["This is a simple",
                          "web page with some", "text in it."]
        load(URL('https://browser.engineering/examples/example1-simple.html'))
        captures = self.output_capture.getvalue().strip().split("\n")
        clean_captures = [cap.strip() for cap in captures]
        self.assertListEqual(expected_texts, clean_captures)

    def test_http(self):
        expected_text = 'Example Domain'
        load(URL('http://example.org:80/index.html'))
        captures = self.output_capture.getvalue().strip().split("\n")
        domain_text = [cap.strip() for cap in captures][0]
        self.assertEqual(expected_text, domain_text)

    def test_file(self):
        expected_texts = ["This text", "Should be read", "By the brow browser"]
        load(URL("file:///Users/jfml/src/brow/tests/test_file1.txt"))
        captures = self.output_capture.getvalue().strip().split("\n")
        clean_captures = [line.strip() for line in captures]
        self.assertListEqual(expected_texts, clean_captures)

    def test_data(self):
        expected_text = "Hello, World!"
        load(URL("data:text/html,Hello, World!"))
        capture = self.output_capture.getvalue().strip()
        self.assertEqual(expected_text, capture)


if __name__ == '__main__':
    unittest.main()
