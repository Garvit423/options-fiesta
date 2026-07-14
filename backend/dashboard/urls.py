from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/greeks/', views.get_greeks, name='get_greeks'),
    path('api/ivs/', views.get_ivs, name='get_ivs'),
    path('api/iv/', views.get_iv_timeseries, name='get_iv_timeseries'),  # Added trailing slash
    path('api/backtest/', views.get_backtest, name='backtest')  # Added trailing slash for consistency
]