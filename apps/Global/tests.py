from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class GlobalViewsTestCase(TestCase):
    @patch("services.cloudinary_service.CloudinaryService.presign_url")
    def test_presign_image_view_success(self, mock_presign):
        url = reverse("presign_image")
        mock_presign.return_value = {
            "signature": "test_signature",
            "timestamp": 1600000000,
            "public_id": "test_file.jpg",
            "folder": "test_folder",
        }

        data = {
            "file_name": "test_file.jpg",
            "folder_name": "test_folder",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_presign.return_value)
        mock_presign.assert_called_once_with(
            public_id="test_file.jpg",
            folder_name="test_folder",
        )

    def test_presign_image_view_missing_file_name(self):
        url = reverse("presign_image")
        data = {
            "folder_name": "test_folder",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message": "Favor fornecer um arquivo"})

    def test_presign_image_view_missing_folder_name(self):
        url = reverse("presign_image")
        data = {
            "file_name": "test_file.jpg",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {"message": "Favor fornecer um nome para a pasta"}
        )
