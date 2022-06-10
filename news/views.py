# Create your views here.
from django.shortcuts import render
from django.views.generic import ListView, UpdateView, CreateView, DetailView, DeleteView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .filters import PostFilter
from .models import Post, PostCategory
from .forms import PostForm


# Список статей
class PostList(ListView):
    model = Post
    ordering = '-time_in'
    template_name = 'news.html'
    context_object_name = 'page'
    paginate_by = 2
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
        return super().get(request, *args, **kwargs)

    # Фильтры со страницами вместе не работали, или одно или другое
    # Где ошиблась с описанием - не нашла.
    #
    # Решила сделать как тут (нашла в гугле)
    # https://stackoverflow.com/questions/44048156/django-filter-use-paginations
    #
    # В итоге фильтры и paginator вызваны руками в нужном порядке
    # и подставлены в результат - страница с данными, объект страницы, и фильтр для формы
    #
    # Также использовала query_transform для формирования правильных URL для перехода
    # между страницами paginator по результатам фильтра (подсмотрела там же)
    def get(self, request, *args, **kwargs):
        sfilter = PostFilter(request.GET, queryset=self.get_queryset())
        filtered_qs = sfilter.qs
        paginator = Paginator(filtered_qs, self.paginate_by)
        page = request.GET.get('page', 1)

        try:
            result = paginator.page(page)
        except PageNotAnInteger:
            result = paginator.page(1)
        except EmptyPage:
            result = paginator.page(paginator.num_pages)

        return render(request, 'news.html', {
            'page': result,
            'page_obj': result,
            'filter': sfilter
        })


# Одна статья в деталях
class PostDetailView(DetailView):
    template_name = 'news/post_detail.html'
    queryset = Post.objects.all()


# Создание новой статьи
class PostCreateView(CreateView):
    template_name = 'news/post_create.html'
    form_class = PostForm


# Альтернативный показ одной статьи, из прошлого урока
class PostDetail(DetailView):
    model = Post
    template_name = 'article.html'
    context_object_name = 'article'


# Редактирование статьи
class PostUpdateView(UpdateView):
    template_name = 'news/post_create.html'
    form_class = PostForm

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте, который мы собираемся
    # редактировать
    def get_object(self, **kwargs):
        sid = self.kwargs.get('pk')
        return Post.objects.get(pk=sid)


# Удаление статьи с запросом подтверждения
class PostDeleteView(DeleteView):
    template_name = 'news/post_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'


# ручной поиск по заголовку в отдельной странице, проба пера
class SearchNews(ListView):
    def get(self, request):
        news = Post.objects.filter(title__contains=request.GET.get('q')).order_by('-time_in')
        data = {
            'found': news,
        }
        return render(request, 'search.html', data)
