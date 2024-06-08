from django.urls import path
from .views import user_dashboard, user_info, user_address, fetch_notifications, mark_notification_as_read


app_name = 'accounts'

urlpatterns = [
    path('dashboard/', user_dashboard, name='dashboard'),
    path('dashboard/info/', user_info, name='info'),
    path('dashboard/address/', user_address, name='address'),
    path('notifications/', fetch_notifications, name='notifications'),
    path('notifications/mark-notification/<int:notification_id>/', mark_notification_as_read, name='mark_notification_as_read'),

]
