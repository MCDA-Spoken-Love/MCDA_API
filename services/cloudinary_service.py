import cloudinary.uploader
from cloudinary import CloudinaryImage


def upload_image(file):
    result = cloudinary.uploader.upload(file)
    return CloudinaryImage(result["public_id"]).build_url()
