from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.views.generic.detail import SingleObjectMixin

from .models import Village


class VillageListView(ListView):
    queryset = Village.objects.not_deleted()
    template_name = 'village_list.html'
    context_object_name = 'villages'


class VillageDetailView(DetailView):
    queryset = Village.objects.not_deleted()
    template_name = 'village_detail.html'
    context_object_name = 'village'


class VillageCreateView(LoginRequiredMixin, CreateView):
    model = Village
    template_name = 'village_form.html'
    fields = ['name', 'description', 'private']
    success_url = reverse_lazy('villages:list')

    def form_valid(self, form):
        village = form.save(commit=False)
        village.contact = self.request.user
        village.save()
        return HttpResponseRedirect(village.get_absolute_url())


class EnsureUserOwnsVillageMixin(SingleObjectMixin):
    model = Village

    def dispatch(self, request, *args, **kwargs):
        # If the user is not contact for this village OR is not staff
        if not request.user.is_staff:
            if self.get_object().contact != request.user:
                raise Http404("Village not found")

        return super(EnsureUserOwnsVillageMixin, self).dispatch(
            request, *args, **kwargs
        )


class VillageUpdateView(EnsureUserOwnsVillageMixin, LoginRequiredMixin, UpdateView):
    model = Village
    queryset = Village.objects.not_deleted()
    template_name = 'village_form.html'
    fields = ['name', 'description', 'private']

    def get_success_url(self):
        return self.get_object().get_absolute_url()


class VillageDeleteView(EnsureUserOwnsVillageMixin, LoginRequiredMixin, DeleteView):
    model = Village
    success_url = reverse_lazy('villages:list')
    template_name = 'village_confirm_delete.html'
    context_object_name = 'village'
