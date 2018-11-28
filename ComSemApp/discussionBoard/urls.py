from django.conf.urls import url
from ComSemApp.discussionBoard import view

app_name = 'discussion_board'
urlpatterns = [
    url(r'^$', view.TopicListView.as_view(), name='topics'),
]