from . import models


class AddUserToPreferenceMixin(object):
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
            return super().form_valid(form)
        else:
            form.add_error(None, "User must be logged in to create.")
            return self.form_invalid(form)


class UniquePerUserMixin(object):
    def form_valid(self, form):
        try:
            _ = models.Profile.objects.get(user=form.instance.user)
            # _ = form.instance.user.profile
            print("form.instance.user.profile = %s" % form.instance.user.profile)
        except models.Profile.DoesNotExist:
            return super().form_valid(form)
        else:
            form.add_error(None, "You already have an existing profile." +
                                 " Please update it instead of creating another one.")
            return self.form_invalid(form)


class UserOwnerMixin(object):
    def form_valid(self, form):
        if form.instance.user == self.request.user:
            return super(UserOwnerMixin, self).form_valid(form)
        else:
            form.add_error(None, "You are not allowed to change this data")
            return self.form_invalid(form)