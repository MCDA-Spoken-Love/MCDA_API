import time

import cloudinary.uploader
from cloudinary import CloudinaryImage

from mcda_api_project import settings


class CloudinaryService:
    def __init__(self):
        self.api_secret = settings.CLOUDINARY_API_SECRET

    @staticmethod
    def upload_image(file) -> CloudinaryImage:
        result = cloudinary.uploader.upload(file)
        return CloudinaryImage(result["public_id"]).build_url()

    def presign_url(self, public_id=str, folder_name=str) -> dict:
        timestamp = int(time.time())
        signature = cloudinary.utils.api_sign_request(
            {
                "timestamp": timestamp,
                "public_id": public_id,
                "folder": folder_name,
                "source": "uw",
            },
            self.api_secret,
        )

        return {
            "signature": signature,
            "timestamp": timestamp,
            "public_id": public_id,
            "folder": folder_name,
        }
