def notifications_count(request):
    """Context processor pour passer le nombre de notifications non lues à tous les templates"""
    if request.user.is_authenticated:
        non_lues = request.user.notifications.filter(lue=False).count()
        return {'notifications_non_lues': non_lues}
    return {'notifications_non_lues': 0}

