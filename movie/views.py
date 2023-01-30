from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import Genre, Movie
from .serializers import (
    GenreSerializer,
    MovieSerializer,
)


class ListGenresView(generics.ListAPIView):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class RetrieveGenreView(generics.GenericAPIView):
    serializer_class = MovieSerializer
    queryset = Genre.objects.all()

    def get(self, request, pk):
        queryset = self.queryset.get(id=pk)
        movies = queryset.genres.all()
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
    serializer_class = MovieSerializer


class UpdateMovieView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()


class DeleteMovieView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Movie.objects.all()
