# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Views for managing images.
"""
from django.core.urlresolvers import reverse  # noqa
from django.core.urlresolvers import reverse_lazy  # noqa
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import forms
from horizon import tabs

from openstack_dashboard import api

from openstack_dashboard.dashboards.project.images_and_snapshots.images \
    import forms as project_forms
from openstack_dashboard.dashboards.project.images_and_snapshots.images \
    import tabs as project_tabs


class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateImageForm
    template_name = 'project/images_and_snapshots/images/create.html'
    context_object_name = 'image'
    success_url = reverse_lazy("horizon:project:images_and_snapshots:index")


class UpdateView(forms.ModalFormView):
    form_class = project_forms.UpdateImageForm
    template_name = 'project/images_and_snapshots/images/update.html'
    success_url = reverse_lazy("horizon:project:images_and_snapshots:index")

    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                self._object = api.glance.image_get(self.request,
                                                    self.kwargs['image_id'])
            except Exception:
                msg = _('Unable to retrieve image.')
                url = reverse('horizon:project:images_and_snapshots:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['image'] = self.get_object()
        return context

    def get_initial(self):
        image = self.get_object()
        properties = getattr(image, 'properties', {})
        return {'image_id': self.kwargs['image_id'],
                'name': getattr(image, 'name', None) or image.id,
                'description': properties.get('description', ''),
                'kernel': properties.get('kernel_id', ''),
                'ramdisk': properties.get('ramdisk_id', ''),
                'architecture': properties.get('architecture', ''),
                'disk_format': getattr(image, 'disk_format', None),
                'public': getattr(image, 'is_public', None),
                'protected': getattr(image, 'protected', None)}


class DetailView(tabs.TabView):
    tab_group_class = project_tabs.ImageDetailTabs
    template_name = 'project/images_and_snapshots/images/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["image"] = self.get_data()
        return context

    def get_data(self):
        if not hasattr(self, "_image"):
            try:
                image_id = self.kwargs['image_id']
                self._image = api.glance.image_get(self.request, image_id)
            except Exception:
                url = reverse('horizon:project:images_and_snapshots:index')
                exceptions.handle(self.request,
                                  _('Unable to retrieve image details.'),
                                  redirect=url)

        return self._image

    def get_tabs(self, request, *args, **kwargs):
        image = self.get_data()
        return self.tab_group_class(request, image=image, **kwargs)
