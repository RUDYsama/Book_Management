import secrets
import bcrypt
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Books, User
from .forms import BooksForm
from .serializers import BooksSerializer, LabUserSerializer
from .authentication import CustomJWTAuthentication
from .permissions import RoleBasedBookPermission


# ==========================================
# Web Page Views
# ==========================================

def dashboard_view(request):
    # Enforce login: redirect to login page if user is not authenticated
    if not request.session.get('user_id'):
        return redirect('login_page')

    current_user = request.session.get('user_name', '')
    current_email = request.session.get('user_email', '')
    current_role = request.session.get('user_role', 'viewer')

    form = BooksForm(request.POST or None) if "Books" in globals() else None
    if request.method == "POST" and form and form.is_valid():
        form.save()
        return redirect('dashboard')

    search = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '-id')
    items = []
    if "Books" in globals():
        qs = Books.objects.all()
        if search:
            try:
                qs = qs.filter(title__icontains=search)
            except Exception:
                qs = qs.filter(id__icontains=search)
        try:
            items = qs.order_by(sort)
        except Exception:
            items = qs.order_by('-id')

    return render(request, 'dashboard.html', {
        'form': form,
        'items': items,
        'search': search,
        'current_sort': sort,
        'model_name': 'Books',
        'current_user': current_user,
        'current_email': current_email,
        'current_role': current_role
    })


def delete_item_view(request, pk):
    if not request.session.get('user_id'):
        return redirect('login_page')
    item = get_object_or_404(Books, pk=pk)
    item.delete()
    return redirect('dashboard')


def edit_item_view(request, pk):
    if not request.session.get('user_id'):
        return redirect('login_page')
    item = get_object_or_404(Books, pk=pk)
    form = BooksForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'edit_item.html', {
        'form': form,
        'item': item,
        'model_name': 'Books'
    })


def register_page_view(request):
    return render(request, 'register.html')


def login_page_view(request):
    return render(request, 'login.html')


def logout_page_view(request):
    request.session.flush()
    return redirect('login_page')


# ==========================================
# Lab 9.2 API Endpoints
# ==========================================

class LabRegisterView(APIView):
    """
    POST /api/register
    Flow: Check email -> Generate verification_token -> INSERT users (plaintext pw) -> Send Verification Email
    """
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check duplicate email
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate 4-digit PIN for verification
        pin = f"{secrets.randbelow(9000) + 1000}"

        # Lab 9.3 Rule: Hash password with bcrypt before saving to DB
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10)).decode('utf-8')

        user = User.objects.create(
            name=name,
            email=email,
            password=hashed_password,
            role='viewer',
            is_verified=False,
            verification_token=pin
        )

        verify_url = request.build_absolute_uri(f"/api/verify?token={pin}")

        # Console notification
        print(f"\n=======================================================")
        print(f" [EMAIL SERVICE - GMAIL]")
        print(f" To: {email}")
        print(f" Subject: [Book Store] Your 4-Digit Verification PIN: {pin}")
        print(f" Verification PIN: {pin}")
        print(f" Verify URL: {verify_url}")
        print(f"=======================================================\n")

        # Send actual email via Gmail SMTP
        email_body = f"""Hello {name},

Thank you for registering with Book Store!

Your 4-digit verification PIN is:

    ======================
            {pin}
    ======================

Please enter this PIN on the verification screen to activate your account.
You can also verify by clicking this link:
{verify_url}

Best regards,
Book Store Team
"""
        try:
            send_mail(
                subject=f"[Book Store] Your 4-Digit Verification PIN: {pin}",
                message=email_body,
                from_email="Book Store <rtaxdt@gmail.com>",
                recipient_list=[email],
                fail_silently=False
            )
        except Exception as e:
            print(f"[MAIL NOTICE] Could not send via Gmail SMTP: {e}")

        return Response({
            "message": f"Verification PIN has been sent to {email}. Please enter the 4-digit PIN to verify.",
            "email": email,
            "pin": pin,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_verified": user.is_verified,
            },
            "verify_url": verify_url
        }, status=status.HTTP_201_CREATED)


