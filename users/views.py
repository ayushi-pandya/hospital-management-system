import io
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Min, Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View, generic
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, TemplateView
from xhtml2pdf import pisa

from appointment.models import Admit, AdmitStaff, Appointments
from constants import PRESCRIPTION_SUCCESS_MSG, REGISTER_SUCCESS_MSG, ROLE_SUCCESS_MSG, SPECIALITY_SUCCESS_MSG, \
    PROFILE_UPDATE_MSG, PROFILE_DELETE_MSG, UPDATE_STAFF_PROFILE, NURSE_ERROR_MSG, FEEDBACK_SUCCESS_MSG, \
    PRESCRIPTION_UPDATE_MSG, EMERGENCY_SUCCESS_MSG, MEDICINE_SUCCESS_MSG, MEDICINE_UPDATE_MSG, BILL_SUCCESS_MSG
from . import models
from .forms import UserRegisterForm, UserUpdateForm, PatientRegistrationForm, StaffUpdateForm, FeedbackForm, \
    PrescriptionForm, PrescriptionUpdateForm, CreateBillForm, MedicineUpdateForm, MedicineForm, EmergencyForm, \
    AddRoleForm, AddSpecialityForm

from .models import CustomUser, Patient, Staff, Feedback, Prescription, Emergency, Bill, Medicine, PrescribeMedicine, \
    UserRole, StaffSpeciality


def is_admin(user):
    return CustomUser.objects.filter(username=user).filter(is_superuser=True)


def is_doctor(user):
    return CustomUser.objects.filter(username=user).filter(role=1)


def is_nurse(user):
    return CustomUser.objects.filter(username=user).filter(role=3)


class Register(SuccessMessageMixin, CreateView):
    """
    This class is for user registration.
    """
    form_class = UserRegisterForm
    patient_form_class = PatientRegistrationForm
    template_name = 'users/register.html'

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user_obj = form.save(commit=True)
            if user_obj.role == 'P':
                patient = Patient.objects.create(patient=user_obj)
                patient.save()
                messages.success(request, REGISTER_SUCCESS_MSG)
            if user_obj.role == 'D' or user_obj.role == 'N':
                staff = Staff.objects.create(staff=user_obj)
                staff.save()
                messages.success(request, REGISTER_SUCCESS_MSG)
            if request.user.is_superuser:
                return redirect('Hospital-home')
            return redirect('login')
        else:
            return render(request, 'users/register.html', {'form': form})


class AddRole(CreateView, SuccessMessageMixin):
    """
    class for adding data in role table
    """
    print('its in')
    form_class = AddRoleForm
    template_name = 'users/add_role.html'
    success_url = reverse_lazy('Hospital-home')
    success_message = ROLE_SUCCESS_MSG

    def dispatch(self, request, *args, **kwargs):
        if is_admin(user=self.request.user):
            return super(AddRole, self).dispatch(
                request, *args, **kwargs)
        return render(request, 'appointment/not_admin.html')


class AddSpeciality(CreateView, SuccessMessageMixin):
    """
    class for adding data in speciality table
    """
    form_class = AddSpecialityForm
    template_name = 'users/add_speciality.html'

    def dispatch(self, request, *args, **kwargs):
        if is_admin(user=self.request.user):
            return super(AddSpeciality, self).dispatch(
                request, *args, **kwargs)
        return render(request, 'appointment/not_admin.html')

    def get_success_url(self):
        messages.success(self.request, SPECIALITY_SUCCESS_MSG)
        return reverse("Hospital-home")


class UpdateProfile(SuccessMessageMixin, UpdateView):
    """
    This class is for update the profile information.
    """
    form_class = UserUpdateForm
    template_name = 'users/profile.html'
    success_message = PROFILE_UPDATE_MSG

    def get_queryset(self):
        query_set = CustomUser.objects.filter(id=self.kwargs['pk'])
        return query_set

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse("update-profile", kwargs={"pk": pk})


class DeleteProfile(SuccessMessageMixin, DeleteView):
    """
    This class is for delete the user profile.
    """
    model = CustomUser
    success_message = PROFILE_DELETE_MSG
    success_url = "/"

    def test_func(self):
        profile = self.get_object()
        if self.request.user == profile.username:
            return True
        return False


class SearchUser(View):
    """
    class for give data to ajax call for search user
    """

    def get(self, request):
        user = CustomUser.objects.all().values_list('username', flat=True)
        user_list = list(user)
        return JsonResponse(user_list, safe=False)


