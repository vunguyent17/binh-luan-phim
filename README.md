# Cửa Hàng Sách Website

<img src="https://github.com/vunguyent17/binh-luan-phim/blob/main/Screenshots/Picture1.png" data-canonical-src="https://github.com/vunguyent17/binh-luan-phim/blob/main/Screenshots/Picture1.png" style="display:block; margin-left: auto; margin-right: auto; width: 80%" alt="Trang chủ" />

## Giới thiệu / Introduction

Website Bình Luận Phim là ứng dụng web cho phép người dùng có thể đăng ký tài khoản, duyệt tìm thông tin phim, viết bài đánh giá cho các phim, tạo danh sách phim cá nhân


Bình Luận Phim Website is a web application that allows users to browse and find information about movies, create movie reviews and personal movie lists.


### Chức năng của ứng dụng / Functionality:
- Duyệt tìm thông tin, lọc các phim
- Tạo tài khoản, đăng ký, đăng nhập, đăng xuất, khởi động lại mật khẩu, đổi mật khẩu
- Viết các bài đánh giá phim và cho điểm. Cho phép chỉnh sửa,  xóa bài đánh giá
- Lưu lại / bỏ lưu các bộ phim yêu thích
- Tạo danh sách các bộ phim. Chỉnh sửa tên và mô tả danh sách. Tìm, thêm và xóa phim trong danh sách


 <br/>

- Browse movies, filter by name, genres, ...
- Sign up, log in, change password
- Post reviews including ratings and comments. Allow to update or delete reviews
- Save / unsave your favorite movies
- Create movie lists. Modify title and description of movie lists. Find, add, remove movies in the lists 

### Công nghệ sử dụng / Tech stack:
- Programming language: Python 3, JavaScript
- Web Framework: [Django](https://www.djangoproject.com/) 
-	Database: [PostgreSQL](https://www.postgresql.org/)
-	CSS library: [Bootstrap 5](https://getbootstrap.com/)
- Deploy database and web application on render.com

### Dịch vụ bên thứ ba / Third-party services:
- SMTP Server (Gửi thông tin email khởi động lại tài khoản): [MailTrap](https://mailtrap.io/)

### Template
https://themewagon.github.io/cyborg/

## Demo
[Link video demo](https://drive.google.com/file/d/1HJ2KIlPDBXLNBYg_Xb00smFRIG9tNZ15/view?usp=sharing)
<br/>
[Link website](https://binh-luan-phim.onrender.com/)
(Sample account: username: vunt, password: Testing@123)

## Set up project locally
### Prerequisites
- Python 3
- PostgreSQL, pgAdmin 4
- MailTrap account

### Installation (on Windows)

1. Clone the repo

2. Create database
- Connect pgAdmin to local PostgreDB Database. Create database BinhLuanPhim
- Restore database from file BinhLuanPhim.sql

3. Configure settings
- Open project folder in Visual Studio Code
- Create a new file name development.py in `src/moviesite/setting/`. Paste the code below and fill in necessary information

```
import os
from django.core.management.utils import get_random_secret_key
from moviesite.settings.common import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
def generate_secret_key (filepath):
    secret_file = open(filepath, "w")
    secret = "SECRET_KEY= " + "\""+ get_random_secret_key() + "\"" + "\n"
    secret_file.write(secret)
    secret_file.close()

try:
    from .secret_key import SECRET_KEY
except ModuleNotFoundError:
    SETTINGS_DIR = os.path.abspath(os.path.dirname(__file__))
    generate_secret_key(os.path.join(SETTINGS_DIR, 'secret_key.py'))
    from .secret_key import SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
SITE = "127.0.0.1:8000"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'BinhLuanPhim',
        'USER': '<put your local database username here>',
        'PASSWORD': '<put your local database password here>',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

EMAIL_HOST = 'smtp.mailtrap.io'
EMAIL_HOST_USER = '<put your mailtrap inbox username here>'
EMAIL_HOST_PASSWORD = '<put your mailtrap inbox password here>'
EMAIL_PORT = '2525'
```

3. Run web application:
- Run `.\Scripts\Activate.ps1` to run Python virtual environment
- Run `py manage.py migrate` to check for migrations which haven't applied yet
- Run `py manage.py runserver` to run web client at localhost:8000


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