class LabVerifyView(APIView):
    """
    GET /api/verify?token=... or pin=...
    POST /api/verify with {"email": "...", "pin": "..."}
    """
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.GET.get('token', '').strip()
        email = request.GET.get('email', '').strip()
        pin = request.GET.get('pin', '').strip() or token

        if not pin:
            return Response({"error": "Verification PIN is required"}, status=status.HTTP_400_BAD_REQUEST)

        query = User.objects.filter(verification_token=pin)
        if email:
            query = query.filter(email=email)
        user = query.first()

        if not user:
            return Response({"error": "Invalid or expired verification PIN"}, status=status.HTTP_400_BAD_REQUEST)

        user.is_verified = True
        user.verification_token = None
        user.save()

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'verify_success.html', {'user': user})

        return Response({
            "message": "Email verified successfully. You can now login.",
            "is_verified": True
        }, status=status.HTTP_200_OK)

    def post(self, request):
        email = request.data.get('email', '').strip()
        pin = request.data.get('pin', '').strip() or request.data.get('token', '').strip()

        if not pin:
            return Response({"error": "4-digit verification PIN is required"}, status=status.HTTP_400_BAD_REQUEST)

        query = User.objects.filter(verification_token=pin)
        if email:
            query = query.filter(email=email)
        user = query.first()

        if not user:
            return Response({"error": "Invalid or incorrect 4-digit PIN"}, status=status.HTTP_400_BAD_REQUEST)

        user.is_verified = True
        user.verification_token = None
        user.save()

        return Response({
            "message": "Account verified successfully! You can now login.",
            "is_verified": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }, status=status.HTTP_200_OK)


class LabLoginView(APIView):
    """
    POST /api/login
    Flow: Check email/password -> Check is_verified == True -> Login Success
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

        # Lab 9.3 Rule: Verify password using bcrypt.checkpw()
        is_password_valid = False
        try:
            stored_pw = user.password or ""
            if stored_pw.startswith('$2b$') or stored_pw.startswith('$2a$') or stored_pw.startswith('$2y$'):
                is_password_valid = bcrypt.checkpw(password.encode('utf-8'), stored_pw.encode('utf-8'))
            else:
                # Graceful backward compatibility for pre-9.3 plaintext accounts
                is_password_valid = (stored_pw == password)
        except Exception:
            is_password_valid = False

        if not is_password_valid:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if verified (Core condition of Lab 9.2)
        if not user.is_verified:
            return Response({
                "error": "Please verify your email before logging in",
                "is_verified": False
            }, status=status.HTTP_403_FORBIDDEN)

        user_role = getattr(user, 'role', 'viewer')

        # Generate JWT Token (SimpleJWT) with role claim
        refresh = RefreshToken.for_user(user)
        refresh['id'] = user.id
        refresh['name'] = user.name
        refresh['email'] = user.email
        refresh['role'] = user_role

        access_token_obj = refresh.access_token
        access_token_obj['id'] = user.id
        access_token_obj['name'] = user.name
        access_token_obj['email'] = user.email
        access_token_obj['role'] = user_role

        access_token = str(access_token_obj)
        refresh_token = str(refresh)

        # Set session for web browser (for Dashboard access)
        request.session['user_id'] = user.id
        request.session['user_name'] = user.name
        request.session['user_email'] = user.email
        request.session['user_role'] = user_role

        return Response({
            "message": "Login successful",
            "token": access_token,
            "access": access_token,
            "refresh": refresh_token,
            "tokens": {
                "access": access_token,
                "refresh": refresh_token,
            },
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user_role
            }
        }, status=status.HTTP_200_OK)


# ==========================================
# Books API Endpoints (Protected with JWT & RBAC)
# ==========================================

class BooksListCreateView(generics.ListCreateAPIView):
    """
    GET /api/books - List all books (viewer, editor, admin, manager)
    POST /api/books - Create new book (editor, admin, manager)
    """
    queryset = Books.objects.all()
    serializer_class = BooksSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, RoleBasedBookPermission]


class BooksDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/books/:id - Retrieve book (viewer, editor, admin, manager)
    PUT /api/books/:id - Update book (editor, admin, manager)
    DELETE /api/books/:id - Delete book (admin only)
    """
    queryset = Books.objects.all()
    serializer_class = BooksSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, RoleBasedBookPermission]
    lookup_field = 'pk'


# ==========================================
# Lab 9.4 Section 26: User Profile Endpoint
# ==========================================

class UserProfileView(APIView):
    """
    GET /api/profile
    Protected REST API: returns authenticated user's profile with role without password
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": getattr(user, 'role', 'viewer')
        }, status=status.HTTP_200_OK)


class CustomTokenRefreshView(APIView):
    """
    POST /api/token/refresh
    Exchange a valid refresh token for a new access token
    """
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_str = request.data.get('refresh', '').strip()
        if not refresh_str:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_str)
            return Response({"access": str(refresh.access_token)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Invalid or expired refresh token",
                "detail": str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)