class ViewUser(View):
    """
    class for view the list of customuser
    """

    def get(self, request):
        all_data = CustomUser.objects.all()
        all_role = UserRole.objects.values_list('role', flat=True)
        context = {
            'all_data': all_data,
            'all_role': all_role
        }
        return render(request, 'users/view_user.html', context)

    def post(self, request):
        search = request.POST['search']
        query_filter = request.POST['name']
        if search != "":
            search = search.strip()
            all_role = UserRole.objects.values_list('role', flat=True)
            user = CustomUser.objects.filter(username__icontains=search)
            return render(request, 'users/view_user.html', {'data': user, 'all_role': all_role})
        elif query_filter != "":
            all_role = UserRole.objects.values_list('role', flat=True)
            if query_filter == 'All':
                user = Staff.objects.all()
            else:
                query = query_filter.strip()
                user = CustomUser.objects.filter(role__role=query)
            return render(request, 'users/view_user.html', {'data': user, 'all_role': all_role})
        else:
            return redirect('Hospital-home')

    def dispatch(self, request, *args, **kwargs):
        if is_admin(user=self.request.user):
            return super(ViewUser, self).dispatch(
                request, *args, **kwargs)
        return render(request, 'appointment/not_admin.html')


class SearchStaff(View):
    """
    class for give data to ajax call for search user
    """

    def get(self, request):
        user = Staff.objects.all().values_list('staff__username', flat=True)
        user_list = list(user)
        return JsonResponse(user_list, safe=False)


class ViewStaff(View):
    """
    class for view the list of customuser
    """

    def get(self, request):
        all_data = Staff.objects.all()
        all_speciality = StaffSpeciality.objects.values_list('speciality', flat=True)
        context = {
            'all_data': all_data,
            'all_speciality': all_speciality
        }
        return render(request, 'users/view_staff.html', context)

    def post(self, request):
        search = request.POST['search']
        query_filter = request.POST['name']
        if search != "":
            search = search.strip()
            staff = Staff.objects.filter(staff__username__icontains=search)
            all_speciality = StaffSpeciality.objects.values_list('speciality', flat=True)
            return render(request, 'users/view_staff.html', {'data': staff, 'all_speciality': all_speciality})
        elif query_filter != "":
            all_speciality = StaffSpeciality.objects.values_list('speciality', flat=True)
            if query_filter == 'All':
                user = Staff.objects.all()
            else:
                query = query_filter.strip()
                user = Staff.objects.filter(speciality__speciality=query)
            return render(request, 'users/view_staff.html', {'data': user, 'all_speciality': all_speciality})
        else:
            return redirect('Hospital-home')

    def dispatch(self, request, *args, **kwargs):
        if is_admin(user=self.request.user):
            return super(ViewStaff, self).dispatch(
                request, *args, **kwargs)
        return render(request, 'appointment/not_admin.html')


class UpdateStaffProfile(SuccessMessageMixin, UpdateView):
    """
    This class is for update the profile information of staff.
    """
    form_class = StaffUpdateForm
    template_name = 'users/staff_update.html'
    success_message = UPDATE_STAFF_PROFILE

    def get_queryset(self, *args, **kwargs):
        query_set = Staff.objects.filter(id=self.kwargs['pk'])
        # query = get_object_or_404(Staff, id=self.kwargs.get('pk'))
        return query_set

    def form_valid(self, form, *args, **kwargs):
        data = self.request.POST
        fetch_speciality = data.get('speciality')
        fetch_pk = get_object_or_404(Staff, id=self.kwargs.get('pk'))
        query = CustomUser.objects.filter(username=fetch_pk).values_list('role', flat=True)
        if query[0] == 'N' and fetch_speciality != 'Nurse':
            messages.error(self.request, NURSE_ERROR_MSG)
            return self.form_invalid(form)
        else:
            return super().form_valid(form)

    def get_success_url(self):
        return reverse("view-staff")


class EnterFeedback(CreateView, SuccessMessageMixin):
    form_class = FeedbackForm
    template_name = 'users/feedback.html'

    def get_queryset(self):
        query_set = CustomUser.objects.filter(id=self.kwargs['pk'])
        return query_set

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(EnterFeedback, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, FEEDBACK_SUCCESS_MSG)
        return reverse("Hospital-home")


