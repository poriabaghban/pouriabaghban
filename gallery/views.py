from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from .models import GalleryImage, GalleryCategory, PortfolioItem, PortfolioCategory


def _paginated_items(request, queryset, per_page=16):
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page')
    return paginator.get_page(page)


def gallery_list(request):
    images = _paginated_items(request, GalleryImage.objects.all().order_by('-created_at'))
    context = {
        'images': images,
        'categories': GalleryCategory.objects.all(),
        'title': _('گالری'),
        'page_kind': 'gallery',
        'empty_message': _('هنوز تصویری در گالری وجود ندارد.'),
        'all_url_name': 'gallery:gallery-list',
        'category_url_name': 'gallery:gallery-category',
    }
    return render(request, 'gallery/gallery_list.html', context)


def gallery_category(request, category):
    try:
        cat = GalleryCategory.objects.get(name=category)
        queryset = GalleryImage.objects.filter(category=cat).order_by('-created_at')
    except GalleryCategory.DoesNotExist:
        queryset = GalleryImage.objects.none()

    images = _paginated_items(request, queryset)
    context = {
        'images': images,
        'categories': GalleryCategory.objects.all(),
        'selected_category': category,
        'title': _('گالری - %(category)s') % {'category': category},
        'page_kind': 'gallery',
        'empty_message': _('در این دسته هنوز تصویری وجود ندارد.'),
        'all_url_name': 'gallery:gallery-list',
        'category_url_name': 'gallery:gallery-category',
    }
    return render(request, 'gallery/gallery_list.html', context)


def portfolio_list(request):
    items = _paginated_items(request, PortfolioItem.objects.all().order_by('-created_at'))
    context = {
        'images': items,
        'categories': PortfolioCategory.objects.all(),
        'title': _('نمونه کار'),
        'page_kind': 'portfolio',
        'empty_message': _('هنوز نمونه کاری ثبت نشده است.'),
        'all_url_name': 'gallery:portfolio-list',
        'category_url_name': 'gallery:portfolio-category',
    }
    return render(request, 'gallery/gallery_list.html', context)


def portfolio_category(request, category):
    try:
        cat = PortfolioCategory.objects.get(name=category)
        queryset = PortfolioItem.objects.filter(category=cat).order_by('-created_at')
    except PortfolioCategory.DoesNotExist:
        queryset = PortfolioItem.objects.none()

    items = _paginated_items(request, queryset)
    context = {
        'images': items,
        'categories': PortfolioCategory.objects.all(),
        'selected_category': category,
        'title': _('نمونه کار - %(category)s') % {'category': category},
        'page_kind': 'portfolio',
        'empty_message': _('در این دسته هنوز نمونه کاری ثبت نشده است.'),
        'all_url_name': 'gallery:portfolio-list',
        'category_url_name': 'gallery:portfolio-category',
    }
    return render(request, 'gallery/gallery_list.html', context)

def portfolio_detail(request, pk):
    item = get_object_or_404(PortfolioItem, pk=pk)
    return render(request, 'gallery/portfolio_detail.html', {'item': item})

