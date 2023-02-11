from django.contrib import admin

from .models import Movie, Genre, Review, MovieList

class MovieAdmin(admin.ModelAdmin):
    """
    Thiết lập giao diện trang admin và các mục cần chỉnh sửa. Dựa trên django.contrib.admin của Django
    """
    list_display = ('title', 'director', 'actors')
    list_filter = ['year']
    search_fields = ['title']

admin.site.register(Movie, MovieAdmin)
admin.site.register(Genre)
admin.site.register(Review)
admin.site.register(MovieList)