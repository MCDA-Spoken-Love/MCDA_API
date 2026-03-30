from unittest.mock import patch, MagicMock

from django.test import TestCase

from services.cloudinary_service import upload_image


class CloudinaryUploadTests(TestCase):
    @patch("services.cloudinary_service.cloudinary.uploader.upload")
    @patch("services.cloudinary_service.CloudinaryImage")
    def test_upload_image_returns_url(self, mock_cloudinary_image, mock_upload):
        mock_upload.return_value = {"public_id": "fake_public_id"}
        mock_instance = MagicMock()
        mock_instance.build_url.return_value = "https://cloudinary.com/fake.jpg"
        mock_cloudinary_image.return_value = mock_instance

        fake_file = MagicMock()
        url = upload_image(fake_file)

        self.assertEqual(url, "https://cloudinary.com/fake.jpg")
        mock_upload.assert_called_once_with(fake_file)
        mock_cloudinary_image.assert_called_once_with("fake_public_id")
        mock_instance.build_url.assert_called_once()
