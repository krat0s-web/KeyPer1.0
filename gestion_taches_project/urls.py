from django.contrib import admin
from django.urls import path, include
from maison_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('taches/', views.liste_taches, name='liste_taches'),
    path('foyers/', views.liste_foyers, name='liste_foyers'),
    path('utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('creer-foyer/', views.creer_foyer, name='creer_foyer'),
    path('ajouter-tache/', views.ajouter_tache, name='ajouter_tache'),
    path('foyer/<int:foyer_id>/inviter/', views.generer_invitation, name='generer_invitation'),  # ← AJOUTÉ
    path('rejoindre/', views.rejoindre_foyer, name='rejoindre_foyer'),
    path('accounts/login/', views.custom_login, name='login'),
    path('tache/<int:tache_id>/supprimer/', views.supprimer_tache, name='supprimer_tache'),
    path('ajouter-piece/', views.ajouter_piece, name='ajouter_piece'),
    path('foyer/<int:foyer_id>/supprimer/', views.supprimer_foyer, name='supprimer_foyer'),
    path('ajouter-animal/', views.ajouter_animal, name='ajouter_animal'),
    path('piece/<int:piece_id>/supprimer/', views.supprimer_piece, name='supprimer_piece'),
    path('animal/<int:animal_id>/supprimer/', views.supprimer_animal, name='supprimer_animal'),
    path('invitation/<int:foyer_id>/', views.generer_invitation, name='generer_invitation'),
    path('logout/', views.custom_logout, name='logout'),
    path('utilisateurs-par-foyer/', views.liste_utilisateurs_par_foyer, name='liste_utilisateurs_par_foyer'),
    path('foyer/<int:foyer_id>/', views.detail_foyer, name='detail_foyer'),
    path('supprimer-membre/<int:user_id>/', views.supprimer_membre, name='supprimer_membre'),
    path('terminer-tache/<int:tache_id>/', views.terminer_tache, name='terminer_tache'),
    path('inscription/', views.inscription, name='inscription'),
    path('foyer/<int:foyer_id>/chat/', views.chat_foyer, name='chat_foyer'),
    path('mes-notes/', views.mes_notes, name='mes_notes'),
    path('mon-profil/', views.mon_profil, name='mon_profil'),
    path('mes-notifications/', views.mes_notifications, name='mes_notifications'),
    path('notification/<int:id>/lue/', views.marquer_notification_lue, name='marquer_notification_lue'),
    path('notification/<int:id>/supprimer/', views.supprimer_notification, name='supprimer_notification'),
    path('budget/', views.budget_foyer, name='budget_foyer'),
    path('ajouter-depense/', views.ajouter_depense, name='ajouter_depense'),
    path('depense/<int:id>/supprimer/', views.supprimer_depense, name='supprimer_depense'),
    path('ajouter-budget/', views.ajouter_budget, name='ajouter_budget'),
    path('api/notifications-count/', views.api_notifications_count, name='api_notifications_count'),
    path('mes-recompenses/', views.mes_recompenses, name='mes_recompenses'),
]

# ← SERVIR LES FICHIERS MÉDIAS EN DÉVELOPPEMENT
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)