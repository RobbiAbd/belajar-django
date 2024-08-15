from rest_framework import serializers
from .models import Recipes, Category, Level, User, FavoriteFoods

class CategoriesSerializer(serializers.ModelSerializer) :
    class Meta:
        model = Category
        fields = ('category_id', 'category_name')

class LevelSerializer(serializers.ModelSerializer) :
    class Meta:
        model = Level
        fields = ('level_id', 'level_name')

class UsersSerializer(serializers.ModelSerializer) :
    class Meta:
        model = User
        fields = ('id', 'fullname')

class RecipeSerializer(serializers.ModelSerializer) :
    category = CategoriesSerializer(read_only=True)
    level = LevelSerializer(read_only=True)

    class Meta:
        model = Recipes
        fields = ('recipe_id', 'recipe_name', 'image_url', 'time', 'is_favorite', 'category', 'level', 'image_filename')


class FavoriteFoodsSerializer(serializers.ModelSerializer) :
    class Meta :
        model = FavoriteFoods
        fields = '__all__'