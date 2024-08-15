from rest_framework import serializers
from .models import Recipes, Category, Level, User, FavoriteFoods

class CategoriesSerializer(serializers.ModelSerializer) :
    categoryId = serializers.CharField(source='category_id')
    categoryName = serializers.CharField(source='category_name')

    class Meta:
        model = Category
        fields = ('categoryId', 'categoryName')

class LevelSerializer(serializers.ModelSerializer) :
    levelId = serializers.CharField(source='level_id')
    levelName = serializers.CharField(source='level_name')

    class Meta:
        model = Level
        fields = ('levelId', 'levelName')

class UsersSerializer(serializers.ModelSerializer) :
    class Meta:
        model = User
        fields = ('id', 'fullname')

class RecipeSerializer(serializers.ModelSerializer) :
    categories = CategoriesSerializer(source='category',read_only=True)
    levels = LevelSerializer(source='level', read_only=True)

    recipeId = serializers.CharField(source='recipe_id')
    recipeName = serializers.CharField(source='recipe_name')
    isFavorite = serializers.CharField(source='is_favorite')
    imageUrl = serializers.CharField(source='image_url')
    imageFilename = serializers.CharField(source='image_filename')

    class Meta:
        model = Recipes
        fields = ('recipeId', 'recipeName', 'imageUrl', 'time', 'isFavorite', 'categories', 'levels', 'imageFilename')


class FavoriteFoodsSerializer(serializers.ModelSerializer) :
    class Meta :
        model = FavoriteFoods
        fields = '__all__'