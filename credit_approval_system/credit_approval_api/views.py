from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .backgroundTask import process_customer_data
from django.views.decorators.csrf import csrf_exempt
from .models import Customer, Loan
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
from datetime import datetime

# Create your views here.

# /register api endpoint

@csrf_exempt
def register(request):
    # process_customer_data.delay()

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        age = request.POST.get('age')
        monthly_income = request.POST.get('monthly_income')
        phone_number = request.POST.get('phone_number')
        
        approved_limit = round(36 * int(monthly_income), -5)

        
        customer = Customer.objects.create(
            first_name=first_name,
            last_name=last_name,
            age=age,
            monthly_salary=monthly_income,
            approved_limit=approved_limit,
            phone_number=phone_number
        )

        
        response_data = {
            'customer_id': customer.customer_id,
            'name': f"{customer.first_name} {customer.last_name}",
            'age': customer.age,
            'monthly_income': customer.monthly_salary,
            'approved_limit': customer.approved_limit,
            'phone_number': customer.phone_number
        }

        return JsonResponse(response_data, status=201)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


# /check-eligibility api endpoint

@csrf_exempt
def check_loan_eligibility(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        loan_amount = float(request.POST.get('loan_amount'))
        interest_rate = float(request.POST.get('interest_rate'))
        tenure = int(request.POST.get('tenure'))
        
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer does not exist'}, status=400)
        
        credit_score = calculate_credit_score(customer)
        loan_approval, corrected_interest_rate = check_loan_approval(customer, credit_score, interest_rate)
        monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
        
        response_data = {
            'customer_id': customer_id,
            'approval': loan_approval,
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_interest_rate, 
            'tenure': tenure,
            'monthly_installment': monthly_installment
        }
        
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)

def calculate_credit_score(customer):
    past_loans_paid_on_time = customer.loan_set.filter(emis_paid_on_time=True).count()
    total_loans_taken = customer.loan_set.count()
    loan_activity_current_year = customer.loan_set.filter(start_date__year=2024).count()
    approved_limit = customer.approved_limit
    
    credit_score = 0
    if past_loans_paid_on_time > 5:
        credit_score += 20
    if total_loans_taken <= 3:
        credit_score += 10
    if loan_activity_current_year > 0:
        credit_score += 15
    if approved_limit >= 500000:
        credit_score += 20
    
    return credit_score

def check_loan_approval(customer, credit_score, interest_rate):
    sum_current_loans = customer.loan_set.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
    sum_current_emis = customer.loan_set.aggregate(Sum('monthly_repayment'))['monthly_repayment__sum'] or 0
    monthly_salary = customer.monthly_salary
    
    if sum_current_loans > customer.approved_limit or sum_current_emis > (0.5 * monthly_salary):
        return False, 0  # Loan not approved
    
    if credit_score > 50:
        return True, interest_rate
    elif 50 >= credit_score > 30:
        if interest_rate <= 12:
            return False, 12
        else:
            return True, interest_rate
    elif 30 >= credit_score > 10:
        if interest_rate <= 16:
            return False, 16
        else:
            return True, interest_rate
    else:
        return False, 0  # Loan not approved

def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    interest_rate_percentage = interest_rate / 100
    monthly_interest_rate = interest_rate_percentage / 12
    numerator = loan_amount * monthly_interest_rate * ((1 + monthly_interest_rate) ** tenure)
    denominator = ((1 + monthly_interest_rate) ** tenure) - 1
    monthly_installment = numerator / denominator
    
    return monthly_installment



@csrf_exempt
def create_loan(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        loan_amount = float(request.POST.get('loan_amount'))
        interest_rate = float(request.POST.get('interest_rate'))
        tenure = int(request.POST.get('tenure'))
        
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer does not exist'}, status=400)
        
        loan_approved, loan_id, monthly_installment, message = process_loan(customer, loan_amount, interest_rate, tenure)
        
        response_data = {
            'loan_id': loan_id,
            'customer_id': customer_id,
            'loan_approved': loan_approved,
            'message': message,
            'monthly_installment': monthly_installment
        }
        
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)

