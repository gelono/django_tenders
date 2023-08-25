from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, FormView, ListView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from django_tenders.permissions import IsAdminOrReadAndPutOnly
from tenders.filters import ArchiveTenderFilter, CustomerFilter, WinnerFilter, ActiveTenderFilter
from tenders.forms import RegisterUserForm, UpdateUserForm
from tenders.models import ArchiveTender, Customer, Subscriber, Winner, SubscriberBalance, TransactionIn, \
    ExtendedCompanyData, ActiveTender, TransactionOut, DKNumber
from tenders.serializers import ArchiveTenderSerializer, CustomerSerializer, WinnerSerializer, \
    SubscriberBalanceSerializer, TransactionInSerializer, ExtendedCompanyDataSerializer, TransactionOutSerializer, \
    ActiveTenderSerializer
from tenders.utils import TenderMixin


class ArchiveTenderViewSet(TenderMixin, ModelViewSet):
    serializer_class = ArchiveTenderSerializer
    filterset_class = ArchiveTenderFilter
    queryset = ArchiveTender.objects.all()

    def get_queryset(self):
        return self.get_queryset_mixin(model=ArchiveTender)


class ActiveTenderViewSet(TenderMixin, ModelViewSet):
    serializer_class = ActiveTenderSerializer
    filterset_class = ActiveTenderFilter
    queryset = ActiveTender.objects.all()

    def get_queryset(self):
        return self.get_queryset_mixin(model=ActiveTender)


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomerFilter


class WinnerViewSet(ModelViewSet):
    queryset = Winner.objects.all()
    serializer_class = WinnerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = WinnerFilter


class BalanceViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrReadAndPutOnly, ]  # IsAdminOrReadOnly, BalanceIsAdmin,
    serializer_class = SubscriberBalanceSerializer
    queryset = SubscriberBalance.objects.all()

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        else:
            user = self.request.user
            subscriber = Subscriber.objects.get(user=user)
            return self.queryset.filter(subscriber=subscriber)


