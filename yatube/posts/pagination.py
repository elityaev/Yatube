from django.core.paginator import Paginator

from yatube.settings import NUM_POST_PER_PAGE


def pagination(posts, request):
    paginator = Paginator(posts, NUM_POST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj