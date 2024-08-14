from django.urls import path
from .views import RecipeListCreate, CategoryListCreate, LevelListCreate

urlpatterns = [
    path('book-recipe/book-recipes', RecipeListCreate.as_view(), name='recipe-list-create'),
    path('book-recipe-masters/categoryoption-lists', CategoryListCreate.as_view(), name='category-list-create'),
    path('book-recipe-masters/leveloption-lists', LevelListCreate.as_view(), name='level-list-create'),
]