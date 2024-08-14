from rest_framework import serializers
from .models import Recipes, Category, Level

class RecipeSerializer(serializers.ModelSerializer) :
    class Meta:
        model = Recipes
        fields = ('recipe_id', 'recipe_name', 'image_url', 'time', 'is_favorite')

class CategoriesSerializer(serializers.ModelSerializer) :
    class Meta:
        model = Category
        fields = ('category_id', 'category_name')

class LevelSerializer(serializers.ModelSerializer) :
    class Meta:
        model = Level
        fields = ('level_id', 'level_name')