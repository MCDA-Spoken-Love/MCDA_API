from unittest.mock import patch

from django.test import TestCase

from mcda_api_project import settings
from services.cloudinary_service import CloudinaryService


class CloudinaryServiceTests(TestCase):
    def setUp(self):
        self.service = CloudinaryService()

    @patch("cloudinary.utils.api_sign_request", return_value="test_url")
    @patch("time.time", return_value=1600000000)
    def test_presign_url_view(self, mock_time, mock_sign):
        cloudinary_presign_params = {
            "file_name": "test_file.jpg",
            "folder_name": "test_folder",
        }
        mock_sign.return_value = "test_url"
        mock_time.return_value = 1600000000

        result = self.service.presign_url(
            cloudinary_presign_params["file_name"],
            cloudinary_presign_params["folder_name"],
        )

        assert result["signature"] == "test_url"
        assert result["timestamp"] == 1600000000
        assert result["public_id"] == cloudinary_presign_params["file_name"]
        assert result["folder"] == cloudinary_presign_params["folder_name"]

        expected_params_to_sign = {
            "timestamp": 1600000000,
            "public_id": cloudinary_presign_params["file_name"],
            "folder": cloudinary_presign_params["folder_name"],
            "source": "uw",
        }
        mock_sign.assert_called_once_with(
            expected_params_to_sign, settings.CLOUDINARY_API_SECRET
        )