class SearchFeedback(View):
    """
    class for give data to ajax call for search medicine
    """

    def get(self, request):
        user = Feedback.objects.all().values_list('user__username', flat=True)
        user_list = list(user)
        print(user_list)
        return JsonResponse(user_list, safe=False)


class ViewFeedback(View):
    """
    class for view the list of feedback
    """

    def get(self, request):
        all_data = Feedback.objects.all()
        context = {
            'all_data': all_data
        }
        return render(request, 'users/view_feedback.html', context)

    def post(self, request):
        search = request.POST['search']
        if search != " ":
            search = search.strip()
            staff = Feedback.objects.filter(user__username__icontains=search)
            return render(request, 'users/view_feedback.html', {'data': staff})
        else:
            return redirect('Hospital-home')

    def dispatch(self, request, *args, **kwargs):
        if is_admin(user=self.request.user):
            return super(ViewFeedback, self).dispatch(
                request, *args, **kwargs)
        return render(request, 'appointment/not_admin.html')


class PatientPrescription(View, SuccessMessageMixin):
    form_class = PrescriptionForm
    template_name = 'users/prescription.html'

    def get(self, request):
        form = PrescriptionForm()
        medicines = [meds.medicine_name for meds in Medicine.objects.all()]
        context = {'form': form, "medicines": medicines}
        return render(request, 'users/prescription.html', context)

    def post(self, request, *args, **kwargs):
        bill_form = PrescriptionForm(request.POST)
        print(bill_form.errors)
        if bill_form.is_valid():
            data = {}
            for p in request.POST:
                data[p] = request.POST[p]
            print('data', data)
            b = {k: v[0] if len(v) == 1 else v for k, v in request.POST.lists()}
            print('b:', b)
            fetch_patient = request.POST.get('patient')
            fetch_medicine = request.POST.getlist('medicine')
            print('fetch_medicine:', fetch_medicine)
            fetch_count = request.POST.getlist('count')
            print('fetch_count:', fetch_count)
            patient = Patient.objects.filter(id=fetch_patient).first()
            bill_form.patient = patient
            bill = bill_form.save(commit=False)
            bill.save()
            id_query = Prescription.objects.latest('id')
            print('id_query', id_query)
            objs = []
            if len(fetch_medicine) > 1:
                for i in range(len(fetch_medicine)):
                    count = fetch_count[i]
                    m = Medicine.objects.filter(medicine_name=fetch_medicine[i]).first()
                    objs.append(PrescribeMedicine(prescription=id_query, medicine=m, count=count))
                    print('m:', m.id)
                PrescribeMedicine.objects.bulk_create(objs)
            else:
                m = Medicine.objects.filter(medicine_name=fetch_medicine[0]).first()
                prescribe = PrescribeMedicine.objects.create(prescription=id_query, medicine=m, count=fetch_count)
                prescribe.save()
            messages.success(request, PRESCRIPTION_SUCCESS_MSG)
            return redirect('Hospital-home')


class PrescriptionUpdate(SuccessMessageMixin, UpdateView):
    """
    This class is for update the profile information.
    """
    form_class = PrescriptionUpdateForm
    template_name = 'users/prescription_update.html'
    success_message = PRESCRIPTION_UPDATE_MSG

    def get_queryset(self):
        query_set = Prescription.objects.filter(id=self.kwargs['pk'])
        return query_set

    def get_success_url(self):
        return reverse('view-prescription')


class ViewPrescription(ListView):
    """
    class for view the list of prescription
    """
    model = Prescription
    template_name = 'users/view_prescription.html'
    context_object_name = 'prescription'

    def get_queryset(self):
        return self.model.objects.all().order_by('id')

    def dispatch(self, request, *args, **kwargs):
        if is_doctor(user=self.request.user):
            return super(ViewPrescription, self).dispatch(
                request, *args, **kwargs)
        return render(request, 'appointment/not_doc.html')


class EmergencyCase(CreateView, SuccessMessageMixin):
    """
    class used for adding emergency case
    """
    form_class = EmergencyForm
    template_name = 'users/emergency.html'

    def dispatch(self, request, *args, **kwargs):
        if is_admin(user=self.request.user):
            return super(EmergencyCase, self).dispatch(
                request, *args, **kwargs)
        return render(request, 'appointment/not_admin.html')

    def get_success_url(self):
        messages.success(self.request, EMERGENCY_SUCCESS_MSG)
        return reverse("Hospital-home")


