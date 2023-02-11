from django.utils import timezone

from django.views import generic

from django.shortcuts import get_object_or_404, render

from django.http import HttpResponse

from movies.models import Movie, Genre, MovieList, Review
from django.db.models import Q, Case, Value, When

from django.core.paginator import Paginator

import json


class IndexView(generic.ListView):
    """
    Màn hình trang chủ, kế thừa từ ListView có sẵn của Django
    - Trong trang chủ có hiển thị danh sách phim mới phát hành
    """
    template_name = 'movies/index.html'
    context_object_name = 'movie_list'

    def get_queryset(self):
        """
        Lấy thông tin các phim ra mắt gần đây nhất để hiển thị trên trang chủ
        - Input: không có
        - Output: 12 phim ra mắt gần đây nhất xếp theo năm phát hành
        """
        return Movie.objects.order_by('-year')[:12]


class DetailView(generic.DetailView):
    """
    Màn hình trang Chi tiết thông tin phim, kế thừa từ DetailView
    - Hiển thị đầy đủ thông tin phim
    - Hiển thị nút yêu thích (Thêm vào Danh sách yêu thích)
    - Hiển thị form viết bình luận
    - Hiển thị các bình luận phim từ người dùng
    """
    model = Movie
    template_name = 'movies/detail.html'

    def get_context_data(self, **kwargs):
        """
        Bổ sung context data cho trang: thêm giá trị favorite_list chứa các phim
        yêu thích của người dùng (trong trường hợp đã đăng nhập)
        để xác định người dùng đã thêm phim hiện tại vào Danh Sách yêu thích chưa,
        thêm giá trị reviews để sắp xếp kết quả lọc phim theo ngày đăng lùi dần và
        nếu đăng nhập thì ưu tiên bài đăng của người đó lên đầu
         - Input: Thông tin user từ request
         - Output: Context data có chứa giá trị favorite_list (trong trường hợp đã đăng nhập) và reviews
        """
        context = super(DetailView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            reordered_reviews = Review.objects.filter(movie__id=self.kwargs['pk']).order_by(Case(
                When(user=self.request.user, then=Value(0)),
                default=Value(1)), '-last_modified')
            movielist = get_object_or_404(MovieList, user=self.request.user, type='favorite')
            context['reviews'] = reordered_reviews
            context['favorite_list'] = movielist.movies.all()
        else:
            context['reviews'] = Review.objects.filter(movie__id=self.kwargs['pk']).order_by('-last_modified')
        return context

    def get(self, request, *args, **kwargs):
        """
        Bổ sung xử lý GET request từ trang, thêm chức năng lấy thông tin Danh sách phim
        - Input: Request từ trang Chi tiết Danh sách phim
        - Output:
            + Trường hợp là request có operation là "get_movielists_from_username" gửi bằng AJAX
            thì xử lý và trả Response có context dạng json gồm các giá trị:
                . Danh sách các Danh sách phim (movielists)
                . Số lượng phim trong danh sách đó  (movielistscount)
            + Ngược lại thì theo phương thức get mặc định của DetailView
        """
        movie_id = self.kwargs['pk']
        if request.GET.get("operation") == "get_movielists_from_username" and request.headers.get(
                'x-requested-with') == 'XMLHttpRequest':
            username = request.GET.get('username')
            movie = get_object_or_404(Movie, pk=movie_id)
            movielists = [{'name': b.name, 'description': b.description, "id": b.id,
                                'added': True if movie in b.movies.all() else False}
                               for b in MovieList.objects.filter(user__username=username)]
            ctx = {"movielists": movielists, "movielistscount": len(movielists)}
            return HttpResponse(json.dumps(ctx), content_type='application/json; charset=utf-8')
        return super().get(self, request)

    def post(self, request, pk):
        """
        Xử lý POST request thêm phim vào Danh sách Yêu thích / Danh sách phim của người dùng
        - Input: Thông tin user từ request, id phim từ URL, id của Danh sách phim (trong trường hợp thêm danh sách phim)
        - Output: response dạng json gồm:
            + Giá trị added thông báo đã thực hiện thêm vào danh sách thành công,
            + Giá trị movie_id trả về id của phim đã thêm vào
        """
        movie_id = pk
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            movie_list = []
            if request.POST.get("operation") == "add_to_favorite_submit":
                movie_list = get_object_or_404(MovieList, user=self.request.user, type='favorite')
            elif request.POST.get("operation") == "add_to_list_submit":
                movielist_id = int(request.POST.get('movielist_id'))
                movie_list = get_object_or_404(MovieList, pk=movielist_id)
            movie = get_object_or_404(Movie, pk=movie_id)

            if movie in movie_list.movies.all():
                movie_list.movies.remove(movie)
                added = False
            else:
                movie_list.movies.add(movie)
                added = True
            movie_list.last_modified = timezone.now()
            movie_list.save()
            ctx = {"added": added, "movie_id": movie_id}
            return HttpResponse(json.dumps(ctx), content_type='application/json')


def browse_view(request):
    """
        Trang duyệt tìm phim
        - Input: Dựa trên Query string từ GET request, gồm các giá trị
            + genre
            + year
            + runtime
            + keyword
            + page (dùng để phân trang)
        - Output:
            Trang duyệt tìm chứa context gồm:
            + Các tùy chọn trong genres, year, runtime
            + filtered_movies: chứa các bộ phim đã loọc theo query string
            + url: chứa GET request của trang đã yêu cầu (dùng để phân trang)
    """
    from_req = {}
    queries = Q()

    get_query = request.GET.copy()
    if get_query.get('page'):
        del get_query['page']

    if get_query:
        get_req = get_query
        if get_req.get('genre') != 'all':
            q_genre = Q(genres__id=get_req.get('genre'))
            queries = queries & q_genre

        if get_req.get('year') != 'all':
            req_year = get_req.get('year')
            q_year = Q(year__range=[int(req_year), int(req_year) + 9])
            queries = queries & q_year

        if get_req.get('runtime') != 'all':
            req_runtime = get_req.get('runtime')
            if req_runtime == 180:
                q_runtime = Q(runtime__gt=180)
            elif req_runtime == 0:
                q_runtime = Q(runtime__lt=60)
            else:
                q_runtime = Q(runtime__range=[int(req_runtime) + 1, int(req_runtime) + 60])
            queries = queries & q_runtime

        if get_req.get('keyword') != '':
            req_keyword = get_req.get('keyword')
            q_keyword = Q(title__icontains=req_keyword)
            queries = queries & q_keyword

        from_req = dict(map(lambda x: (x[0], int(x[1]) if (x[1].isdigit()) else (x[0], x[1])), get_req.items()))

    if queries == Q():
        filtered_movies = Movie.objects.all()
    else:
        filtered_movies = Movie.objects.filter(queries)

    paginator = Paginator(filtered_movies, 30)
    page_number = request.GET.get('page')
    filtered_movies = paginator.get_page(page_number)

    browse_context = display_filter_fields() | {
        "from_req": from_req,
        "filtered_movies": filtered_movies,
        "query": get_query.urlencode()
    }
    return render(request=request, template_name="movies/browse.html", context=browse_context)


def display_filter_fields():
    """
    Hỗ trợ hiển thị trang Duyệt tìm(browse), tạo giá trị cho các trường chọn
    - Input: Không có
    - Output: dict chứa các giá trị genres, year, runtime

    """
    years = {}
    for year in range(2030, 1870, -10):
        years[year] = f"{year} - {year + 9}"

    runtimes = {0: "Dưới 60 phút",
                60: "Từ 60 đến 120 phút",
                120: "Từ 120 đến 180 phút",
                180: "Trên 180 phút"}

    return {"genres": Genre.objects.all(), "years": years, "runtimes": runtimes}
