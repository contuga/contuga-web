class OnlyAuthoredByCurrentUserMixin:

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)


class OnlyOwnedByCurrentUserMixin:

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)
