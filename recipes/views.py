from rest_framework import generics, status
from rest_framework.response import Response
from .models import Recipes, Category, Level, FavoriteFoods, User
from .serializer import RecipeSerializer, CategoriesSerializer, LevelSerializer, FavoriteFoodsSerializer
from myproject.pagination import CustomPagination
from rest_framework.permissions import IsAuthenticated
import logging, os
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import time

logger = logging.getLogger(__name__)

# Create your views here.        
class RecipeListCreate(generics.ListCreateAPIView) :
    permission_classes = [IsAuthenticated]
    queryset = Recipes.objects.filter(is_deleted = False)
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination

    def get(self, request):
        try :
            ordering_params = self.request.GET
            filter_field = {}
            ordering_field = []

            queryset = self.filter_queryset(self.get_queryset())
            
            if ordering_params :
                for field, value in ordering_params.items() :
                    filter_params = value.split(',') 

                    if len(filter_params) < 2:
                        continue

                    filter_search = filter_params[0].strip()
                    filter_direction = filter_params[1].strip()

                    if filter_search :
                        filter_field[field] = filter_search

                    if filter_direction :
                        if filter_direction == 'asc' :
                            ordering_field.append(field)
                        elif filter_direction == 'desc' :
                            ordering_field.append(f'-{field}')
                        
            if ordering_field :
                queryset = queryset.order_by(*ordering_field)
            else :
                queryset = queryset.order_by('recipe_name')

            if filter_field :
                for field, value in filter_field.items() :
                    field_contain = f'{field}__icontains'
                    queryset = queryset.filter(**{field_contain: value})

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data
            else:
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data

            payload = {
                'total_data': self.queryset.count(),
                'statusCode': status.HTTP_200_OK,
                'status': 'Success',
                'message': 'Success',
                'data': data
            }

            logger.info(f"Success get list")
            return Response(payload, status=status.HTTP_200_OK)
        except Exception as e :
            logger.info(f"An error occurred while creating the product: ${str(e)}")
            return Response({
                "status": "error",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            user = User.objects.get(id=user_id)
            document = request.FILES.get('files', None)

            file_name = f"{request.data.get('recipe_name')}_{request.data.get('category')}_{request.data.get('level')}_{int(time.time())}"
            if document:
                _, file_extension = os.path.splitext(document.name)
                request.data['image_filename'] = f"{file_name}.{file_extension}"

            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                if document:
                    handle_upload_files(document, file_name)

                serializer.save(user=user)

                return Response({
                    "status": "Success",
                    "message": "Resep Makanan Berhasil disimpan",
                    "statusCode": status.HTTP_201_CREATED
                }, status=status.HTTP_201_CREATED)
            else :

                return Response({
                    "status": "Failed",
                    "message": "Data Resep Makanan tidak berhasil disimpan",
                    "statusCode": status.HTTP_400_BAD_REQUEST
                }, status=status.HTTP_400_BAD_REQUEST)        
        except Exception as e:            

            return Response({
                "status": "error",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RecipeToggleFavorite(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteFoodsSerializer

    def put(self, request, *args, **kwargs):
        try :
            if not request.data.get('user_id') :
                return Response({
                    "status": "Failed",
                    "message": "Data Resep Makanan tidak berhasil disimpan",
                    "statusCode": status.HTTP_400_BAD_REQUEST
                }, status=status.HTTP_400_BAD_REQUEST)    

            recipe_id = kwargs.get('recipe_id')
            user_id = request.data.get('user_id')
            recipe = Recipes.objects.get(recipe_id=recipe_id)
            
            if not recipe :
                return Response({
                    "status": "Error",
                    "message": "Recipe not found.",
                    "statusCode": status.HTTP_404_NOT_FOUND
                }, status=status.HTTP_404_NOT_FOUND)
            
            user = User.objects.get(id=user_id)
            if not user :
                return Response({
                    "status": "Error",
                    "message": "UserId not found.",
                    "statusCode": status.HTTP_404_NOT_FOUND
                }, status=status.HTTP_404_NOT_FOUND)
            
            recipe.is_favorite = not recipe.is_favorite
            recipe.save()

            favorite_food, created = FavoriteFoods.objects.get_or_create(
                recipe=recipe,
                user=user,
                defaults={'is_favorite': False}
            )

            if not created :
                favorite_food.is_favorite = not recipe.is_favorite
                favorite_food.save()

            serializer = self.get_serializer(favorite_food)

            return Response({
                "status": "Success",
                "message": "Favorite berhasil diperbarui",
                "data": serializer.data,
                "statusCode": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)
        
        except Exception as e :
            return Response({
                "status": "error",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryListCreate(generics.ListCreateAPIView) :
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer
    pagination_class = CustomPagination

    def get(self, request):
        try :
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data
            else:
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data

            payload = {
                'total_data': self.queryset.count(),
                'statusCode': status.HTTP_200_OK,
                'status': 'Success',
                'message': 'Success',
                'data': data
            }

            return Response(payload)
        except Exception as e :
            return Response({
                "status": "error",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                return Response({
                    "status": "success",
                    "message": "Kategori Makanan Berhasil disimpan",
                    "statusCode": status.HTTP_201_CREATED
                }, status=status.HTTP_201_CREATED)
            
            else :
                return Response({
                    "status": "failed",
                    "message": "Data Kategori Makanan tidak berhasil disimpan",
                    "statusCode": status.HTTP_400_BAD_REQUEST
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LevelListCreate(generics.ListCreateAPIView) :
    permission_classes = [IsAuthenticated]
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    pagination_class = CustomPagination

    def get(self, request):
        try :
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data
            else:
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data

            payload = {
                'total_data': self.queryset.count(),
                'statusCode': status.HTTP_200_OK,
                'status': 'OK',
                'message': 'Success',
                'data': data
            }

            return Response(payload, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({
                "status": "error",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                return Response({
                    "status": "success",
                    "message": "Level Makanan Berhasil disimpan",
                    "statusCode": status.HTTP_201_CREATED
                }, status=status.HTTP_201_CREATED)
            
            else :
                return Response({
                    "status": "failed",
                    "message": "Data Level Makanan tidak berhasil disimpan",
                    "statusCode": status.HTTP_400_BAD_REQUEST
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
def handle_upload_files(file, file_name):
    if file:
        base_name, ext = os.path.splitext(file_name)
        if not ext:
            ext = '.jpg' 

        file_name = f"{base_name}{ext}"
        file_path = os.path.join('uploads', file_name)
        file_url = default_storage.save(file_path, ContentFile(file.read()))
        return file_url
    return None