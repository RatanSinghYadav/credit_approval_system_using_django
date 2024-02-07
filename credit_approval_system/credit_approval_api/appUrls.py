from django.urls import path
from credit_approval_api.views import register, check_loan_eligibility, create_loan, view_loan_details, view_customer_loans

urlpatterns = [
    path('register/', register, name='register'),
    path('check-eligibility/', check_loan_eligibility, name='check-eligibility'),
    path('create-loan/', create_loan, name='create-loan'),
    path('view-loan/<int:loan_id>/', view_loan_details, name='view-loan'),
    path('view-loan/customer_id/<int:customer_id>/', view_customer_loans, name='customer-loan'),
]
 