class TransactionInView(APIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = TransactionInSerializer
    queryset = TransactionIn.objects.all()

    def get(self, request):
        user = request.user

        if user.is_staff:
            data = self.queryset.all()
            serializer = TransactionInSerializer(data, many=True)
            return Response(serializer.data)

        subscriber = Subscriber.objects.select_related('subscriberbalance').get(user=user)  # fix added
        subscriber_balance = subscriber.subscriberbalance
        data = self.queryset.filter(subscriber_balance=subscriber_balance)
        serializer = TransactionInSerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        user = request.user
        subscriber = Subscriber.objects.select_related('subscriberbalance').get(user=user)  # fix added
        user_subscriber_balance = subscriber.subscriberbalance
        serializer = TransactionInSerializer(data=request.data)
        if serializer.is_valid():
            transaction = serializer.save(subscriber_balance=user_subscriber_balance)
            subscriber_balance = transaction.subscriber_balance
            subscriber_balance.current_balance += transaction.amount
            subscriber_balance.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExtendedCompanyDataView(APIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ExtendedCompanyDataSerializer
    queryset = ExtendedCompanyData.objects.all()

    def get(self, request):
        user = request.user
        company_id = request.query_params.get('id')
        try:
            data = self.queryset.get(id=company_id)
        except ObjectDoesNotExist:
            data = None

        if user.is_staff:
            if not company_id:
                data = self.queryset.all()
                serializer = ExtendedCompanyDataSerializer(data, many=True)
                return Response(serializer.data)

            if data:
                serializer = ExtendedCompanyDataSerializer(data)
                return Response(serializer.data)
            else:
                return Response('The company was not found', status=status.HTTP_400_BAD_REQUEST)

        subscriber = Subscriber.objects.select_related('subscriberbalance').get(user=user)  # fix added
        subscriber_balance = subscriber.subscriberbalance
        if subscriber_balance.current_balance >= 10:
            if data:
                serializer = ExtendedCompanyDataSerializer(data)
                trans_data = {
                    'amount': 10,
                    'currency': 'UAH'
                }
                serializer_out = TransactionOutSerializer(data=trans_data)
                if serializer_out.is_valid():
                    transaction = serializer_out.save(subscriber_balance=subscriber_balance)
                    subscriber_balance.current_balance -= transaction.amount
                    subscriber_balance.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response('The company was not found', status=status.HTTP_404_NOT_FOUND)

        return Response('The lack of funds', status=status.HTTP_400_BAD_REQUEST)


class ProfileUser(LoginRequiredMixin, DetailView):
    model = Subscriber
    template_name = 'tenders/profile.html'
    slug_url_kwarg = 'username'
    context_object_name = 'subscriber'
    login_url = reverse_lazy('login')

    def get_object(self, queryset=None):
        # Get the username from the URL
        username = self.kwargs.get(self.slug_url_kwarg)

        # Get the user id from the User model
        user = User.objects.get(username=username)
        user_id = user.id

        # Retrieve the Subscriber object based on user_id
        subscriber = get_object_or_404(Subscriber, user_id=user_id)
        return subscriber

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the subscriber object
        subscriber = context['subscriber']

        # Retrieve the related codifiers information
        dk_numbers = list(subscriber.dk_numbers.all())

        # Retrieve transactions related to the subscriber
        transactions_in = TransactionIn.objects.filter(subscriber_balance=subscriber.subscriberbalance)
        transactions_out = TransactionOut.objects.filter(subscriber_balance=subscriber.subscriberbalance)

        # Add the values to the context dictionary
        context['dk_numbers'] = dk_numbers
        context['transactions_in'] = list(transactions_in)
        context['transactions_out'] = list(transactions_out)

        # Include the UpdateUserForm instance in the context
        update_user_form = UpdateUserForm(instance=self.request.user)
        context['update_user_form'] = update_user_form

        return context

    def post(self, request, *args, **kwargs):
        # Get the subscriber object
        subscriber = self.get_object()

        # Create an instance of the UpdateUserForm
        update_user_form = UpdateUserForm(request.POST, instance=subscriber.user)

        if update_user_form.is_valid():
            # Update User model fields
            user = update_user_form.save()

            # Redirect to the profile page
            return HttpResponseRedirect(reverse('profile', kwargs={'username': user.username}))

        # If form data is not valid, re-render the profile page with errors
        context = self.get_context_data()
        context['update_user_form'] = update_user_form
        return self.render_to_response(context)


class RegisterUser(FormView):
    form_class = RegisterUserForm
    template_name = 'tenders/register.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Реєстрація'
        return context

    def form_valid(self, form):
        # Create the User instance
        user = form.save()

        # Create the Subscriber instance
        subscriber = Subscriber.objects.create(
            user=user,
            phone_number=form.cleaned_data['phone_number']
        )

        # Create the SubscriberBalance instance
        SubscriberBalance.objects.create(subscriber=subscriber)

        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return super(RegisterUser, self).form_valid(form)

    def get_success_url(self):
        user = self.request.user
        return reverse_lazy('profile', kwargs={'username': user.username})


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'tenders/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизація'
        return context

    def get_success_url(self):
        user = self.request.user
        return reverse_lazy('profile', kwargs={'username': user.username})

def index(request):
    return render(request, 'tenders/index.html', {'title': 'Головна сторінка'})


class CodifierView(LoginRequiredMixin, ListView):
    model = DKNumber
    template_name = 'tenders/codifiers.html'
    context_object_name = 'dk_numbers'
    object_list = DKNumber.objects.all()
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dk_numbers_subs = self.request.user.subscriber.dk_numbers.all()

        # For the searching
        search_result = 'Введіть параметри пошуку'
        search_description = self.request.GET.get('search_description')
        if search_description:
            dk_numbers_search = self.object_list.filter(
                Q(description__icontains=search_description)
            )
            if dk_numbers_search:
                context['dk_numbers_search'] = dk_numbers_search
            else:
                search_result = f'За вказаними даними "{search_description}" кодифікатори не знайдені'

        context['object_list'] = self.object_list
        context['dk_numbers_subs'] = dk_numbers_subs
        context['search_result'] = search_result


        return context

    def post(self, request, *args, **kwargs):
        # Get the selected value from the form
        selected_dk_number = request.POST.get('dk_number')

        # Delete the dk number from subscriptions
        if 'delete' in request.POST:
            dk_name = request.POST.get('dk_to_delete')
            dk_to_delete = DKNumber.objects.get(dk=dk_name)
            self.request.user.subscriber.dk_numbers.remove(dk_to_delete)
            return redirect('codifiers')

        # Update subscriptions
        new_dk_number = DKNumber.objects.get(dk=selected_dk_number)
        if new_dk_number in list(self.request.user.subscriber.dk_numbers.all()):
            about_subs = 'Ви вже підписані на цей кодифікатор:'
        else:
            self.request.user.subscriber.dk_numbers.add(new_dk_number)
            about_subs = 'Ви підписались на кодифікатор:'

        # Update the context and render the template
        context = self.get_context_data()
        context['selected_dk_number'] = selected_dk_number
        context['about_subs'] = about_subs

        return render(request, self.template_name, context)
