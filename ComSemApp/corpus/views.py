from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db import connection

import nltk
from nltk.data import load

import json
from ComSemApp.models import *

#TODO: is the user a teacher or Admin

@login_required
def corpus_search(request):
    tags = Tag.objects.all()
    template = loader.get_template('ComSemApp/corpus/corpus_search_new.html')
    return HttpResponse(template.render({'tags': tags, 'offsetRange':[i for i in range(-8,8+1)]}, request))

@login_required
def populate_word_tag(request):
    val = request.POST.get('val', None).lstrip(' ').rstrip(' ')
    search_type = request.POST.get('type', None)
    output = request.POST.get('output', None)

    print("Value:", val)

    context = {}
    id_list = []
    if(search_type == 'word'):
        template = loader.get_template('ComSemApp/corpus/word_table.html')
        words = Word.objects.filter(form=val)
        context = {'val': val, 'words': words} # for html
        id_list = []
        for word in words:
            id_list.append(word.id)
        json_response = {'val': val, 'id_list': id_list} # for json

    else:
        template = loader.get_template('ComSemApp/corpus/tag_table.html')
        if val == "ALL":
            tags = Tag.objects.all()
        else:
            tags = Tag.objects.filter(tag=val)
        context = {'val': val, 'tags': tags} # for html
        for tag in tags:
            id_list.append(tag.id)
        json_response = {'val': val, 'id_list': id_list} # for json

    if output == 'html':
        return HttpResponse(template.render(context, request))
    else:
        return JsonResponse(json_response)


@login_required
def search_results(request):
    sequential_search = request.POST.get('searchType') == '1'
    search_criteria = request.POST.get('searchCriteria', None)

    if not search_criteria or search_criteria == "":
        return HttpResponse('No search criteria provided', status=401)

    search_criteria = json.loads(search_criteria)

    # query = build_query(len(search_criteria) - 1, search_criteria, sequential_search)
    query = build_query(search_criteria, sequential_search)

    print(query)
    print(search_criteria)

    with connection.cursor() as cursor:
        expression_ids = []
        cursor.execute(query)
        for row in cursor.fetchall():
            expression_ids.append(row[0])

    # grab the information we want about the expressions
    expressions = Expression.objects.filter(id__in=expression_ids)

    context = {
        'expressions': expressions,
        'sequential_search': sequential_search,
        'search_criteria': search_criteria,
    }
    template = loader.get_template('ComSemApp/corpus/search_results.html')
    return HttpResponse(template.render(context, request))

# This query builder makes the following assumptions about the search criteria:
# there is one word, either a tag or a second word, and there may be an offset.
def build_query(search_criteria, sequential_search):
    words = []
    tags = []
    offset = 0
    for item in search_criteria:
        if item['type'] == 'word':
            words.append(item)
        elif item['type'] == 'tag':
            tags.append(item)
        elif item['type'] == 'offset' and sequential_search == True:
            offset = item['val']

    if len(words) == 0:
        return ""

    query = "SELECT SW.expression_id"
    if sequential_search:
        query += ", SW.position"
    query += " FROM ComSemApp_sequentialwords as SW"

    if len(words) > 1 or len(tags) > 0:
        query += ", (SELECT SW2.expression_id"
        if sequential_search:
            query += ", SW2.position"
        query += " from ComSemApp_sequentialwords as SW2"
        if len(tags) > 0:
            query += ", ComSemApp_word as W where W.tag_id in (" + ','.join([str(id) for id in tags[0]['id_list']])
            query += ") and SW2.word_id = W.id"
        else:
            query += " where SW2.word_id in (" + ','.join([str(id) for id in words[1]['id_list']])
            query += ")"
        query += ") as derived2"
    query += " where SW.word_id in (" + ','.join([str(id) for id in words[0]['id_list']])
    query += ")"

    if len(words) > 1 or len(tags) > 0:
        query += " and SW.expression_id = derived2.expression_id"

    if offset > 0:
        query += " and derived2.position <= (SW.position + " + str(offset) + ") and SW.position < derived2.position"
    elif offset < 0:
        query += " and SW.position <= (derived2.position + " + str(abs(offset)) + ") and derived2.position < SW.position"

    return query


# work backwards through the search criteria - we make n - 1 joins (where n = number of search criteria) with n tables that
# select expression ID and position (if sequential search).
# def build_query(i, search_criteria, sequential_search):
#     current_criteria = search_criteria[i]
#     criteria_type = current_criteria['type']
#     val = current_criteria['val']
#     id_list = current_criteria['id_list']
#
#     # if val isnt valid, id_list isn't a list of int ...
#
#     if i < 0:
#         return ""
#     else:
#         if(criteria_type == "offset"):
#             print ("to do")
#
#         select_position = ", SW.Position" if sequential_search else ""
#         from_words = ", ComSemApp_word as W " if criteria_type == "tag" else ""
#
#         query = "SELECT SW.expression_id" + select_position + " FROM ComSemApp_sequentialwords AS SW" + from_words
#
#         if i > 0:
#             query += ", (" + build_query(i - 1, search_criteria, sequential_search) + ") as Derived" + str(i)
#
#         query += " WHERE "
#
#         if criteria_type == "tag" and len(id_list) > 0:
#             query += " SW.word_id = W.id AND W.tag_id in (" + ','.join([str(id) for id in id_list]) + ") "
#
#         elif criteria_type == "word" and len(id_list) > 0:
#             query += " SW.word_id in (" + ','.join([str(id) for id in id_list]) + ") "
#
#         else:
#             query += " '1' = '1' " # hacky way to prevent error when building query
#
#         if i > 0:
#             if sequential_search:
#                 next_position = 0
#
#                 # if the next search criteria is an offset, we'll use it here then skip it in the next call.
#                 if search_criteria[i-1]['type'] == 'offset':
#                     next_position += search_criteria[i-1]['val']
#
#                 if next_position > 0:
#                     query += "AND SW.position <= (Derived" + str(i) + ".position + " + str(next_position) + ") "
#                 elif next_position < 0:
#                     query += "AND Derived" + str(i) + ".position <= (SW.position + " + str(abs(next_position)) + ") "
#
#             query += "AND SW.expression_id = Derived" + str(i) + ".expression_id "
#         return query
