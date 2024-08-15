from django.urls import path
from .views import RecipeListCreate, CategoryListCreate, LevelListCreate, RecipeToggleFavorite
from .auth import LoginView, RegisterView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('book-recipe/book-recipes', RecipeListCreate.as_view(), name='recipe-list-create'),
    path('book-recipe/book-recipes/<int:recipe_id>/favorites', RecipeToggleFavorite.as_view(), name='recipe-detail'),

    path('book-recipe-masters/categoryoption-lists', CategoryListCreate.as_view(), name='category-list-create'),

    path('book-recipe-masters/leveloption-lists', LevelListCreate.as_view(), name='level-list-create'),

    path('token', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token-refresh'),

    path('user-management/users/sign-in', LoginView.as_view(), name='login'),
    path('user-management/users/sign-up', RegisterView.as_view(), name='register'),
]