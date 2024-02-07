from django.contrib import admin
from .models import Customer, Loan
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

# Register your models here.

class CustomerResource(resources.ModelResource):
    customer_id = fields.Field(attribute='customer_id', column_name='customer_id')
    first_name = fields.Field(attribute='first_name', column_name='first_name')
    last_name = fields.Field(attribute='last_name', column_name='last_name')
    age = fields.Field(attribute='age', column_name='age')
    phone_number = fields.Field(attribute='phone_number', column_name='phone_number')
    monthly_salary = fields.Field(attribute='monthly_salary', column_name='monthly_salary')
    approved_limit = fields.Field(attribute='approved_limit', column_name='approved_limit')

    class Meta:
        model = Customer
        import_id_fields = ['customer_id']
        fields = ('customer_id', 'first_name', 'last_name', 'age', 'phone_number', 'monthly_salary', 'approved_limit')

    def before_import_row(self, row, **kwargs):
        row['customer_id'] = row.get('customer_id', None)

class CustomerAdmin(ImportExportModelAdmin):
    resource_class = CustomerResource

admin.site.register(Customer, CustomerAdmin)

class LoanResource(resources.ModelResource):
    customer_id = fields.Field(attribute='customer_id', column_name='customer_id', widget=ForeignKeyWidget(Customer, 'customer_id'))
    loan_id = fields.Field(attribute='loan_id', column_name='loan_id')
    loan_amount = fields.Field(attribute='loan_amount', column_name='loan_amount')
    tenure = fields.Field(attribute='tenure', column_name='tenure')
    interest_rate = fields.Field(attribute='interest_rate', column_name='interest_rate')
    monthly_repayment = fields.Field(attribute='monthly_repayment', column_name='monthly_repayment')
    emis_paid_on_time = fields.Field(attribute='emis_paid_on_time', column_name='emis_paid_on_time')
    start_date = fields.Field(attribute='start_date', column_name='start_date')
    end_date = fields.Field(attribute='end_date', column_name='end_date')

    class Meta:
        model = Loan
        import_id_fields = ['loan_id']
        fields = ('loan_id', 'customer_id', 'loan_amount', 'tenure', 'interest_rate', 'monthly_repayment', 'emis_paid_on_time', 'start_date', 'end_date')

class LoanAdmin(ImportExportModelAdmin):
    resource_class = LoanResource
    list_display = ['loan_id', 'customer_id', 'loan_amount', 'tenure', 'interest_rate', 'monthly_repayment', 'emis_paid_on_time', 'start_date', 'end_date']

admin.site.register(Loan, LoanAdmin)
