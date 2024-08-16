from django.urls import path
from .views import RecipeListCreate, CategoryListCreate, LevelListCreate, RecipeToggleFavorite, FavoriteListCreate, MyRecipesListCreate, DetailRecipeListCreate
from .auth import LoginView, RegisterView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('book-recipe/book-recipes', RecipeListCreate.as_view(), name='recipe-list-create'),
    path('book-recipe/book-recipes/<int:recipe_id>/favorites', RecipeToggleFavorite.as_view(), name='toogle-favorite'),
    path('book-recipe/book-recipes/<int:recipe_id>', DetailRecipeListCreate.as_view(), name='recipe-detail'),

    path('book-recipe/my-favorite-recipes', FavoriteListCreate.as_view(), name='favorite-recipe-list-create'),

    path('book-recipe/my-recipes', MyRecipesListCreate.as_view(), name='my-recipe-list-create'),

    path('book-recipe-masters/category-option-lists', CategoryListCreate.as_view(), name='category-list-create'),

    path('book-recipe-masters/level-option-lists', LevelListCreate.as_view(), name='level-list-create'),

    path('token', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token-refresh'),

    path('user-management/users/sign-in', LoginView.as_view(), name='login'),
    path('user-management/users/sign-up', RegisterView.as_view(), name='register'),
]