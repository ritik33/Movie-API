from rest_framework import serializers
from .models import Genre, Movie, Review


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"
        # name validators = [] causes unique constraint error
        # to protect from that error use validation in view
        # if validate() in serializer then create or update movie with already existing genre fails
        extra_kwargs = {"name": {"validators": []}}

    def update(self, instance, validated_data):
        instance.name = validated_data["name"]
        instance.save()
        return instance


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class CreateUpdateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("description",)


class MovieSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    movie_reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        fields = "__all__"


class CreateUpdateMovieSerializer(serializers.ModelSerializer):
    # separate serializer to create/update movies without providing reviews
    genre = GenreSerializer(many=True)

    class Meta:
        model = Movie
        fields = "__all__"

    def create(self, validated_data):
        genres = validated_data.pop("genre")[0]
        movie = Movie.objects.create(**validated_data)
        # m2m fields are set after obj is created
        for genre in genres.values():
            genre_obj, created = Genre.objects.get_or_create(
                name__iexact=genre, defaults={"name": genre}
            )
            movie.genre.add(genre_obj)

        return movie

    def update(self, instance, validated_data):
        fields = ["name", "release_date", "rating"]
        movie_genres = instance.genre.all()

        for field in fields:
            try:
                setattr(instance, field, validated_data[field])
            except KeyError:  # validated_data may not contain all fields during HTTP PATCH
                pass
        try:
            genres = validated_data.pop("genre")[0]
            for genre in genres.values():
                genre_obj, created = Genre.objects.get_or_create(
                    name__iexact=genre, defaults={"name": genre}
                )
                if movie_genres.filter(name__iexact=genre).exists():
                    instance.genre.remove(genre_obj)
                else:
                    instance.genre.add(genre_obj)
        except KeyError:
            pass

        instance.save()
        return instance
