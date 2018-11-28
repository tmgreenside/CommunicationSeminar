import json

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

from ComSemApp.teacher import constants as teacher_constants

from ComSemApp.models import *
from ComSemApp.libs.mixins import RoleViewMixin, CourseViewMixin, WorksheetViewMixin, SubmissionViewMixin


class TopicListView(ListView):
    # discussion board topic page
    model = Topic
    template_name = 'ComSemApp/discussionBoard/topic_list.html'
    context_object_name = 'topics'

    def get_queryset(self):
        return Topic.objects.filter()