
from logging import PlaceHolder
from random import random
from django.http.response import HttpResponse
from django.shortcuts import render
from markdown2 import Markdown
from django.utils.html import format_html
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse

# Desde este mismo directorio (eso es el punto), importar el archivo util.py
from . import util


class SearchForm(forms.Form):
    searchTxt = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'Search Encyclopedia'}))


class NewForm(forms.Form):
    entryTitle = forms.CharField(label='Entry title')
    entryMarkdownTxt = forms.CharField(
        label='Entry Markdown text', widget=forms.Textarea(attrs={"rows": 5, "cols": 15}))


class UpdateForm(forms.Form):
    entryMarkdownTxt = forms.CharField(
        label='Entry Markdown text', widget=forms.Textarea(attrs={"rows": 5, "cols": 15}))


def index(request):
    if request.method == "POST":
        searchForm = SearchForm(request.POST)
        if searchForm.is_valid():
            searchTxt = searchForm.cleaned_data["searchTxt"]
            entries = util.list_entries()
            entriesUpper = [x.upper() for x in entries]
            if searchTxt.upper() in entriesUpper:
                return HttpResponseRedirect(reverse('entry', kwargs={'pathRecived': searchTxt}))
            else:
                entriesFiltered = []
                for entry in entries:
                    if searchTxt.upper() in entry.upper():
                        entriesFiltered.append(entry)
                return render(
                    request,
                    "encyclopedia/index.html",
                    {
                        "listTitle": "Search Results",
                        "searchForm": SearchForm(),
                        "entries": entriesFiltered
                    }
                )
    return render(
        request,
        "encyclopedia/index.html",
        {
            "listTitle": "All Pages",
            "searchForm": SearchForm(),
            "entries": util.list_entries()
        }
    )


def entry(request, pathRecived):
    markdowner = Markdown()
    visibleLink = True
    # Verify the reserved command 'cmdrandompage'
    if pathRecived == 'cmdrandompage':
        entries = util.list_entries()
        if len(entries) > 0:
            randomEntry = entries[round((len(entries)-1)*random())]
            entryContent = util.get_entry(randomEntry)
            return render(
                request,
                "encyclopedia/entry.html",
                {
                    "visibleLink": visibleLink,
                    "entryTitle": randomEntry,
                    "entryContent": format_html(markdowner.convert(entryContent))
                }
            )
        else:
            visibleLink = False
            return render(
                request,
                "encyclopedia/entry.html",
                {
                    "visibleLink": visibleLink,
                    "entryTitle": pathRecived,
                    "entryContent": format_html(f" <h1 > Error: List is empty </h1>")
                }
            )
    else:
        entryContent = util.get_entry(pathRecived)
        if entryContent == None:
            visibleLink = False
            entryContent = f" <h1 > Error: Entry '{pathRecived}' does not exist! </h1>"
        else:
            entryContent = markdowner.convert((entryContent))
        return render(
            request,
            "encyclopedia/entry.html",
            {
                "visibleLink": visibleLink,
                "entryTitle": pathRecived,
                "entryContent": format_html(entryContent)
            }
        )


def new(request):
    if request.method == "POST":
        newForm = NewForm(request.POST)
        if newForm.is_valid():
            entryTitle = newForm.cleaned_data["entryTitle"]
            entryMarkdownTxt = newForm.cleaned_data["entryMarkdownTxt"]
            entries = util.list_entries()
            entriesUpper = [x.upper() for x in entries]
            # Entry already exist
            if entryTitle.upper() in entriesUpper:
                return render(
                    request,
                    "encyclopedia/new.html",
                    {
                        "title": "Create New Page",
                        "newForm": newForm,
                        "errorAlreadyExist": True
                    }
                )
            else:
                util.save_entry(entryTitle.upper(), entryMarkdownTxt)
                return HttpResponseRedirect(reverse('entry', kwargs={'pathRecived': entryTitle}))
    return render(
        request,
        "encyclopedia/new.html",
        {
            "title": "Create New Page",
            "newForm": NewForm(),
            "errorAlreadyExist": False
        }
    )


def update(request, entryTitle):
    if request.method == "POST":
        updateForm = UpdateForm(request.POST)
        if updateForm.is_valid():
            entryMarkdownTxt = updateForm.cleaned_data["entryMarkdownTxt"]
            util.save_entry(entryTitle, entryMarkdownTxt)
            return HttpResponseRedirect(reverse('entry', kwargs={'pathRecived': entryTitle}))

    return render(
        request,
        "encyclopedia/update.html",
        {
            "title": "Update Existing Page",
            "entryTitle": entryTitle,
            "updateForm": UpdateForm(initial={'entryMarkdownTxt': util.get_entry(entryTitle)})
        }
    )
