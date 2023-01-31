from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    genre = models.ManyToManyField(Genre, related_name="movies")
    name = models.CharField(max_length=50)
    release_date = models.DateField()
    rating = models.IntegerField(
        blank=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10)]
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    user = models.ForeignKey(
        "user.User", related_name="user_reviews", on_delete=models.CASCADE
    )
    movie = models.ForeignKey(
        Movie, related_name="movie_reviews", on_delete=models.CASCADE
    )
    description = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
