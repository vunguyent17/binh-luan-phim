from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import Review, MovieList


# Create your forms here.

class NewUserForm(UserCreationForm):
    """
    Thiết lập form đăng ký cho website, chỉnh sửa nhãn, thêm trường email
    """
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        """
        Chỉnh sửa nhãn cho form
        - Input: không có
        - Output: form có nhãn và help text được chỉnh sửa
        """
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Tên người dùng'
        self.fields['username'].help_text = 'Tên người dùng ít hơn 150 ký tự. Chỉ dùng chữ, số và các ký tự @/./+/-/_ '
        self.fields['password1'].label = 'Mật khẩu'
        self.fields[
            'password1'].help_text = 'Mật khẩu mới không được quá giồng với mật khẩu cũ,' \
                                     ' có ít nhất 8 ký tự, có tính bảo mật, và không được chứa toàn số'
        self.fields['password2'].label = 'Nhập lại mật khẩu'
        self.fields['password2'].help_text = 'Nhập lại mật khẩu như trên để xác minh'

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        """
        Bồ sung thêm thông tin email từ form trước khi lưu dữ liệu User
        - Input: không có
        - Output: user có chứa thông tin email
        """
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """
    Thiết lập form đăng nhập cho website, chỉnh sửa nhãn, thêm trường remember_me
    """
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    def __init__(self, *args, **kwargs):
        """
        Sửa lại nhãn cho các trường trong form đăng nhập
        """
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Tên người dùng'
        self.fields['password'].label = 'Mật khẩu'
        self.fields['remember_me'].label = 'Lưu đăng nhập'

    class Meta:
        model = get_user_model()
        fields = ('username', 'password')


class UpdatedLoginForm(LoginForm):
    """
        Kế thừa từ LoginForm và thêm tính năng ghi nhớ đăng nhập
    """
    form_class = LoginForm

    def form_valid(self, form):
        """
        Xử lý tính năng Ghi nhớ đăng nhập
        - Input: form đăng nhập
        - Output: Khi gửi form bổ sung thêm bước Nếu không có remember me thì thiết lập
        session cookie sẽ hết hạn khi đóng trình duyệt.
        """
        remember_me = form.cleaned_data['remember_me']  # get remember me data from cleaned_data of form
        if not remember_me:
            self.request.session.set_expiry(0)  # if remember me is
            self.request.session.modified = True
        return super(UpdatedLoginForm, self).form_valid(form)


class PasswordChangeForm(PasswordChangeForm):
    """
    Chỉnh sửa các nhãn
    """

    def __init__(self, *args, **kwargs):
        """
        Chỉnh sửa các nhãn
        - Input: không có
        - Output: form có nhãn và help text được chỉnh sửa
        """
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Mật khẩu hiện tại'
        self.fields['new_password1'].label = 'Mật khẩu mới'
        self.fields['new_password2'].label = 'Nhập lại mật khẩu mới'
        self.fields[
            'new_password1'].help_text = 'Mật khẩu mới không được quá giồng với mật khẩu cũ, ' \
                                         'có ít nhất 8 ký tự, có tính bảo mật, và không được chứa toàn số'

    class Meta:
        model = get_user_model()
        fields = ('old_password', 'new_password1', 'new_password2')


class SetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        """
        Chỉnh sửa các nhãn
        - Input: không có
        - Output: form có nhãn và help text được chỉnh sửa
        """
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = 'Mật khẩu mới'
        self.fields['new_password2'].label = 'Nhập lại mật khẩu mới'
        self.fields[
            'new_password1'].help_text = 'Mật khẩu mới không được quá giồng với mật khẩu cũ, ' \
                                         'có ít nhất 8 ký tự, có tính bảo mật, và không được chứa toàn số'


class ReviewUpdateForm(forms.ModelForm):
    """
    Chỉnh sửa các nhãn, thay đổi loại input của comment là textarea
    """

    class Meta:
        model = Review
        fields = ('rating', 'comment')
        labels = {'rating': 'Đánh giá', 'comment': 'Nhận xét'}
        widgets = {
            'rating': forms.NumberInput(attrs={'name': "rating", 'min': 0, 'max': 10, 'step': 1}),
            'comment': forms.Textarea,
        }
        help_texts = {
            'rating': '<span class="my-class">Trên thang điểm 10</span>',
        }


class MovieListForm(forms.ModelForm):
    """
    Chỉnh sửa các nhãn, thay đổi loại input của description là textarea
    """

    class Meta:
        model = MovieList
        fields = ('name', 'description')
        labels = {'name': 'Tiêu đề danh sách phim', 'description': 'Mô tả'}
        widgets = {
            'description': forms.Textarea,
        }