class SearchEmergency(View):
    """
    class for give data to ajax call for search user
    """

    def get(self, request):
        user = Emergency.objects.all().values_list('patient__patient__username', flat=True)
        user_list = list(user)
        return JsonResponse(user_list, safe=False)


class ViewEmergency(View):
    """
    class for view the list of emergency cases
    """

    def get(self, request):
        all_data = Emergency.objects.all()
        context = {
            'all_data': all_data
        }
        return render(request, 'users/view_emergency.html', context)

    def post(self, request):
        search = request.POST['search']
        if search != " ":
            search = search.strip()
            staff = Emergency.objects.filter(patient__patient__username__icontains=search)
            return render(request, 'users/view_emergency.html', {'data': staff})
        else:
            return redirect('Hospital-home')

    def dispatch(self, request, *args, **kwargs):
        if is_admin(user=self.request.user):
            return super(ViewEmergency, self).dispatch(
                request, *args, **kwargs)
        return render(request, 'appointment/not_admin.html')


class AddMedicine(CreateView, SuccessMessageMixin):
    """
    class for adding medicines
    """
    form_class = MedicineForm
    template_name = 'users/add_medicine.html'

    def dispatch(self, request, *args, **kwargs):
        if is_doctor(user=self.request.user):
            return super(AddMedicine, self).dispatch(
                request, *args, **kwargs)
        return render(request, 'appointment/not_doc.html')

    def get_success_url(self):
        messages.success(self.request, MEDICINE_SUCCESS_MSG)
        return reverse("Hospital-home")


class SearchMedicine(View):
    """
    class for give data to ajax call for search medicine
    """

    def get(self, request):
        minPrice = request.GET['minPrice']
        maxPrice = request.GET['maxPrice']
        allProducts = Medicine.objects.all().order_by('-id').distinct()
        allProducts = allProducts.filter(medicineattribute__charge_gte=minPrice)
        allProducts = allProducts.filter(medicineattribute__charge_lte=maxPrice)
        topics = Medicine.objects.all().values_list('medicine_name', flat=True)
        medicine_list = list(topics)
        return JsonResponse(medicine_list, allProducts, safe=False)


class ViewMedicine(View):
    """
    class for view list of medicines
    """

    def get(self, request):
        all_data = Medicine.objects.all()
        user = CustomUser.objects.filter(id=self.request.user.id).first()
        minMaxPrice = Medicine.objects.aggregate(Min('charge'), Max('charge'))
        context = {
            'all_data': all_data,
            'user': user,
            'minMaxPrice': minMaxPrice
        }
        return render(request, 'users/view_medicine.html', context)

    def post(self, request):
        search = request.POST['search']
        if search != " ":
            search = search.strip()
            user = CustomUser.objects.filter(id=self.request.user.id).first()
            medicine = Medicine.objects.filter(medicine_name__icontains=search)
            return render(request, 'users/view_medicine.html', {'data': medicine, 'user': user})
        else:
            return redirect('Hospital-home')


class MedicineUpdate(SuccessMessageMixin, UpdateView):
    """
    This class is for update the medicine information.
    """
    form_class = MedicineUpdateForm
    template_name = 'users/medicine_update.html'
    success_message = MEDICINE_UPDATE_MSG

    def get_queryset(self):
        query_set = Medicine.objects.filter(id=self.kwargs['pk'])
        return query_set

    def get_success_url(self):
        return reverse('view-medicine')

    def dispatch(self, request, *args, **kwargs):
        if is_doctor(user=self.request.user):
            return super(MedicineUpdate, self).dispatch(
                request, *args, **kwargs)
        return render(request, 'appointment/not_doc.html')


