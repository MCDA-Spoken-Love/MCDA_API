from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.Account.models import Users
from apps.Account.serializer import UserAccountSerializer


class ManageUserView(APIView):
    @staticmethod
    def get(request) -> Response:
        user = request.user
        return Response(
            {"username": user.username, "email": user.email}, status=status.HTTP_200_OK
        )

    @staticmethod
    def patch(request) -> Response:
        user = request.user
        try:
            serializer = UserAccountSerializer(user, data=request.data, partial=True)
            print(serializer)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Usuário atualizado com sucesso"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "message": "Dados de atualização invalidos",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {"message": "Error ao tentar atualizar usuário", "full_error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @staticmethod
    def delete(request) -> Response:
        user = request.user
        try:
            Users.objects.get(id=user.id).delete()
            return Response(
                {"message": f"A conta @{user.username} foi excluída com sucesso"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": "Error in deleting user", "full_error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GetUserByFilterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @staticmethod
    def get(request) -> Response:
        try:
            username = request.query_params.get("username")
            email = request.query_params.get("email")
            all_users = []
            if not username and not email:
                return Response(
                    {"message": "Por favor insira um username ou e-mail"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                if username and email:
                    all_users = Users.objects.filter(username=username, email=email)
                elif username:
                    all_users = Users.objects.filter(username=username)
                elif email:
                    all_users = Users.objects.filter(email=email)

            return Response({"user_count": len(all_users)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"message": "Erro ao filtrar usuário", "full_error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
