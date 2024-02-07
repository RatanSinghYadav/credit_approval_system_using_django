from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Customer

@shared_task
def process_customer_data():
   
    customers = Customer.objects.all()

    for customer in customers:
       
        print(f"Processing customer: {customer.first_name} {customer.last_name}")
