from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
urlpatterns = [
    path('extraction/',views.page1,name='page1'),
    url('extraction/page2',views.page2,name='page2'),
    path('extraction/page3',views.page3,name='page3'),
    path('extraction/page4',views.extractionpage,name='page4'),
    url('extraction/upload',views.upload,name='upload'),
    path('extraction/fonctionExtraction',views.fonctionExtraction,name='extract'),
    url('extraction/func_page_to_keep',views.func_page_to_keep,name='func_page_to_keep'),
    url(r'^pdf', views.pdf, name='pdf'),
    path('extraction/prediction',views.prediction,name='prediction')


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.SHORTPDF_URL, document_root=settings.SHORTPDF_ROOT)
