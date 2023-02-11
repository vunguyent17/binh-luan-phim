from django.contrib.auth.decorators import login_required

from django.contrib import messages

from django.utils import timezone

from django.views.generic.edit import UpdateView

from django.shortcuts import get_object_or_404, render, redirect

from django.http import HttpResponseRedirect
from django.urls import reverse

from movies.models import Movie, Review, Genre, MovieList

from movies.forms import ReviewUpdateForm, MovieListForm

@login_required
def send_review(request, pk):
    """
    Xử lý request gửi form đánh giá phim của người dùng
    Yêu cầu người dùng đã đăng nhập mới có thể đăng đánh giá
    - Input:
        + Giá trị rating từ form
        + Giá trị comment từ form
        + Giá trị id phim được đánh giá, lấy từ tham số URL
    - Output:
        + Trường hợp người dùng viết thiếu mục thì trả về trang Chi tiết phim kèm thông báo lỗi
        + Trường hợp viết đủ mục thì lưu thông tin bài đánh giá và trả về trang Chi tiết phim
        kèm thông báo đã gửi bài đánh giá thành công
    """
    current_movie = get_object_or_404(Movie, pk=pk)
    try:
        rating = int(request.POST['rating'])
        if rating > 10:
            rating = 10
        if rating < 0:
            rating = 0
        comment = request.POST['comment']
    except KeyError:
        messages.error(request, "Bạn phải viết đầy đủ bài đánh giá")
        return render(request, 'movies/detail.html', {
            'movie': current_movie})
    else:
        new_review = Review(
            movie=current_movie,
            rating=rating,
            comment=comment,
            pub_date=timezone.now(),
            last_modified=timezone.now()
        )
        if request.user.is_authenticated:
            new_review.user = request.user
        new_review.save()

    messages.success(request, "Gửi bài đánh giá thành công")
    return HttpResponseRedirect(reverse('movies:detail', args=(current_movie.id,)))


@login_required
def delete_review(request, pk=None):
    """
    Xử lý request xóa bài đánh giá phim của người dùng
    Yêu cầu người dùng đã đăng nhập mới có thể xóa bài đánh giá
    - Input:
        + Request
        + Giá trị id cuủa bài đánh giá, lấy từ tham số URL
    - Output:
        + Thông báo kết quả xóa bài đánh giá
        + Điều hướng qua trang Chi tiết phim của phim bị xóa
    """
    review_to_delete = get_object_or_404(Review, pk=pk)
    try:
        review_to_delete.delete()
        messages.success(request, "Đã xóa bài đánh giá thành công")
    except:
        messages.error(request, "Xóa bài đăng không thành công")
    return HttpResponseRedirect(reverse('movies:detail', args=(review_to_delete.movie.id,)))


class ReviewUpdateView(UpdateView):
    """
    Trang Cập nhật Đánh giá phim, được kế thừa từ UpdateView của django
    """
    model = Review
    template_name_suffix = '_update_form'
    form_class = ReviewUpdateForm

    def get(self, request, *args, **kwargs):
        """
        Kiểm tra người dủng có phải chủ nhân bài đánh giá để tiến hành chỉnh sửa
        - Input: request
        - Output: Trường hơp không phải là do người dùng viết
        sẽ thông báo chỉ có thể sửa bài đăng của chính mình và điều hướng về
        trang Chi tiết phim
        Trường hợp dđúng là người viết yêu cầu thì trả response hiển thị form chỉnh sửa
        """
        self.object = self.get_object()
        if not self.object.user == request.user:
            messages.error(
                request, "Bạn chỉ có thể sửa bài đăng của mình")
            return redirect('movies:detail', pk=self.object.movie.pk)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def form_valid(self, form):
        """
        Thêm thông tin cho form instance đuợc gửi đến trước khi lưu vào cơ sở dữ liệu
         - Input: kết quả form cập nhật Bình luận phim
         - Output: Phương thưc mặc định form_valid mà ReviewUpdateView được kế thừa từ UpdateView
          (sau khi tiến hành thêm thông tin cho form)
        """
        form.instance.last_modified = timezone.now()
        return super(ReviewUpdateView, self).form_valid(form)

    def get_success_url(self):
        """
        Xử lý và điều hướng trang khi lưu dữ liệu thành công
         - Input: không có
         - Output: Trả về trang Chi tiết phim (tham số url chứa id phim có đánh giá phim đã được cập nhật)
        """
        messages.success(
            self.request, "Bài đánh giá của bạn đã được cập nhật")
        return reverse('movies:detail', kwargs={'pk': self.object.movie.pk})
