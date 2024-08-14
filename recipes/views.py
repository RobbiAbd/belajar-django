from rest_framework import generics, status
from rest_framework.response import Response
from .models import Recipes, Category, Level
from .serializer import RecipeSerializer, CategoriesSerializer, LevelSerializer
from myproject.pagination import CustomPagination

# Create your views here.
class RecipeListCreate(generics.ListCreateAPIView) :
    queryset = Recipes.objects.filter(is_deleted = False)
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination

    def get(self, request):
        try :
            ordering_params = self.request.GET
            ordering_field = []

            queryset = self.filter_queryset(self.get_queryset())
            if ordering_params :
                for field, direction in ordering_params.items() :
                    if direction == 'asc' :
                        ordering_field.append(field)
                    elif direction == 'desc' :
                        ordering_field.append(f'-{field}')
                        
            if ordering_field :
                queryset = queryset.order_by(*ordering_field)
            else :
                queryset = queryset.order_by('recipe_name')

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
                    "status": "Success",
                    "message": "Resep Makanan Berhasil disimpan",
                    "statusCode": status.HTTP_201_CREATED
                }, status=status.HTTP_201_CREATED)
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
        
class CategoryListCreate(generics.ListCreateAPIView) :
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
                'status': 'OK',
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
                    "message": "Level Makanan Berhasil disimpan",
                    "statusCode": status.HTTP_201_CREATED
                }, status=status.HTTP_201_CREATED)
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