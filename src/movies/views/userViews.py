from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string

from django.utils import timezone

from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode

from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q

from movies.models import MovieList

from movies.forms import PasswordChangeForm, UpdatedLoginForm, NewUserForm, SetPasswordForm

from django.conf import settings


@login_required
def profile_view(request, user_username):
    """
        Trang tài khoản cá nhân
        - Input: user_username của tài khoản cá nhân, dựa trên tham số URL
        - Output:
            Trang tài khoản cá nhân chứa context gồm:
            + Thông tin chủ trang tài khoản cá nhân đó (user)
            + Các bài đánh giá mà tài khoản đó đã tạo (reviews)
            + Số lượng các bài đánh giá (reviews_count)
            + Số lượng các bộ phim đã đánh giá (reviews_count)
            + Các danh sách phim mà tài khoản đó đã tạo (movielists)
    """
    current_user = get_object_or_404(User, username=user_username)
    reviews = current_user.review_set.order_by('-pub_date')
    reviews_count = reviews.count()
    movies_count = reviews.values('movie').distinct().count()
    profile_context = {"user": current_user, "reviews": reviews, "reviews_count": reviews_count,
                       "movies_count": movies_count,
                       'movielists': current_user.movielist_set}
    return render(request=request, template_name="registration/profile.html", context=profile_context)


def signup_request(request):
    """
    Xử lý request liên quan đến trang Đăng Ký (tạo tài khoản)
    - Input: request từ người dùng
    - Output:
        + Nếu request POST và form hợp lệ thì tiến hành lưu thông tin
        và đăng nhập bằng tài khoản vừa tạo, điều hướng về trang chủ
        + Nếu request POST và form không hợp lệ thì thông báo tạo tài khoản thất bại
        và đi đến trang đăng ký (có chứa thông tin chứa hợp lệ người dùng đã điền trước đó)
        + Nếu request GET thì trả về trang đăng ký chứa form đăng ký trống
    """
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            fav_list = MovieList.objects.create(
                name="Yêu thích",
                description="Những bộ phim mà bạn yêu thích",
                pub_date=timezone.now(),
                last_modified=timezone.now(),
                user=user,
                type="favorite")
            fav_list.save()
            login(request, user)
            messages.success(request, "Tạo tài khoản mới thành công")
            return redirect(reverse("movies:index"))
        messages.error(request, "Tạo tài khoản mới thất bại. Thông tin không hợp lệ.")
    form = NewUserForm()
    return render(request=request, template_name="registration/signup.html", context={"register_form": form})


def login_request(request):
    """
    Xử lý request liên quan đến trang Đăng Nhập
    - Input: request từ người dùng
    - Output:
        + Nếu request POST và form hợp lệ thì tiến hành xác thực
            . Nếu xác thực đúng thì tiến hành đăng nhập, thông báo đã đăng nhập thành công,
             điều hướng về trang chủ
             . Nếu xác thực sai thì thông báo Tên người dùng hay Mật khẩu không hợp lệ,
             đi đến trang đăng nhập
        + Nếu request POST và form không hợp lệ thì thông báo Bạn cần điền đầy đủ thông tin,
        đi đến trang đăng nhập
        + Nếu request GET thì đi đến trang đăng nhập
    """
    if request.method == "POST":
        form = UpdatedLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Bạn đã đăng nhập với tên người dùng <b>{username}</b>.")
                return redirect(reverse("movies:index"))
            else:
                messages.error(request, "Tên người dùng hay Mật khẩu không hợp lệ.")
        else:
            messages.error(request, "Bạn cần điền đầy đủ thông tin.")
    form = UpdatedLoginForm()
    return render(request=request, template_name="registration/login.html", context={"login_form": form})


def logout_request(request):
    """
    Xử lý request đăng xuất
    - Input: request từ người dùng
    - Output:
       + Thực hiện đăng xuất, thông báo đã đăng xuất thành công,
       + Điều hướng đến trang đăng nhập
    """
    logout(request)
    messages.info(request, f"Bạn đã đăng xuất.")
    return redirect(reverse("movies:login"))


@login_required
def password_change(request):
    """
    Xử lý request liên quan đến trang Đổi mật khẩu
    - Input: request từ người dùng
    - Output:
        + Nếu request POST và form hợp lệ thì:
            . Lưu thông tin mật khẩu mới, thông báo đổi mật khẩu thành công
            . Điều hướng đến trang Đăng nhập
        + Nếu request POST và form không hợp lệ thì thông báo lỗi và đi đến trang Đổi mật khẩu
        + Nếu request GET thì đi đến trang Đổi mật khẩu
    """
    user = request.user
    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Mật khẩu đã được đổi thành công")
            return redirect('movies:login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    form = PasswordChangeForm(user)
    return render(request, 'registration/password_change_form.html', {'password_change_form': form})


def password_reset_request(request):
    """
    Xử lý request liên quan đến trang Khởi động lại mật khẩu
    - Input: request từ người dùng
    - Output:
        + Nếu request POST và form hợp lệ thì tiến hành lấy email đối chiếu với email của người dùng
        trong cơ sở dữ liệu, nếu có thì tiến hành gửi thư đến email đó để thực hiện Khởi động lại mật khẩu.
        Sau khi gửi xong đi đến trang /accounts/password-reset/done/
        + Nếu request POST và form không hợp lệ hoặc không tìm thấy người dùng khớp thì
        thông báo lỗi và tải trang Khởi động mật khẩu
        + Nếu request GET thì đi đến trang Khởi động mật khẩu
    """
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Khởi động mật khẩu tài khoản trên trong Bình Luận Phim"

                    email_template_name = "registration/password_reset_email_html_template.html"
                    c = {
                        "email": user.email,
                        'domain': settings.SITE,
                        'site_name': 'Bình Luận Phim',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    html_message = render_to_string(email_template_name, c)
                    plain_message = strip_tags(html_message)
                    try:
                        send_mail(subject, plain_message, 'admin@example.com', [user.email], fail_silently=False,
                                  html_message=html_message)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/accounts/password-reset/done/")
            else:
                messages.error(request, "Không thấy thông tin của email này trong cơ sở dữ liệu.")
        else:
            messages.error(request, "Bạn cần điền đầy đủ thông tin.")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name='registration/password_reset_email.html',
                  context={"password_reset_form": password_reset_form})


class PasswordResetConfirmView(PasswordResetConfirmView):
    form_class = SetPasswordForm
