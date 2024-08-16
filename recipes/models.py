from django.db import models
from django.contrib.auth.hashers import make_password

class HowToCook(models.Model):
    how_to_cook_id = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)

class Ingredient(models.Model):
    ingridient_id = models.BigAutoField(primary_key=True)
    ingridient_measurement = models.CharField(max_length=255, null=True, blank=True)
    ingridient_name = models.CharField(max_length=255, null=True, blank=True)
    ingridient_quantity = models.IntegerField(null=True, blank=True)

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, null=True, blank=True)
    is_deleted = models.BooleanField(null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_time = models.DateTimeField(null=True, blank=True)
    modified_by = models.CharField(max_length=255, null=True, blank=True)
    modified_time = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.category_name    
    
class Level(models.Model):
    level_id = models.AutoField(primary_key=True)
    level_name = models.CharField(max_length=100, null=True, blank=True)
    is_deleted = models.BooleanField(null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_time = models.DateTimeField(null=True, blank=True)
    modified_by = models.CharField(max_length=255, null=True, blank=True)
    modified_time = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.level_name
    
class Role(models.Model):
    role_id = models.BigAutoField(primary_key=True)
    role_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return self.role_name
    
class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    password = models.TextField(null=True, blank=True)
    role = models.CharField(max_length=100, null=True, blank=True)
    is_deleted = models.BooleanField(null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_time = models.DateTimeField(null=True, blank=True)
    modified_by = models.CharField(max_length=255, null=True, blank=True)
    modified_time = models.DateTimeField(null=True, blank=True)
    role_id = models.ForeignKey(Role, on_delete=models.RESTRICT, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)

    def str(self):
        return self.username
    
class Recipes(models.Model):
    recipe_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.RESTRICT, null=True, blank=True)
    recipe_name = models.CharField(max_length=255, null=True, blank=True)
    image_filename = models.TextField(null=True, blank=True)
    time_cook = models.IntegerField(null=True, blank=True)
    ingredient = models.TextField(null=True, blank=True)
    how_to_cook = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_time = models.DateTimeField(null=True, blank=True)
    modified_by = models.CharField(max_length=255, null=True, blank=True)
    modified_time = models.DateTimeField(null=True, blank=True)
    image_url = models.CharField(max_length=255, null=True, blank=True)
    time = models.IntegerField(null=True, blank=True)
    is_favorite = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self) -> str:
        return self.recipe_name
    
class FavoriteFoods(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT, null=True, blank=True)
    recipe = models.ForeignKey(Recipes, on_delete=models.RESTRICT, null=True, blank=True)
    is_favorite = models.BooleanField(null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_time = models.DateTimeField(null=True, blank=True)
    modified_by = models.CharField(max_length=255, null=True, blank=True)
    modified_time = models.DateTimeField(null=True, blank=True)
    
class RecipeHowToCook(models.Model):
    how_to_cook = models.ForeignKey(HowToCook, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)

class RecipeIngredient(models.Model):
    ingridient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
