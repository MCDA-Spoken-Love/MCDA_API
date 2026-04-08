from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from services.cloudinary_service import CloudinaryService


class PresignImageView(APIView):
    permission_classes = [permissions.AllowAny]

    def __init__(self):
        super(PresignImageView, self).__init__()
        self.cloudinary_service = CloudinaryService()

    def post(
        self,
        request,
    ) -> Response:
        try:
            file_name = request.data.get("file_name")
            folder_name = request.data.get("folder_name")
            if not file_name:
                return Response({"message": "Favor fornecer um arquivo"}, status=400)

            if not folder_name:
                return Response(
                    {"message": "Favor fornecer um nome para a pasta"}, status=400
                )

            presigned_url = self.cloudinary_service.presign_url(
                public_id=file_name, folder_name=folder_name
            )
            return Response(presigned_url, status=200)
        except Exception as e:
            return Response(
                {"message": f"Erro ao tentar gerar url para arquivo: {str(e)}"},
                status=500,
            )
