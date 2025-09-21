from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('book-appointment', views.book_appointment, name='book_appointment'),
    
    #login
    # path('admin-login', views.login, name='admin_login')

    path('admin/login', views.admin_login, name='login'),
    path("logout/", auth_views.LogoutView.as_view(next_page='login'), name="logout"),
    path('admin/logout', LogoutView.as_view(), name='admin_logout'),
    path("admin/download-appointments/", views.download_appointments_excel, name="download_appointments"),
    path('admin/appointments', views.admin_appointments, name='admin_appointments'),
    path('admin/dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('admin/add-appointment', views.admin_add_appointment, name='admin_add_appointment'),
    path('admin/manage-admins', views.manage_admins, name='manage_admins'),
    path('admin/add-admin', views.add_admin, name='add_admin'),
    path('admin/edit-admin/<int:user_id>/', views.edit_admin, name='edit_admin'),
    path('admin/delete-admin/<int:user_id>/', views.delete_admin, name='delete_admin'),
    path('admin/make-doctor/<int:id>/', views.set_doctor, name='make_doctor'),
    path('admin/remove-doctor/<int:id>/', views.remove_doctor, name='remove_doctor'),
    path('admin/profile', views.admin_profile, name='admin_profile'),
    path('admin/logout', views.admin_logout, name='admin-logout')
]    
