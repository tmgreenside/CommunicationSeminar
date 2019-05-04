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
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from ComSemApp.teacher import constants as teacher_constants

from ComSemApp.models import *
from ComSemApp.libs.mixins import RoleViewMixin, CourseViewMixin, WorksheetViewMixin, SubmissionViewMixin


#This class deals with listing out all the topics within database
#brings back the Topic model and displays it using Django Listview
#This page requires you to be logged in to use
class TopicListView(LoginRequiredMixin,ListView):
    model = Topic
    template_name = 'ComSemApp/discussionBoard/topic_list.html'
    context_object_name = 'topics'

    def get_queryset(self):
        return Topic.objects.filter()

class ReplyMixin(LoginRequiredMixin, object):
    def dispatch(self, request, *args, **kwargs):
        topic_id = kwargs.get('topic_id', None)
        topics = Topic.objects.filter(id = topic_id)
        if not topics.exists():
            return HttpResponseRedirect(reverse("discussion_board:topics"))
        self.topic = topics.first()
        return super(ReplyMixin, self).dispatch(request, *args, **kwargs)
    


class ReplyView(ReplyMixin, ListView):
    model = Reply
    template_name = 'ComSemApp/discussionBoard/reply_page.html'
    context_object_name = 'replies'

    def get_queryset(self):
        return Reply.objects.filter(topic = self.topic)

    def get_context_data(self, **kwargs):
        context = super(ReplyView, self).get_context_data(**kwargs)
        context['topic_description'] = self.topic.topic
        context['discussion_board'] = True
        return context

class CreateThreadView(LoginRequiredMixin,CreateView):
    print("Hello World")

