from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import DeleteView
from django.views.generic.list import ListView
from django.views import View
from chatgpt_parser.app import generate_texts, generate_text_set_zip
from chatgpt_parser.forms import CreateTextForm
from chatgpt_parser.models import TextsParsingSet
from django.http import FileResponse
import logging


logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'index.html')


class LoginUser(LoginView):
    template_name = 'login_user.html'
    next_page = reverse_lazy('index')
    form_class = AuthenticationForm


class LogoutUser(LogoutView):
    template_name = 'index.html'
    next_page = reverse_lazy('index')


class GenerateTexts(View):
    def get(self, request, *args, **kwargs):
        form = CreateTextForm()
        return render(request, 'generate_texts.html', {'form': form})

    def post(self, request, *args, **kwargs):
        generate_texts.delay(
            author=request.user.id,
            set_name=request.POST.get('set_name', ''),
            temperature=request.POST.get('temperature', ''),
            task_strings=request.POST.get('tasks_strings', ''),
            required_uniqueness=request.POST.get('required_uniqueness', ''),
            rewriting_task=request.POST.get('rewriting_task', ''))
        return render(request, 'index.html')



def generate_set_for_download(request, set_id):
    text_set = TextsParsingSet.objects.get(id=set_id)
    zip_buffer = generate_text_set_zip(text_set)

    response = FileResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{text_set.set_name}.zip"'
    return response


class TextsList(ListView):
    model = TextsParsingSet
    template_name = 'text_set_list.html'
    context_object_name = 'text_sets'
    queryset = TextsParsingSet.objects.all().order_by('created_at')


class DeleteTextsSet(DeleteView):
    model = TextsParsingSet
    template_name = 'delete_text_set.html'
    success_url = reverse_lazy('texts_list')
