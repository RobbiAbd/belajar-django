from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import logging
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from .models import User

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')

            if not username or not password:
                logger.info(f"Input is not valid")
                response_data = {
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "status": "Failed",
                    "message": "Input is not valid",
                }

                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(username=username).exists():
                logger.info(f"Username already exist")
                response_data = {
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "status": "Failed",
                    "message": "Username already exist",
                }

                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            user = User(username=username, password=password)
            user.save()

            response_data = {
                "statusCode": status.HTTP_201_CREATED,
                "status": "Success",
                "message": f"Register Success",
            }

            logger.info(f"User registered successfully")
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An error occurred during registration: {str(e)}")
            return Response({
                "status": "error",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")
            user = User.objects.get(username=username, is_deleted=False)

            if check_password(password, user.password) :
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                response_data = {
                    "data": {
                        "id": user.id,
                        "token": access_token,
                        "type": 'bearer',
                        "username": user.username,
                    },
                    "message": 'Success login',
                    "statusCode": status.HTTP_200_OK,
                    "status": 'Success',
                }

                logger.info(f"Successful login for user: {user.username}")
                return Response(response_data, status=status.HTTP_200_OK)
            
            else:
                logger.warning(f"Failed login attempt for username: {username}")
                response_data = {
                    "message": f"Failed login attempt for username: {username}",
                    "statusCode": status.HTTP_401_UNAUTHORIZED,
                    "status": "Failed",
                }

                return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            logger.error(f"An error occurred during login: {str(e)}")

            return Response({
                "status": "error",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)