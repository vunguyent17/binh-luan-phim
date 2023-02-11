from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from django.utils import timezone

from django.views import generic
from django.views.generic.edit import UpdateView, CreateView

from django.shortcuts import get_object_or_404

from django.http import HttpResponse
from django.urls import reverse

from movies.models import Movie, MovieList

from movies.forms import MovieListForm

import json


class MovielistCreateView(CreateView):
    """
    Trang tạo Danh sách phim mới, được kế thừa từ CreateView của django.views.generic.edit
    """
    model = MovieList
    template_name = 'movies/movielist_form.html'
    form_class = MovieListForm

    def get_context_data(self, **kwargs):
        """
        Bổ sung context data cho trang: thêm giá trị submitButtonLabel, sectionTitle
        để chỉnh sửa nhãn cho giao diện
         - Input: Không có
         - Output: Context data có chứa giá trị submitButtonLabel, sectionTitle
        """
        context = super(MovielistCreateView, self).get_context_data(**kwargs)
        context['sectionTitle'] = "Tạo danh sách phim mới"
        context['submitButtonLabel'] = "Tạo danh sách phim mới"
        return context

    def form_valid(self, form):
        """
        Thêm thông tin cho form instance đuợc gửi đến trước khi lưu vào cơ sở dữ liệu
         - Input: kết quả form tạo Danh sách phim mới
         - Output: Phương thức mặc định form_valid mà MovielistCreateView được kế thừa từ CreateView
          (sau khi tiến hành thêm thông tin cho form)
        """
        form.instance.pub_date = timezone.now()
        form.instance.last_modified = timezone.now()
        form.instance.user = self.request.user
        form.instance.type = 'private'
        return super(MovielistCreateView, self).form_valid(form)

    def get_success_url(self):
        """
        Xử lý và điều hướng trang khi lưu dữ liệu thành công
         - Input: không có
         - Output: Trả về trang Chi tiết Danh sách phim vừa tạo (tham số url chứa id của Danh sách phim mới)
        """
        messages.success(
            self.request, "Đã tạo danh sách mới")
        return reverse('movies:detail_movielist', kwargs={'pk': self.object.pk})


