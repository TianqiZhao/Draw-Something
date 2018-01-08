from django.conf.urls import include, url
from django.contrib import auth
from django.contrib.auth import views as auth_views
import draw_something.views

urlpatterns = [
    url(r'^home/$', draw_something.views.home, name='home'),
    url(r'^search/(?P<param>[\w\W]+)=(?P<content>[\w\W]+)$', draw_something.views.search, name='search'),

    url(r'^add-room$', draw_something.views.add_room, name='add-room'),
    url(r'^join-room/(?P<room_id>[\w\W]+)$', draw_something.views.join_room, name='join'),
    url(r'^exit-room/(?P<room_id>[\w\W]+)$', draw_something.views.exit_room, name='exit'),
    url(r'^drawer-page/(?P<room_id>[\w\W]+)$', draw_something.views.drawer_page, name='drawer'),
    url(r'^guesser-page/(?P<room_id>[\w\W]+)$', draw_something.views.guesser_page, name='guesser'),

    url(r'^profile-image/(?P<username>[\w\W]+)$', draw_something.views.profile_image, name='profile-image'),
    url(r'^edit-profile/$', draw_something.views.profile, name='edit-profile'),
    url(r'^change-password/$', draw_something.views.change_password, name='change-password'),

    url(r'^login$',draw_something.views.log_in, name='login'),
    url(r'^logout$',draw_something.views.log_out, name='logout'),
    url(r'^register$',draw_something.views.register, name='register'),
    url(r'^confirm_register/(?P<username>[\w\W]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',draw_something.views.confirm_register, name='confirm-register'),

    url(r'^get-changes/?$', draw_something.views.get_changes),
    url(r'^get-changes/(?P<time>.+)$', draw_something.views.get_changes),
    url(r'^ranks/$', draw_something.views.get_ranks, name='ranks'),

    url(r'^password_reset/$', auth_views.password_reset, {'template_name':'draw_something/password_reset_form.html',\
                                                          'email_template_name': 'draw_something/password_reset_email.html', \
                                                          'subject_template_name': 'draw_something/password_reset_subject.txt',\
                                                          'from_email': 'support@grumblr.com'}, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, {'template_name':'draw_something/password_reset_done.html'}, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',\
        auth_views.password_reset_confirm, {'template_name':'draw_something/password_reset_confirm.html'}, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, {'template_name':'draw_something/password_reset_complete.html'}, name='password_reset_complete'),
]