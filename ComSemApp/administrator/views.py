from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse_lazy

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView, DeleteView
from django.views import View

from django.core.mail import send_mail
from django.contrib import messages


from ComSemApp.models import *
from django.contrib.auth.models import User
from ComSemApp.administrator.forms import CourseForm, CourseTypeForm, SessionForm, SessionTypeForm, TeacherForm, StudentForm, UserForm
from ComSemApp.libs.mixins import RoleViewMixin


class AdminViewMixin(RoleViewMixin):

    role_class = Admin

    def _set_role_obj(self):
        # role_obj self in RoleViewMixin
        self.admin = self.role_obj


class InstanceCreateUpdateMixin(AdminViewMixin):
    # initializes the necessary form, passing the current institution
    # necessary in situations like the Course form which offers course type options specific to an institution
    def get_form_kwargs(self):
        kwargs = super(InstanceCreateUpdateMixin, self).get_form_kwargs()
        kwargs['institution'] = self.institution
        return kwargs


### LIST

class TeacherListView(AdminViewMixin, ListView):
    model = Teacher
    template_name = 'ComSemApp/admin/teacher_list.html'

    def get_queryset(self):
        return Teacher.objects.filter(institution=self.institution)


class StudentListView(AdminViewMixin, ListView):
    model = Student
    template_name = 'ComSemApp/admin/student_list.html'

    def get_queryset(self):
        return Student.objects.filter(institution=self.institution)


class CourseListView(AdminViewMixin, ListView):
    model = Course
    template_name = 'ComSemApp/admin/course_list.html'

    def get_queryset(self):
        course_types = CourseType.objects.filter(institution=self.institution)
        return Course.objects.filter(course_type__in=course_types)


class CourseTypeListView(AdminViewMixin, ListView):
    model = CourseType
    template_name = 'ComSemApp/admin/course_type_list.html'

    def get_queryset(self):
        return CourseType.objects.filter(institution=self.institution)


class SessionListView(AdminViewMixin, ListView):
    model = Session
    template_name = 'ComSemApp/admin/session_list.html'

    def get_queryset(self):
        session_types = SessionType.objects.filter(institution=self.institution)
        return Session.objects.filter(session_type__in=session_types)


class SessionTypeListView(AdminViewMixin, ListView):
    model = SessionType
    template_name = 'ComSemApp/admin/session_type_list.html'

    def get_queryset(self):
        return SessionType.objects.filter(institution=self.institution)


### CREATE

class UserMixin(AdminViewMixin, FormView):
    # This mixin is used to create and update teachers and students.
    # A mixin is needed because the teacher and student views combine two forms, the django user form and the form
    # for a student / teacher object.
    template_name = 'ComSemApp/standard_form.html'

    def form_invalid(self, user_form, obj_form, **kwargs):
        user_form.prefix = 'user_form'
        obj_form.prefix = 'obj_form'
        return self.render_to_response(self.get_context_data(form=user_form, obj_form=obj_form))

    def _send_email(self, user, password):
        link = "https://www.comsem.net"
        message = ("You have been invited to join Communication Seminar by an administrator for " + self.institution.name + ".\n"
                    "In order to log in, go to " + link + " and use \n"
                    "\tusername: " + user.username + "\n\tpassword: " + password + "\n"
                    "from there you can change your password.")

        send_mail(
            'Invitation to Communication Seminar',
            message,
            'signup@comsem.net',
            [user.email],
            fail_silently=False,
        )


class UserCreateMixin(UserMixin):

    def get(self, request, *args, **kwargs):
        user_form = UserForm()
        user_form.prefix = 'user_form'
        obj_form = self.get_obj_form()
        obj_form.prefix = 'obj_form'
        return self.render_to_response(self.get_context_data(form=user_form, obj_form=obj_form))

    def post(self, request, *args, **kwargs):
        user_form = UserForm(self.request.POST, prefix='user_form')
        obj_form = self.get_obj_form()

        if user_form.is_valid() and obj_form.is_valid():
            # create the user object with random password
            user = user_form.save()
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()

            # create the student / teacher
            self.save_obj(obj_form, user)

            super(UserCreateMixin, self)._send_email(user, password)
            return HttpResponseRedirect(self.success_url)
        else:
            return self.form_invalid(user_form, obj_form, **kwargs)


class TeacherCreateView(UserCreateMixin):
    success_url = reverse_lazy("administrator:teachers")

    def get_obj_form(self):
        return TeacherForm(self.request.POST, prefix='obj_form')

    def save_obj(self, obj_form, user):
        obj = obj_form.save(commit=False)
        obj.user = user
        obj_form.save()
        obj.institution.add(self.institution)


class StudentCreateView(UserCreateMixin):
    success_url = reverse_lazy("administrator:students")

    def get_obj_form(self):
        return StudentForm(self.request.POST, prefix='obj_form')

    def save_obj(self, obj_form, user):
        obj = obj_form.save(commit=False)
        obj.user = user
        obj.institution = self.institution
        obj_form.save()


