import os

import django
from faker import Faker
from PIL import Image

from authentication.models import User
from feed.models import Photo, Review, Ticket

# Configure Django's settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "litrevu.settings")
django.setup()

# Create a Faker instance
fake = Faker()


# Generate and save fake User objects
def generate_fake_users(num_users=10):
    for _ in range(num_users):
        username = fake.user_name()
        email = fake.email()
        profile_photo = fake.image_url()
        user = User(
            username=username,
            email=email,
            profile_photo=profile_photo,
        )
        user.set_password("S3cret!!!")  # Set a default password for users
        user.save()


# Generate and save fake Photo, Ticket, Review objects, and UserFollows relationships
def generate_fake_data(num_photos=10, num_tickets=10, num_reviews_per_ticket=3):
    users = User.objects.all()  # Get all users to use for relationships

    for _ in range(num_photos):
        file_path = fake.image_filename()
        caption = fake.sentence(nb_words=6)
        uploader = fake.random_element(users)  # Get a random user as the uploader

        # Create a new Photo instance
        photo = Photo(
            file=file_path,
            caption=caption,
            uploader=uploader,
        )
        photo.save()

    for _ in range(num_tickets):
        title = fake.sentence(nb_words=4)
        description = fake.paragraph(nb_sentences=3)
        user = fake.random_element(users)  # Get a random user

        # Create a new Ticket instance
        ticket = Ticket(
            title=title,
            description=description,
            user=user,
        )
        ticket.save()

        for _ in range(num_reviews_per_ticket):
            rating = fake.random_int(min=1, max=5)
            headline = fake.sentence(nb_words=4)
            body = fake.paragraph(nb_sentences=3)
            user = fake.random_element(users)  # Get a random user

            # Create a new Review instance associated with the Ticket
            review = Review(
                ticket=ticket,
                rating=rating,
                user=user,
                headline=headline,
                body=body,
            )
            review.save()

        # Create UserFollows relationships
        user_follows = fake.random_elements(users, unique=True, length=fake.random_int(min=1, max=len(users) - 1))
        for followed_user in user_follows:
            user.follows.add(followed_user)


if __name__ == "__main__":
    from django.contrib.auth.models import User  # Import User model

    # Call the function to generate fake User, Photo, Ticket, Review objects, and relationships
    generate_fake_users()
    generate_fake_data()
