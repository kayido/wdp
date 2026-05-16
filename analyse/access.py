from django.contrib.auth.decorators import user_passes_test


def staff_permissions_required(*permissions):
    def has_access(user):
        if not user.is_authenticated or not user.is_staff:
            return False
        if user.is_superuser:
            return True
        return all(user.has_perm(permission) for permission in permissions)

    return user_passes_test(has_access, login_url="/admin/login/")


staff_required = staff_permissions_required()
image_view_required = staff_permissions_required("analyse.view_image")
image_change_required = staff_permissions_required("analyse.change_image")
signalement_view_required = staff_permissions_required("analyse.view_signalement")
zone_view_required = staff_permissions_required("analyse.view_zonerisques")
zone_add_required = staff_permissions_required("analyse.add_zonerisques")
classification_view_required = staff_permissions_required("analyse.view_classificationdefine")
classification_add_required = staff_permissions_required("analyse.add_classificationdefine")
classification_change_required = staff_permissions_required("analyse.change_classificationdefine")
