from django.db import models
from django.contrib.auth.models import User


class Genre(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=500)
    year = models.IntegerField(default=0)
    genres = models.ManyToManyField(Genre)
    runtime = models.IntegerField(default=0)
    director = models.CharField(max_length=500)
    actors = models.CharField(max_length=500)
    plot = models.CharField(max_length=1000)
    posterUrl = models.CharField(max_length=1000)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    comment = models.CharField(max_length=2000)
    pub_date = models.DateTimeField('date published')
    last_modified = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return '[' + self.user.username + '] reviews the movie [' + self.movie.title + \
               "] --- Rating: " + str(self.rating) + " --- Comment: " + self.comment


class MovieList(models.Model):
    name = models.CharField(max_length=500)
    movies = models.ManyToManyField(Movie)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=2000, null=True)
    pub_date = models.DateTimeField('date published')
    last_modified = models.DateTimeField(null=True, auto_now=True)
    type = models.CharField(max_length=100, null=True)

    def __str__(self):
        return 'Playlist [name: ' + self.name + '] created by [username:' + self.user.username + \
               "]. The playlist has " + str(self.movies.count()) + " movies"
