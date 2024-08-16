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
from django.conf import settings
import time, json
from django.core.files.uploadedfile import InMemoryUploadedFile

logger = logging.getLogger(__name__)

# Create your views here.        
class RecipeListCreate(generics.ListCreateAPIView) :
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user_id = self.request.query_params.get('userId', None)
        category_id = self.request.query_params.get('categoryId', None)
        recipe_name = self.request.query_params.get('recipeName', None)
        level_id = self.request.query_params.get('levelId', None)
        sort_by = self.request.query_params.get('sortBy', None)
        time_range = self.request.query_params.get('time', None)

        queryset = Recipes.objects.filter(is_deleted=False)

        ordering_mapping = {
            'recipeName': 'recipe_name',
            'timeCook': 'time_cook',
        }

        if recipe_name :
            queryset = queryset.filter(recipe_name__icontains=recipe_name)

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if level_id:
            queryset = queryset.filter(level_id=level_id)

        if sort_by:
            sort_field, sort_order = sort_by.split(',')
            sort_field = ordering_mapping.get(sort_field, sort_field)

            if sort_order == 'desc':
                sort_field = f'-{sort_field}'
                queryset = queryset.order_by(sort_field)
            else:
                queryset = queryset.order_by('recipe_name')

        if time_range:
            try:
                if '-' in time_range:
                    time_min, time_max = map(int, time_range.split('-'))
                    queryset = queryset.filter(time__gte=time_min, time__lte=time_max)
                else:
                    time_value = int(time_range)
                    if time_value == 60:
                        queryset = queryset.filter(time__gte=60)
                    else:
                        queryset = queryset.filter(time=time_value)
            except ValueError:
                raise ValueError("time range invalid")
        
        return queryset

    def get(self, request):
        try :                        
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data
            else:
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data

            payload = data

            logger.info(f"Success get list")
            return Response(payload, status=status.HTTP_200_OK)
        except Exception as e :
            logger.info(f"An error occurred while creating the product: ${str(e)}")
            return Response({
                "status": "ERROR",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            user = User.objects.get(id=user_id)

            json_blob = request.FILES.get('request')
            if json_blob:
                json_data = json.load(json_blob)
            else:
                json_data = request.data

            recipe_name = json_data.get('recipeName')
            category_data = json_data.get('categories', {})
            level_data = json_data.get('levels', {})
            category_name = category_data.get('categoryName')
            level_name = level_data.get('levelName')

            mapped_data = {
                'recipe_name': recipe_name,
                'time_cook': json_data.get('timeCook'),
                'time': json_data.get('timeCook'),
                'ingredient': json_data.get('ingredient'),
                'how_to_cook': json_data.get('howToCook'),
                'category_id': category_data.get('categoryId'),
                'level_id': level_data.get('levelId'),
            }        

            document = request.FILES.get('file', None)
            if document:
                try:
                    validate_image_file(document)
                except ValidationError as e:
                    return Response({
                        "status": "ERROR",
                        "message": str(e),
                        "statusCode": status.HTTP_400_BAD_REQUEST
                    }, status=status.HTTP_400_BAD_REQUEST)
        
                _, file_extension = os.path.splitext(document.name)
                    
                file_name = f"{recipe_name}_{category_name}_{level_name}_{int(time.time())}{file_extension}"
                mapped_data['image_filename'] = file_name
                scheme = request.scheme 
                domain = request.get_host() 
                mapped_data['image_url'] = f"{scheme}://{domain}/media/{mapped_data['image_filename']}"
                handle_upload_files(document, file_name)

                recipe = Recipes(user=user,recipe_name=mapped_data['recipe_name'], time_cook=mapped_data['time_cook'], time=mapped_data['time'], ingredient=mapped_data['ingredient'], how_to_cook=mapped_data['how_to_cook'], category_id=mapped_data['category_id'], level_id=mapped_data['level_id'], image_filename=mapped_data['image_filename'], image_url=mapped_data['image_url'], is_deleted=False)
                recipe.save()        

                return Response({
                    "status": "OK",
                    "message": "Resep Makanan Berhasil disimpan",
                    "statusCode": status.HTTP_201_CREATED
                }, status=status.HTTP_201_CREATED)
            else :

                return Response({
                    "status": "ERROR",
                    "message": "File upload not found",
                    "statusCode": status.HTTP_400_BAD_REQUEST
                }, status=status.HTTP_400_BAD_REQUEST)        
        except Exception as e:            
            return Response({
                "status": "ERROR",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DetailRecipeListCreate(generics.ListCreateAPIView) :
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeSerializer

    def get(self, request, *args, **kwargs):
        try :              
            recipe_id = int(kwargs.get('recipe_id'))
            queryset = Recipes.objects.filter(recipe_id=recipe_id)
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            payload = {
                'status': 'OK',
                'statusCode': status.HTTP_200_OK,
                'message': 'success',
                'data': data[0]
            }

            logger.info(f"Success get list")
            return Response(payload, status=status.HTTP_200_OK)
        except Exception as e :
            logger.info(f"An error occurred while creating the product: ${str(e)}")
            return Response({
                "status": "ERROR",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FavoriteListCreate(generics.ListCreateAPIView) :
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user_id = self.request.query_params.get('userId', None)
        category_id = self.request.query_params.get('categoryId', None)
        recipe_name = self.request.query_params.get('recipeName', None)
        level_id = self.request.query_params.get('levelId', None)
        sort_by = self.request.query_params.get('sortBy', None)
        time_range = self.request.query_params.get('time', None)

        queryset = Recipes.objects.filter(is_deleted=False, is_favorite=True)

        ordering_mapping = {
            'recipeName': 'recipe_name',
            'timeCook': 'time_cook',
        }

        if recipe_name :
            queryset = queryset.filter(recipe_name__icontains=recipe_name)

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if level_id:
            queryset = queryset.filter(level_id=level_id)

        if sort_by:
            sort_field, sort_order = sort_by.split(',')
            sort_field = ordering_mapping.get(sort_field, sort_field)

            if sort_order == 'desc':
                sort_field = f'-{sort_field}'
                queryset = queryset.order_by(sort_field)
            else:
                queryset = queryset.order_by('recipe_name')

        if time_range:
            try:
                if '-' in time_range:
                    time_min, time_max = map(int, time_range.split('-'))
                    queryset = queryset.filter(time__gte=time_min, time__lte=time_max)
                else:
                    time_value = int(time_range)
                    if time_value == 60:
                        queryset = queryset.filter(time__gte=60)
                    else:
                        queryset = queryset.filter(time=time_value)
            except ValueError:
                raise ValueError("time range invalid")
        
        return queryset

    def get(self, request):
        try :                        
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data
            else:
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data

            payload = data

            logger.info(f"Success get list")
            return Response(payload, status=status.HTTP_200_OK)
        except Exception as e :
            logger.info(f"An error occurred while creating the product: ${str(e)}")
            return Response({
                "status": "ERROR",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class MyRecipesListCreate(generics.ListCreateAPIView) :
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user_id = self.request.query_params.get('userId', None)
        category_id = self.request.query_params.get('categoryId', None)
        recipe_name = self.request.query_params.get('recipeName', None)
        level_id = self.request.query_params.get('levelId', None)
        sort_by = self.request.query_params.get('sortBy', None)
        time_range = self.request.query_params.get('time', None)

        queryset = Recipes.objects.filter(is_deleted=False)

        ordering_mapping = {
            'recipeName': 'recipe_name',
            'timeCook': 'time_cook',
        }

        if recipe_name :
            queryset = queryset.filter(recipe_name__icontains=recipe_name)

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if level_id:
            queryset = queryset.filter(level_id=level_id)

        if sort_by:
            sort_field, sort_order = sort_by.split(',')
            sort_field = ordering_mapping.get(sort_field, sort_field)

            if sort_order == 'desc':
                sort_field = f'-{sort_field}'
                queryset = queryset.order_by(sort_field)
            else:
                queryset = queryset.order_by('recipe_name')

        if time_range:
            try:
                if '-' in time_range:
                    time_min, time_max = map(int, time_range.split('-'))
                    queryset = queryset.filter(time__gte=time_min, time__lte=time_max)
                else:
                    time_value = int(time_range)
                    if time_value == 60:
                        queryset = queryset.filter(time__gte=60)
                    else:
                        queryset = queryset.filter(time=time_value)
            except ValueError:
                raise ValueError("time range invalid")
        
        return queryset

    def get(self, request):
        try :                        
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data
            else:
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data

            payload = data

            logger.info(f"Success get list")
            return Response(payload, status=status.HTTP_200_OK)
        except Exception as e :
            logger.info(f"An error occurred while creating the product: ${str(e)}")
            return Response({
                "status": "ERROR",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RecipeToggleFavorite(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteFoodsSerializer

    def put(self, request, *args, **kwargs):
        try :
            if not request.data.get('userId') :
                return Response({
                    "status": "ERROR",
                    "message": "UserId tidak ditemukan",
                    "statusCode": status.HTTP_400_BAD_REQUEST
                }, status=status.HTTP_400_BAD_REQUEST)    

            recipe_id = int(kwargs.get('recipe_id'))
            user_id = int(request.data.get('userId'))
            recipe = Recipes.objects.get(recipe_id=recipe_id)
            
            if not recipe :
                return Response({
                    "status": "ERROR",
                    "message": "Recipe not found.",
                    "statusCode": status.HTTP_404_NOT_FOUND
                }, status=status.HTTP_404_NOT_FOUND)
            
            user = User.objects.get(id=user_id)
            if not user :
                return Response({
                    "status": "ERROR",
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
                "status": "OK",
                "message": "Favorite berhasil diperbarui",
                "data": serializer.data,
                "statusCode": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)
        
        except Exception as e :
            return Response({
                "status": "ERROR",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryListCreate(generics.ListCreateAPIView) :
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer

    def get(self, request):
        try :
            queryset = self.filter_queryset(self.get_queryset())            
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

            payload = {
                'total_data': self.queryset.count(),
                'statusCode': status.HTTP_200_OK,
                'status': 'OK',
                'message': 'Success',
                'data': data
            }

            return Response(payload)
        except Exception as e :
            return Response({
                "status": "ERROR",
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
                    "status": "OK",
                    "message": "Kategori Makanan Berhasil disimpan",
                    "statusCode": status.HTTP_201_CREATED
                }, status=status.HTTP_201_CREATED)
            
            else :
                return Response({
                    "status": "ERROR",
                    "message": "Data Kategori Makanan tidak berhasil disimpan",
                    "statusCode": status.HTTP_400_BAD_REQUEST
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                "status": "ERROR",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LevelListCreate(generics.ListCreateAPIView) :
    permission_classes = [IsAuthenticated]
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

    def get(self, request):
        try :
            queryset = self.filter_queryset(self.get_queryset())            
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
                "status": "ERROR",
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
                    "status": "OK",
                    "message": "Level Makanan Berhasil disimpan",
                    "statusCode": status.HTTP_201_CREATED
                }, status=status.HTTP_201_CREATED)
            
            else :
                return Response({
                    "status": "ERROR",
                    "message": "Data Level Makanan tidak berhasil disimpan",
                    "statusCode": status.HTTP_400_BAD_REQUEST
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "ERROR",
                "message": "An error occurred while creating the product",
                "errors": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
ALLOWED_IMAGE_MIME_TYPES = ['image/jpeg', 'image/png']

def validate_image_file(file):
    if not isinstance(file, InMemoryUploadedFile):
        raise ValidationError("Uploaded file is not a valid image file.")
    
    # Check file extension
    _, file_extension = os.path.splitext(file.name)
    if file_extension.lower() not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("Unsupported file extension. Allowed extensions are: .jpg, .jpeg, .png")

    # Check MIME type
    if file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise ValidationError("Unsupported file type. Allowed types are: image/jpeg, image/png")
        
def handle_upload_files(file, file_name):
    # Determine the directory path
    directory_path = settings.MEDIA_ROOT
    
    # Ensure the directory exists
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    # Full file path
    file_path = os.path.join(directory_path, file_name)
    
    # Write the file
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)