class CreateBill(View, SuccessMessageMixin):
    """
    class for creating bill
    """
    form_class = CreateBillForm
    template_name = 'users/create_bill.html'

    def get(self, request):
        form = CreateBillForm()
        context = {'form': form}
        return render(request, 'users/create_bill.html', context)

    def post(self, request, *args, **kwargs):
        print("Start")
        bill_form = CreateBillForm(request.POST)
        print("before form")
        print(bill_form.errors)
        if bill_form.is_valid():
            print("its valid !!")
            fetch_patient = request.POST.get('patient')
            fetch_staff_charge = request.POST.get('staff_charge')
            fetch_other_charge = request.POST.get('other_charge')
            patient = Patient.objects.filter(id=fetch_patient).first()
            print("1: ", fetch_staff_charge)
            print("2: ", fetch_other_charge)
            bill_form.patient = patient
            bill = bill_form.save(commit=False)
            fetch_medicine = Prescription.objects.filter(patient=fetch_patient).first()
            admit_obj = Admit.objects.filter(patient=fetch_patient)
            emergency_obj = Emergency.objects.filter(patient=fetch_patient)
            total = 0
            medicine_charge = 0
            emergency_charge = 0
            for admit in admit_obj:
                total += admit.room.charge
                bill.room_charge = admit.room.charge
            for emergency in emergency_obj:
                total += emergency.charge
                print('emergency :', emergency.charge)
                bill.emergency_charge = emergency.charge
            if fetch_medicine:
                print('in medicine')
                print('medicine:', fetch_medicine.medicine)
                charge = Medicine.objects.filter(medicine_name=fetch_medicine.medicine).first()
                print(charge)
                print('charge:', charge.charge)
                print('dose:', fetch_medicine.count)
                medicine_charge = charge.charge * fetch_medicine.count
                print(medicine_charge)
                bill.medicine_charge = medicine_charge

            total += Decimal(fetch_staff_charge) + Decimal(fetch_other_charge) + Decimal(medicine_charge) + Decimal(
                emergency_charge)
            bill.total_charge = total
            bill.save()
            messages.success(request, BILL_SUCCESS_MSG)
            return redirect('Hospital-home')

        else:
            return render(request, self.template_name, {'form': bill_form})


class BillDetailView(generic.DetailView):
    model = Bill

    def get_context_data(self, **kwargs):
        context = super(BillDetailView, self).get_context_data(**kwargs)
        fetch_bill = Bill.objects.get(id=self.object.id)
        print('fetch_bill', fetch_bill.id)
        fetch_admit = Admit.objects.filter(patient=fetch_bill.patient_id).first()
        fetch_emergency = Emergency.objects.filter(patient=fetch_bill.patient_id).first()
        print('fetch_emergency', fetch_emergency)
        if fetch_emergency:
            # print(fetch_emergency.staff)
            context['emergency_staff'] = fetch_emergency.staff
        if fetch_admit:
            # print('its in!!!')
            fetch_staff = AdmitStaff.objects.get(id=fetch_admit.pk)
            # print(fetch_staff.staff, '......')
            # print(fetch_bill.patient_id, '123456789')
            # print(fetch_admit.pk, '[[[[[[[[[[[[[[[[[[[[[[[[[')
            context['patient'] = fetch_admit.patient
            context['staff'] = fetch_staff.staff
            context['disease'] = fetch_admit.disease
            print(context['patient'])
        print(context)
        context['bill_id'] = fetch_bill.id
        return context


class BillView(ListView):
    """
    class for displaying generated bills
    """
    model = Bill
    template_name = 'users/view_bill.html'
    context_object_name = 'bill'

    def get_queryset(self):
        return Bill.objects.order_by('id')

    def get_context_data(self, **kwargs):
        context = super(BillView, self).get_context_data(**kwargs)
        context['bill_list'] = Bill.objects.order_by('id')
        return context


class ViewTodayAppointment(ListView):
    """
    class for displaying today's appointment for doctor
    """
    model = Appointments
    template_name = 'users/view_todays_appointment.html'
    context_object_name = 'appointment'

    def get_queryset(self):
        date = datetime.now().date()
        return Appointments.objects.filter(staff__staff__username=self.request.user).filter(date=date).order_by('id')


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return


class DownloadPdfView(View):
    def get(self, request, pk):
        bill_details = models.Bill.objects.filter(patient=pk).order_by('-id')[:1]
        patient_details = models.CustomUser.objects.filter(patient=pk).order_by('-id')[:1]
        dict = {
            'id': bill_details[0].id,
            'patientName': bill_details[0].patient.patient.username,
            'address': patient_details[0].address,
            'mobile': patient_details[0].phone,
            'medicineCost': bill_details[0].medicine_charge,
            'roomCharge': bill_details[0].room_charge,
            'doctorFee': bill_details[0].staff_charge,
            'OtherCharge': bill_details[0].other_charge,
            'total': bill_details[0].total_charge,
        }
        return render_to_pdf('users/download_bill.html', dict)


class ViewBill(ListView):
    model = Bill
    template_name = 'users/view_bill.html'
    context_object_name = 'bill'

    def get_queryset(self):
        print(self.request.user)
        query_set = Bill.objects.filter(patient__patient__username=self.request.user)
        return query_set
