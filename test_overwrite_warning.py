#!/usr/bin/env python3
"""
Test script for overwrite confirmation logic in ImageConverterApp
"""
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from PIL import Image

# Import after setting up dummy display/mock if needed
import tkinter as tk
from image_converter import ImageConverterApp

class TestOverwriteConfirmation(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide root window
        self.app = ImageConverterApp(self.root)

        # Temporary files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_image_path = os.path.join(self.temp_dir.name, "test_input.png")
        img = Image.new("RGB", (50, 50), color="blue")
        img.save(self.test_image_path, "PNG")

        self.app.input_file = self.test_image_path
        self.app.format_var.set("png")

    def tearDown(self):
        try:
            self.app.quit_app()
        except:
            pass
        self.temp_dir.cleanup()

    @patch("tkinter.messagebox.askyesno")
    def test_overwrite_confirmed(self, mock_askyesno):
        """User confirms overwrite -> image is converted and overwritten"""
        mock_askyesno.return_value = True

        # Existing target file (same name & ext)
        output_file = os.path.join(self.temp_dir.name, "test_input.png")
        self.assertTrue(os.path.exists(output_file))

        with patch("tkinter.messagebox.showinfo"):
            self.app.convert_image()

        # Confirmation dialog was called
        mock_askyesno.assert_called_once()
        args, kwargs = mock_askyesno.call_args
        self.assertEqual(args[0], "警告")
        self.assertIn("test_input.png", args[1])
        self.assertEqual(kwargs.get("icon"), "warning")
        self.assertEqual(self.app.status_var.get(), "変換完了")

    @patch("tkinter.messagebox.askyesno")
    def test_overwrite_cancelled(self, mock_askyesno):
        """User cancels overwrite -> conversion is aborted"""
        mock_askyesno.return_value = False

        output_file = os.path.join(self.temp_dir.name, "test_input.png")
        self.assertTrue(os.path.exists(output_file))

        with patch.object(self.app, "save_image") as mock_save:
            self.app.convert_image()
            mock_save.assert_not_called()

        mock_askyesno.assert_called_once()
        self.assertEqual(self.app.status_var.get(), "保存をキャンセルしました")
        # output_file should be reset since it was auto-generated
        self.assertEqual(self.app.output_file, "")

    @patch("tkinter.messagebox.askyesno")
    def test_overwrite_cancelled_manual_output(self, mock_askyesno):
        """User cancels overwrite when output file was manually selected"""
        mock_askyesno.return_value = False

        custom_output = os.path.join(self.temp_dir.name, "custom_output.png")
        # Create existing file
        with open(custom_output, "w") as f:
            f.write("test")

        self.app.output_file = custom_output

        with patch.object(self.app, "save_image") as mock_save:
            self.app.convert_image()
            mock_save.assert_not_called()

        mock_askyesno.assert_called_once()
        self.assertEqual(self.app.status_var.get(), "保存をキャンセルしました")
        # Manual output_file is preserved for user to change
        self.assertEqual(self.app.output_file, custom_output)

    @patch("tkinter.messagebox.askyesno")
    def test_no_existing_file_no_warning(self, mock_askyesno):
        """If file does not exist, no confirmation is shown"""
        self.app.format_var.set("jpg")
        output_file = os.path.join(self.temp_dir.name, "test_input.jpg")
        if os.path.exists(output_file):
            os.remove(output_file)

        with patch("tkinter.messagebox.showinfo"):
            self.app.convert_image()

        mock_askyesno.assert_not_called()
        self.assertEqual(self.app.status_var.get(), "変換完了")

if __name__ == "__main__":
    unittest.main()
