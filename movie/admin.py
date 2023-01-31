from django.contrib import admin
from .models import Genre, Movie, Review


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "created_at", "updated_at")
