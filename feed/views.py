from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import View, CreateView, DeleteView
from .forms import PhotoForm, TicketForm, ReviewForm, Review
from django.urls import reverse_lazy, reverse
from .models import Ticket
from itertools import chain
from django.core.paginator import Paginator
from django.db.models import Q

# Create your views here.
@login_required
def feed(request):
    return render(request, 'feed/home.html')

@login_required
def create_new_ticket(request):
  ticket_form = TicketForm()
  photo_form = PhotoForm()
  review_form = ReviewForm()
  if request.method == 'POST':
    ticket_form = TicketForm(request.POST)
    photo_form = PhotoForm(request.POST, request.FILES)
    review_form = ReviewForm(request.POST)
    if any([ticket_form.is_valid(),photo_form.is_valid(),review_form.is_valid()]):
       photo = photo_form.save(commit=False)
       photo.uploader = request.user
       photo.save()
       ticket = ticket_form.save(commit=False)
       ticket.image = photo
       ticket.user = request.user
       ticket.save()
       review = review_form.save(commit=False)
       review.ticket = ticket
       review.user = request.user
       review.save()
       return redirect(reverse('home'))
  forms = [ticket_form, photo_form, review_form]
  context = {
    'forms': forms,

  }
  return render(request, 'feed/new_ticket.html', context=context)

@login_required
def get_all_tickets(request):
   tickets = Ticket.objects.filter(user=request.user)
   return render(request, 'feed/all_tickets.html', context={'tickets': tickets})

@login_required
def get_single_ticket(request, ticket_id):
   ticket = get_object_or_404(Ticket, pk=ticket_id)
   return render(request, 'feed/ticket_detail.html', {'ticket':ticket})

@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, instance=ticket)
        image_form = PhotoForm(request.POST, request.FILES, instance=ticket.image)

        if ticket_form.is_valid() and image_form.is_valid():
            ticket.image.delete()
            image = image_form.save(commit=False)
            image.uploader = request.user
            image.save()
            ticket = ticket_form.save(commit=False)
            ticket.image = image
            ticket.user = request.user
            ticket.save()
            return redirect('ticket_detail', ticket_id=ticket_id)
    else:
        ticket_form = TicketForm(instance=ticket)
        image_form = PhotoForm(instance=ticket.image)

    return render(request, 'feed/edit_ticket.html', {'image_form': image_form, 'ticket_form': ticket_form, 'ticket': ticket})

def delete_ticket(request, ticket_id):
    return DeleteView.as_view(
        model=Ticket,
        success_url=reverse_lazy('all_tickets'),  # Redirect to a success URL after deletion
        template_name='feed/confirm_delete_ticket.html',  # Template for confirmation page
        context_object_name='ticket',  # Name to use for the ticket object in the template
        extra_context={'ticket_id': ticket_id},  # Pass ticket_id to the template
    )(request, pk=ticket_id)

def add_review(request, ticket_id):
   pass

@login_required
def feed(request):
    tickets = Ticket.objects.filter(
        user__in=request.user.follows.all()
    )
    reviews = Review.objects.filter(
        user__in=request.user.follows.all()
    )
    tickets_and_reviews = sorted(
        chain(tickets, reviews),
        key=lambda instance: instance.time_created,
        reverse=True
    )

    paginator = Paginator(tickets_and_reviews, 6)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    context = {
        'page_obj': page_obj
    }

    return render(
        request,
        'feed/home.html',
        context
    )

@login_required
def discover(request):
   tickets = Ticket.objects.exclude(user=request.user)
   tickets = sorted(
        tickets,
        key=lambda instance: instance.time_created,
        reverse=True
    )
   paginator = Paginator(tickets, 6)
   page = request.GET.get('page')
   page_obj = paginator.get_page(page)
   
   print(page_obj.__dict__)

   context = {
      'page_obj': page_obj,
   }

   return render(request, 'feed/discover.html', context)