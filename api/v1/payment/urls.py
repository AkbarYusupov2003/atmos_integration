from django.urls import path

from api.v1.payment import views


urlpatterns = [
    # Bind Card
    path("atmos/bind-card/init", views.AtmosBindCardInitAPIView.as_view()),
    path("atmos/bind-card/confirm", views.AtmosBindCardConfirmAPIView.as_view()),
    path("atmos/bind-card/dial", views.AtmosBindCardDialAPIView.as_view()),
    path("atmos/bind-card/list", views.AtmosBindCardListAPIView.as_view()),
    path("atmos/bind-card/remove", views.AtmosBindCardRemoveAPIView.as_view()),
    # Pay Scheduler
    path("atmos/pay-scheduler/create", views.AtmosPaySchedulerCreateAPIView.as_view()),
    path("atmos/pay-scheduler/confirm", views.AtmosPaySchedulerConfirmAPIView.as_view()),
    path("atmos/pay-scheduler/change", views.AtmosPaySchedulerChangeAPIView.as_view()),
]