class MovielistDetailView(generic.DetailView):
    """
    Trang Chi tiết Danh sách phim, được kế thừa từ DetailView của django
    """
    model = MovieList
    template_name = 'movies/movielist_detail.html'

    def get(self, request, *args, **kwargs):
        """
        Bổ sung xử lý GET request từ trang, dùng cho chức năng tìm kiếm phim trực tiếp (live search)
        để tìm kiếm và thêm phim vào Danh sách phim
        - Input: Request từ trang Chi tiết Danh sách phim
        - Output:
            + Trường hợp là request có operation là "live_search_movies" gửi từ AJAX
            thì xử lý và trả Response có context dđang json gồm các giá trị:
                . Danh sách Kết quả tìm kiếm phim (movies_live_result)
                . Số lượng phim trong danh sách đó  (moviescount)
                . Từ khóa tìm kiếm (searchtext)
            + Ngược lại thì theo phương thức get mặc định của MovielistDetailView
        """
        if request.GET.get("operation") == "live_search_movies" and request.headers.get(
                'x-requested-with') == 'XMLHttpRequest':
            search_text = request.GET.get('search_text')
            movie_list = get_object_or_404(MovieList, user=self.request.user, id=self.kwargs['pk'])
            if search_text is not None and search_text != u"":
                movies_data = [{'id': b.id, 'title': b.title, 'genres': [a.name for a in b.genres.all()],
                                'added': True if b in movie_list.movies.all() else False}
                               for b in Movie.objects.filter(title__icontains=search_text).prefetch_related('genres')]
            else:
                movies_data = []
            ctx = {"movies_live_result": movies_data, "moviescount": len(movies_data), "searchtext": search_text}
            return HttpResponse(json.dumps(ctx), content_type='application/json; charset=utf-8')
        return super().get(self, request)

    def post(self, request, pk):
        """
        Xử lý POST request từ trang
        - Input:
            + Request từ trang Chi tiết Danh sách phim
            + id của Danh sách phim, lấy từ tham số url (pk)
        - Output: trả response chứa context của 1 trong 3 trường hợp
            + Xóa phim khỏi danh sách phim  (phương thức delete_movie_in_list)
            + Xóa danh sách phim  (phương thức delete_movielist)
            + Thêm phim danh sách phim  (phương thức add_movie_to_this_list)
        """
        ctx = {}
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.POST.get("operation") == "delete_movielist":
                ctx = self.delete_movielist(request, pk)
            elif request.POST.get("operation") == "delete_movie_in_list":
                ctx = self.delete_movie_in_list(request, pk)
            elif request.POST.get("operation") == "add_movie_to_this_list_submit":
                ctx = self.add_movie_to_this_list(request, pk)
        return HttpResponse(json.dumps(ctx), content_type='application/json')

    def delete_movie_in_list(self, request, pk):
        """
        Thực hiện chức năng Xóa phim khỏi danh sách phim
        - Input:
            + Request từ trang Chi tiết Danh sách phim
            + Id của Danh sách phim, lấy từ tham số url (pk)
        - Output:
            + Trường hợp giá trị operation nhận từ AJAX POST request là "delete_movie_in_list",
            thực hiện xoá phim khỏi danh sách phim trên cơ sở dữ liệu,
            trả về context chứa thông tin
            thông báo kết quả xóa, id của phim bị xóa, số lượng phim trong danh sách, id của danh sách phim liên quan
            + Ngược lại thì không làm gì
        """
        if request.POST.get("operation") == "delete_movie_in_list" and request.headers.get(
                'x-requested-with') == 'XMLHttpRequest':
            movie_id = int(request.POST.get("movie_id"))
            movie = get_object_or_404(Movie, pk=movie_id)
            movie_list = get_object_or_404(MovieList, user=self.request.user, id=pk)
            if movie in movie_list.movies.all():
                movie_list.movies.remove(movie)
                movie_list.last_modified = timezone.now()
                movie_list.save()
                deleted = True
            else:
                deleted = False
            ctx = {"deleted": deleted, "movie_id": movie_id, "moviescount": len(movie_list.movies.all()), "list_id": pk}
            return ctx

    def delete_movielist(self, request, pk):
        """
        Thực hiện chức năng Xóa danh sách phim
        - Input:
            + Request từ trang Chi tiết Danh sách phim
            + id của Danh sách phim, lấy từ tham số url (pk)
        - Output:
            + Trường hợp giá trị operation nhận từ AJAX POST request là "delete_movielist",
            thực hiện xoá danh sách phim trên cơ sở dữ liệu,
            thông báo kết quả xóa (thành công / không thành công)
            trả về context chứa thông tin
            link điều hường về trang tài khoản cá nhân của người dùng
            + Ngược lại thì không làm gì
        """
        if request.POST.get("operation") == "delete_movielist" and request.headers.get(
                'x-requested-with') == 'XMLHttpRequest':
            try:
                movie_list = get_object_or_404(MovieList, user=self.request.user, id=pk)
                if movie_list.type != "favorite":
                    movie_list.delete()
                    messages.success(request, "Đã xóa danh sách phim thành công")
            except:
                messages.error(request, "Xóa danh sách phim không thành công")
            ctx = {"link_to_redirect": reverse('movies:profile', kwargs={'user_username': self.request.user.username})}
            return ctx

    def add_movie_to_this_list(self, request, pk):
        """
        Thực hiện chức năng Thêm phim vào danh sách phim
        - Input:
            + Request từ trang Chi tiết Danh sách phim
            + id của Danh sách phim, lấy từ tham số url (pk)
        - Output:
            + Trường hợp giá trị operation nhận từ AJAX POST request là "add_movie_to_this_list_submit",
            thực hiện thêm phim vào danh sách phim trên cơ sở dữ liệu,
            trả về  context chứa thông tin
            kết quả thêm phim vào danh sách, thông tin của phim được thêm vào,
            số lượng phim trong danh sách, id của danh sách phim liên quan
            + Ngược lại thì không làm gì
        """
        if request.POST.get("operation") == "add_movie_to_this_list_submit" and request.headers.get(
                'x-requested-with') == 'XMLHttpRequest':
            moviescount = 0
            try:
                movie_id = int(request.POST.get("movie_id"))
                movie = get_object_or_404(Movie, pk=movie_id)
                movie_list = get_object_or_404(MovieList, user=self.request.user, id=pk)
                movie_list.movies.add(movie)
                movie_list.last_modified = timezone.now()
                movie_list.save()
                movie_added = {'id': movie.id, 'title': movie.title, 'year': movie.year,
                               'genres': ', '.join([b.name for b in movie.genres.all()])}
                moviescount = len(movie_list.movies.all())
                added = True
            except:
                added = False
                movie_added = {}
            ctx = {"added": added, "movie_added": movie_added, "moviescount": moviescount,
                   "list_id": pk}
            return ctx


class MovielistUpdateView(UpdateView):
    """
    Trang Cập nhật Danh sách phim, được kế thừa từ UpdateView của django
    """
    model = MovieList
    form_class = MovieListForm
    template_name = 'movies/movielist_form.html'

    def get_context_data(self, **kwargs):
        """
         Bổ sung context data cho trang: thêm giá trị submitButtonLabel, sectionTitle
         để chỉnh sửa nhãn cho giao diện
          - Input: Không có
          - Output: Context data có chứa giá trị submitButtonLabel
         """
        context = super(MovielistUpdateView, self).get_context_data(**kwargs)
        context['sectionTitle'] = "Cập nhật danh sách phim"
        context['submitButtonLabel'] = "Cập nhật thông tin"
        return context

    def form_valid(self, form):
        """
        Thêm thông tin cho form instance đuợc gửi đến trước khi lưu vào cơ sở dữ liệu
         - Input: kết quả form cập nhật Danh sách phim
         - Output: Hàm mặc định form_valid mà MovielistUpdateView được kế thừa từ UpdateView
          (sau khi tiến hành thêm thông tin cho form)
        """
        form.instance.last_modified = timezone.now()
        form.instance.user = self.request.user
        return super(MovielistUpdateView, self).form_valid(form)

    def get_success_url(self):
        """
        Xử lý và điều hướng trang khi lưu dữ liệu thành công
         - Input: không có
         - Output: Trả về trang Chi tiết Danh sách phim (tham số url chứa id của Danh sách phim đã được cập nhật)
        """
        messages.success(
            self.request, "Đã cập nhật danh sách phim")
        return reverse('movies:detail_movielist', kwargs={'pk': self.object.pk})
