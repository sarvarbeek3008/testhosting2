from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Index
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.generic import FormView, TemplateView, ListView, DetailView

from app.form import ProdctModelForm, LoginForm, RegisterForm, ForgotPasswordForm, send_email
from app.models import Product, Category, User
from app.token import account_activation_token


# def index(request):
#     products = Product.objects.order_by('-id')
#     context = {
#         "products": products
#     }
#     return render(request, 'app/index.html', context)

class IndexPage(ListView):
    template_name = 'app/index.html'
    model = Product


# def product_details(request, product_id):
#     product = Product.objects.filter(id=product_id).first()
#     context = {
#         'product': product
#     }
#     return render(request, 'app/product_details.html', context)

class ProductDetailsPage(DetailView):
    template_engine = Product.objects.order_by('-id')
    template_name = 'app/product_details.html'
    model = Product

# def shop_view(request):
#     products = Product.objects.all()
#     context = {
#         'products': products
#     }
#     return render(request, 'app/shop.html', context)


class ShopPage(ListView):
    template_name = 'app/shop.html'
    model = Product
    queryset = Product.objects.all()
    context_object_name = 'products'
    # paginate_by = 3

    def get_queryset(self):
        title = self.request.GET.get('title')
        if title:
            return Product.objects.filter(title__icontains=title)
        return Product.objects.all()


def shopping_cart(request):
    return render(request, 'app/shopping_cart.html')


def contact(request):
    return render(request, 'app/contact.html')


def checkout(request):
    return render(request, 'app/checkout.html')


def create_product(request):
    category = Category.objects.all()
    if request == 'POST':
        form = ProdctModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('index')
    form = ProdctModelForm()
    context = {
        'form': form,
        'sizes': Product.ChoiceSize,
        'colors': Product.ChoiceColor,
        'price': Product.price,
        'categories': category
    }
    return render(request, 'app/create_product.html', context)


def update_product(request, product_id):
    category = Category.objects.all()
    product = Product.objects.filter(id=product_id).first()
    if request.method == 'POST':
        form = ProdctModelForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
        return redirect('index')

    form = ProdctModelForm(instance=product)
    context = {
        "form": form,
        'sizes': Product.ChoiceSize,
        'colors': Product.ChoiceColor,
        'categories': category
    }
    return render(request, 'app/update_product.html', context)


def login_view(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect('index')

    return render(request, 'app/auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return render(request, 'app/auth/logout.html')


def register_view(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            send_email(form.data.get('email'), request, 'register')
            messages.add_message(
                request,
                level=messages.INFO,
                message='Xabar yuborildi, emailingizni tekshiring'
            )
            return redirect('register')
    return render(request, 'app/auth/register.html', {'form': form})


class ForgotPasswordView(FormView):
    template_name = 'app/auth/forgot_password.html'
    success_url = reverse_lazy('login')
    form_class = ForgotPasswordForm

    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)


class ActivateEmailView(TemplateView):
    template_name = 'app/auth/confirm_email.html'

    def get(self, request, *args, **kwargs):
        uid = kwargs.get('uid')
        token = kwargs.get('token')

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except Exception as e:
            print(e)
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            messages.add_message(
                request=request,
                level=messages.SUCCESS,
                message="Your account successfully activated!"
            )
            return redirect('index')
        else:
            return HttpResponse('Activation link is invalid!')


def new_product(request):
    products = Product.objects.order_by('-id')
    context = {
        'products':products
    }
    return render(request, 'app/auth/new_product.html', context)

def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect('index')