class TypeCreateMixin(AdminViewMixin, CreateView):

    def form_valid(self, form):
        form.instance.institution = self.institution
        return super(TypeCreateMixin,self).form_valid(form)


class CourseTypeCreateView(TypeCreateMixin):
    success_url = reverse_lazy("administrator:course_types")
    template_name = 'ComSemApp/standard_form.html'
    form_class = CourseTypeForm


class SessionTypeCreateView(TypeCreateMixin):
    success_url = reverse_lazy("administrator:session_types")
    template_name = 'ComSemApp/standard_form.html'
    form_class = SessionTypeForm


class CourseCreateView(InstanceCreateUpdateMixin, CreateView):
    success_url = reverse_lazy("administrator:courses")
    template_name = 'ComSemApp/standard_form.html'
    form_class = CourseForm


class SessionCreateView(InstanceCreateUpdateMixin, CreateView):
    success_url = reverse_lazy("administrator:sessions")
    template_name = 'ComSemApp/standard_form.html'
    form_class = SessionForm


### UPDATE


class UserUpdateMixin(UserMixin):

    def get(self, request, *args, **kwargs):
        obj_form = self.get_obj_form()
        obj_form.prefix = 'obj_form'
        user_form = UserForm(instance=self.instance.user)
        user_form.prefix = 'user_form'
        return self.render_to_response(self.get_context_data(form=user_form, obj_form=obj_form))

    def post(self, request, *args, **kwargs):
        user_form = UserForm(self.request.POST, instance=self.instance.user, prefix='user_form')
        obj_form = self.get_obj_form(initial=self.request.POST)

        if user_form.is_valid() and obj_form.is_valid():
            user = user_form.save()
            obj_form.save()

            # to do ! what should we send in an email ?
            # super(UserUpdateMixin, self)._send_email(user, password)
            return HttpResponseRedirect(self.success_url)
        else:
            return self.form_invalid(user_form, obj_form, **kwargs)


class TeacherUpdateView(UserUpdateMixin):
    success_url = reverse_lazy("administrator:teachers")

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Teacher, pk=kwargs['pk'])
        return super(TeacherUpdateView, self).dispatch(request, args, kwargs)

    def get_obj_form(self, initial=None):
        return TeacherForm(initial, instance=self.instance, prefix='obj_form')


class StudentUpdateView(UserUpdateMixin):
    success_url = reverse_lazy("administrator:students")

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Student, pk=kwargs['pk'])
        return super(StudentUpdateView, self).dispatch(request, args, kwargs)

    def get_obj_form(self, initial=None):
        return StudentForm(initial, instance=self.instance, prefix='obj_form')


class CourseTypeUpdateView(AdminViewMixin, UpdateView):
    success_url = reverse_lazy("administrator:course_types")
    model = CourseType
    form_class = CourseTypeForm
    template_name = 'ComSemApp/standard_form.html'


class SessionTypeUpdateView(AdminViewMixin, UpdateView):
    success_url = reverse_lazy("administrator:session_types")
    model = SessionType
    form_class = SessionTypeForm
    template_name = 'ComSemApp/standard_form.html'


class CourseUpdateView(InstanceCreateUpdateMixin, UpdateView):
    success_url = reverse_lazy("administrator:courses")
    model = Course
    form_class = CourseForm
    template_name = 'ComSemApp/standard_form.html'


class SessionUpdateView(InstanceCreateUpdateMixin, UpdateView):
    success_url = reverse_lazy("administrator:sessions")
    model = Session
    form_class = SessionForm
    template_name = 'ComSemApp/standard_form.html'


### DELETE

class NoConfirmDeleteMixin(DeleteView):

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class DisactivateUserMixin(NoConfirmDeleteMixin):

    def post(self, request, *args, **kwargs):
        user = self.get_object().user
        user.is_active = False
        user.save()
        return  HttpResponseRedirect(self.success_url)


class TeacherDisactivateView(DisactivateUserMixin):
    success_url = reverse_lazy("administrator:teachers")
    model = Teacher


class StudentDisactivateView(DisactivateUserMixin):
    success_url = reverse_lazy("administrator:students")
    model = Student


class CourseTypeDeleteView(NoConfirmDeleteMixin):
    success_url = reverse_lazy("administrator:course_types")
    model = CourseType


class SessionTypeDeleteView(NoConfirmDeleteMixin):
    success_url = reverse_lazy("administrator:session_types")
    model = SessionType


class CourseDeleteView(NoConfirmDeleteMixin):
    success_url = reverse_lazy("administrator:courses")
    model = Course


class SessionDeleteView(NoConfirmDeleteMixin):
    success_url = reverse_lazy("administrator:sessions")
    model = Session