def process_loan(customer, loan_amount, interest_rate, tenure):
    # Check customer eligibility (you can implement this based on your previous logic)
    # For example:
    credit_score = calculate_credit_score(customer)
    loan_approval, corrected_interest_rate = check_loan_approval(customer, credit_score, interest_rate)
    monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
    
    if loan_approval: 
        # Create a new Loan object
        loan = Loan.objects.create(
            customer_id=customer.customer_id,
            loan_amount=loan_amount,
            interest_rate=corrected_interest_rate,
            tenure=tenure,
            monthly_repayment=monthly_installment,
            emis_paid_on_time=0,  # Assuming this starts at 0
            start_date=datetime.date.today(),  # Use today's date as the start date
            end_date=datetime.date.today() + relativedelta(months=tenure)  # Calculate end date based on tenure
        )
        return True, loan.loan_id, monthly_installment, "Loan approved"
    else:
        return False, None, 0, "Loan not approved"


def calculate_credit_score(customer):
    past_loans_paid_on_time = customer.loan_set.filter(emis_paid_on_time=True).count()
    total_loans_taken = customer.loan_set.count()
    loan_activity_current_year = customer.loan_set.filter(start_date__year=2024).count()
    approved_limit = customer.approved_limit
    
    credit_score = 0
    if past_loans_paid_on_time > 5:
        credit_score += 20
    if total_loans_taken <= 3:
        credit_score += 10
    if loan_activity_current_year > 0:
        credit_score += 15
    if approved_limit >= 500000:
        credit_score += 20
    
    return credit_score

def check_loan_approval(customer, credit_score, interest_rate):
    sum_current_loans = customer.loan_set.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
    sum_current_emis = customer.loan_set.aggregate(Sum('monthly_repayment'))['monthly_repayment__sum'] or 0
    monthly_salary = customer.monthly_salary
    
    if sum_current_loans > customer.approved_limit or sum_current_emis > (0.5 * monthly_salary):
        return False, 0  # Loan not approved
    
    if credit_score > 50:
        return True, interest_rate
    elif 50 >= credit_score > 30:
        if interest_rate <= 12:
            return False, 12
        else:
            return True, interest_rate
    elif 30 >= credit_score > 10:
        if interest_rate <= 16:
            return False, 16
        else:
            return True, interest_rate
    else:
        return False, 0  # Loan not approved

def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    interest_rate_percentage = interest_rate / 100
    monthly_interest_rate = interest_rate_percentage / 12
    numerator = loan_amount * monthly_interest_rate * ((1 + monthly_interest_rate) ** tenure)
    denominator = ((1 + monthly_interest_rate) ** tenure) - 1
    monthly_installment = numerator / denominator
    
    return monthly_installment



# /view-loan/loan_id api endpoint
def view_loan_details(request, loan_id):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
    except Loan.DoesNotExist:
        return JsonResponse({'error': 'Loan does not exist'}, status=404)
    
    customer = loan.customer
    customer_details = {
        'customer_id': customer.customer_id,
        'first_name': customer.first_name,
        'last_name': customer.last_name,
        'phone_number': customer.phone_number,
        'age': customer.age
    }
    
    loan_details = {
        'loan_id': loan.loan_id,
        'customer': customer_details,
        'loan_approved': True, 
        'loan_amount': loan.loan_amount,
        'interest_rate': loan.interest_rate,
        'monthly_installment': loan.monthly_repayment,
        'tenure': loan.tenure
    }
    
    return JsonResponse(loan_details)



# /view-loans/customer_id api endpoint
def view_customer_loans(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Customer does not exist'}, status=404)
    
    loans = Loan.objects.filter(customer=customer)
    
    loan_details = []
    for loan in loans:
        loan_detail = {
            'loan_id': loan.loan_id,
            'loan_approved': True,  # Assuming loan is already approved if it exists
            'loan_amount': loan.loan_amount,
            'interest_rate': loan.interest_rate,
            'monthly_installment': loan.monthly_repayment,
            'repayments_left': loan.tenure - loan.emis_paid_on_time  # Assuming EMIs are paid on time
        }
        loan_details.append(loan_detail)
    
    return JsonResponse(loan_details, safe=False)