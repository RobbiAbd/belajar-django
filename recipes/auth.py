from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import logging
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            username = request.data.get('username')
            fullname = request.data.get('fullname')
            password = request.data.get('password')
            retype_password = request.data.get('retypePassword')

            if not username or not password or not fullname or not retype_password:
                logger.info(f"Input is not valid")
                response_data = {
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "status": "ERROR",
                    "message": "Input is not valid",
                }

                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            if password != retype_password:
                logger.info(f"Password and Retype Password tidak sama")
                response_data = {
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "status": "ERROR",
                    "message": "Password and Retype Password tidak sama",
                }

                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(username=username).exists():
                logger.info(f"Username already exist")
                response_data = {
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "status": "ERROR",
                    "message": "Username already exist",
                }

                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            user = User(username=username, password=password, fullname=fullname, is_deleted=False)
            user.set_password(password)
            user.save()

            response_data = {
                "statusCode": status.HTTP_201_CREATED,
                "status": "OK",
                "message": f"Register Success",
            }

            logger.info(f"User registered successfully")
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An error occurred during registration: {str(e)}")
            return Response({
                "status": "ERROR",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")

            try :
                user = User.objects.get(username=username, is_deleted=False)
            except User.DoesNotExist :
                logger.warning(f"Username not registered: {username}")
                response_data = {
                    "message": f"Username not registered: {username}",
                    "statusCode": status.HTTP_401_UNAUTHORIZED,
                    "status": "ERROR",
                }
                return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

            if user.check_password(password) :
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
                    "status": 'OK',
                }

                logger.info(f"Successful login for user: {user.username}")
                return Response(response_data, status=status.HTTP_200_OK)
            
            else:
                logger.warning(f"Failed login attempt for username: {username}")
                response_data = {
                    "message": f"Failed login attempt for username: {username}",
                    "statusCode": status.HTTP_401_UNAUTHORIZED,
                    "status": "ERROR",
                }

                return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            logger.error(f"An error occurred during login: {str(e)}")

            return Response({
                "status": "ERROR",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)