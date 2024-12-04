from django.urls import path
from . import views

# Endpoints basados en:
#   /api/v1/login/
#   /api/v1/refresh/
#   /api/v1/users/
#   /api/v1/rest/productos/
#   /api/v1/rest/ordenes/
#
# Cada uno manda llamar a la función correspondiente de las vistas.
urlpatterns = [
    path('api/v2/login/', views.login, name='login'),
    path('api/v2/refresh/', views.refresh_token, name='refresh_token'),
    path('api/v2/users/', views.users_proxy, name='users_proxy'),
    path('api/v2/rest/productos/', views.rest_productos_proxy, name='rest_productos_proxy'),
    path('api/v2/rest/productos/<int:id>/', views.rest_productos_proxy_by_id, name='rest_productos_proxy_by_id'),
    path('api/v2/rest/ordenes/', views.rest_ordenes_proxy, name='rest_orders_proxy'),
    path('api/v2/rest/ordenes/<int:id>', views.rest_ordenes_by_id_proxy, name='rest_orders_by_id_proxy'),
]