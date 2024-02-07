from .models import Customer, Loan
import pandas as pd

customer_data = pd.read_excel('./customer_data.xlsx')
loan_data = pd.read_excel('./loan_data.xlsx')

# Get Customer data from excel and insert into our aap Customer model
for index, row in customer_data.iterrows():
    customer = Customer(
        customer_id=row['customer_id'],
        first_name=row['first_name'],
        last_name=row['last_name'],
        age=row['age'],
        phone_number=row['phone_number'],
        monthly_salary=row['monthly_salary'],
        approved_limit=row['approved_limit'] 
    )
    customer.save()

# Get Loan data from excel and insert into our aap Loan model
    
for index, row in loan_data.iterrows():
    loan = Loan(
        customer_id=row['customer_id'],
        loan_id=row['loan_id'],
        loan_amount=row['loan_amount'],
        tenure=row['tenure'],
        interest_rate=row['interest_rate'],
        monthly_repayment=row['monthly_repayment'],
        emis_paid_on_time=row['emis_paid_on_time'],
        start_date=row['start_date'],
        end_date=row['end_date']
    )
    loan.save()

# print(customer_data.head())  
# print(loan_data.head())  
