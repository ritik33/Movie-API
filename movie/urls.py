from django.urls import path
from .views import (
    ListGenresView,
    RetrieveGenreView,
    CreateGenreView,
    UpdateGenreView,
    DeleteGenreView,
    ListMoviesView,
    RetrieveMovieView,
    CreateMovieView,
    UpdateMovieView,
    DeleteMovieView,
    CreateReviewView,
    UpdateReviewView,
    DeleteReviewView,
)


urlpatterns = [
    path("genres/", ListGenresView.as_view(), name="list-genres"),
    path("genre/<int:pk>/", RetrieveGenreView.as_view(), name="retrieve-genre"),
    path("create-genre/", CreateGenreView.as_view(), name="create-genre"),
    path("update-genre/<int:pk>/", UpdateGenreView.as_view(), name="update-genre"),
    path("delete-genre/<int:pk>/", DeleteGenreView.as_view(), name="delete-genre"),
    path("", ListMoviesView.as_view(), name="list-movies"),
    path("<int:pk>/", RetrieveMovieView.as_view(), name="retrieve-movie"),
    path("create-movie/", CreateMovieView.as_view(), name="create-movie"),
    path("update-movie/<int:pk>/", UpdateMovieView.as_view(), name="update-movie"),
    path("delete-movie/<int:pk>/", DeleteMovieView.as_view(), name="delete-movie"),
    path("create-review/<int:pk>/", CreateReviewView.as_view(), name="create-review"),
    path("update-review/<int:pk>/", UpdateReviewView.as_view(), name="update-review"),
    path("delete-review/<int:pk>/", DeleteReviewView.as_view(), name="delete-review"),
]
