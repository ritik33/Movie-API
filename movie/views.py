from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import Genre, Movie, Review
from .serializers import (
    GenreSerializer,
    MovieSerializer,
    CreateUpdateMovieSerializer,
    CreateUpdateReviewSerializer,
)


class ListGenresView(generics.ListAPIView):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class RetrieveGenreView(generics.GenericAPIView):
    serializer_class = MovieSerializer
    queryset = Genre.objects.all()

    def get(self, request, pk):
        queryset = self.queryset.get(id=pk)
        movies = queryset.movies.all()
        serializer = self.serializer_class(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateGenreView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GenreSerializer

    def create(self, request, *args, **kwargs):
        genre = Genre.objects.filter(name__iexact=request.data["name"])
        if genre.exists():
            return Response(
                {"error": "genre already exists."}, status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)


class UpdateGenreView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()

    def put(self, request, pk):
        instance = self.queryset.get(id=pk)
        genre = Genre.objects.filter(name__iexact=request.data["name"])
        if genre.exists():
            return Response(
                {"error": "genre already exists."}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteGenreView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Movie.objects.all()

    def destroy(self, request, pk):
        if self.queryset.filter(genre__id=pk).exists():
            return Response(
                {"error": "only empty genre can be deleted."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        genre = Genre.objects.get(id=pk)
        genre.delete()
        return Response({"genre": "deleted"}, status=status.HTTP_200_OK)


class ListMoviesView(generics.ListAPIView):
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()


class RetrieveMovieView(generics.RetrieveAPIView):
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()


class CreateMovieView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateUpdateMovieSerializer


class UpdateMovieView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateUpdateMovieSerializer
    queryset = Movie.objects.all()


class DeleteMovieView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Movie.objects.all()


class CreateReviewView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateUpdateReviewSerializer
    queryset = Movie.objects.all()

    def create(self, request, pk):
        user = request.user
        movie = self.queryset.get(id=pk)
        review = Review.objects.filter(movie=movie, user=user)
        if review.exists():
            return Response(
                {"error": "movie already reviewed."}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, movie=movie)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpdateReviewView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateUpdateReviewSerializer
    queryset = Review.objects.all()

    def put(self, request, pk):
        instance = self.queryset.get(id=pk)
        if instance.user != request.user:
            return Response(
                {"error": "only review creator can update review."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteReviewView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()

    def destroy(self, request, pk, *args, **kwargs):
        review = self.queryset.get(id=pk)
        if review.user != request.user:
            return Response(
                {"error": "only review creator can delete review."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)
