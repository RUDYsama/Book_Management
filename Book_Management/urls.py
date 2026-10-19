from django.contrib import admin
from django.urls import path
from .views import (
    dashboard_view,
    delete_item_view,
    edit_item_view,
    register_page_view,
    login_page_view,
    logout_page_view,
    LabRegisterView,
    LabVerifyView,
    LabLoginView,
    CustomTokenRefreshView,
    UserProfileView,
    BooksListCreateView,
    BooksDetailView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='dashboard'),
    path('books/edit/<int:pk>/', edit_item_view, name='item_edit'),
    path('books/delete/<int:pk>/', delete_item_view, name='item_delete'),

    # Lab 9.2 Web UI Pages
    path('register/', register_page_view, name='register_page'),
    path('login/', login_page_view, name='login_page'),
    path('logout/', logout_page_view, name='logout'),

    # Lab 9.2 API Endpoints (supports both with and without trailing slash)
    path('api/register/', LabRegisterView.as_view(), name='lab_register'),
    path('api/register', LabRegisterView.as_view()),
    path('api/verify/', LabVerifyView.as_view(), name='lab_verify'),
    path('api/verify', LabVerifyView.as_view()),
    path('api/login/', LabLoginView.as_view(), name='lab_login'),
    path('api/login', LabLoginView.as_view()),

    # JWT Token Refresh
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/refresh', CustomTokenRefreshView.as_view()),

    # Lab 9.4 Section 26: User Profile
    path('api/profile/', UserProfileView.as_view(), name='user_profile'),
    path('api/profile', UserProfileView.as_view()),

    # Books API Endpoints
    path('api/books/', BooksListCreateView.as_view(), name='books_list_create'),
    path('api/books', BooksListCreateView.as_view()),
    path('api/books/<int:pk>/', BooksDetailView.as_view(), name='books_detail'),
    path('api/books/<int:pk>', BooksDetailView.as_view()),
]


