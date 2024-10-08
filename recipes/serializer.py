from rest_framework import serializers
from .models import Recipes, Category, Level, User, FavoriteFoods

class CategoriesSerializer(serializers.ModelSerializer) :
    categoryId = serializers.IntegerField(source='category_id')
    categoryName = serializers.CharField(source='category_name')

    class Meta:
        model = Category
        fields = ('categoryId', 'categoryName')

class LevelSerializer(serializers.ModelSerializer) :
    levelId = serializers.IntegerField(source='level_id')
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

    recipeId = serializers.IntegerField(source='recipe_id')
    recipeName = serializers.CharField(source='recipe_name')
    imageUrl = serializers.CharField(source='image_url')
    imageFilename = serializers.CharField(source='image_filename')
    timeCook = serializers.IntegerField(source='time_cook')
    howToCook = serializers.CharField(source='how_to_cook')

    isFavorite = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = ('recipeId', 'recipeName', 'imageUrl', 'timeCook', 'time', 'categories', 'levels', 'imageFilename', 'isFavorite', 'ingredient', 'howToCook')

    def get_isFavorite(self, obj):
        user_id = self.context['request'].user.id

        favorite = FavoriteFoods.objects.filter(user_id=user_id, recipe=obj).first()
        return favorite.is_favorite if favorite else False

class FavoriteFoodsSerializer(serializers.ModelSerializer) :
    recipeId = serializers.IntegerField(source='recipe.recipe_id')
    recipeName = serializers.CharField(source='recipe.recipe_name')
    imageUrl = serializers.CharField(source='recipe.image_url')
    imageFilename = serializers.CharField(source='recipe.image_filename')
    timeCook = serializers.CharField(source='recipe.time_cook')

    categories = CategoriesSerializer(source='recipe.category', read_only=True)
    levels = LevelSerializer(source='recipe.level', read_only=True)

    isFavorite = serializers.BooleanField(source='is_favorite')

    class Meta:
        model = FavoriteFoods
        fields = [
            'recipeId', 'recipeName', 'imageUrl', 'imageFilename', 'timeCook', 'isFavorite', 'categories', 'levels'
        ]