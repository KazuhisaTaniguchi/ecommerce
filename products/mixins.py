# -*- coding: utf-8 -*-
# from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

from django.utils.decorators import method_decorator

from django.http import Http404


class StaffRequireMixin(object):
    @classmethod
    def as_view(self, *args, **kwargs):
        view = super(StaffRequireMixin, self).as_view(*args, **kwargs)
        return login_required(view)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super(
                StaffRequireMixin, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404


class LoginRequireMixin(object):
    @classmethod
    def as_view(self, *args, **kwargs):
        view = super(LoginRequireMixin, self).as_view(*args, **kwargs)
        return login_required(view)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(
            LoginRequireMixin, self).dispatch(request, *args, **kwargs)
