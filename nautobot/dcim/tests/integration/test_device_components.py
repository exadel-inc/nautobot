from django.urls import reverse

from nautobot.core.testing.integration import SeleniumTestCase
from nautobot.dcim.models import Interface, Manufacturer, Module, ModuleBay, ModuleType
from nautobot.extras.models import Status
from nautobot.extras.tests.integration import create_test_device


class DeviceComponentAddButtonTestCase(SeleniumTestCase):
    """Integration tests for adding a component from a Device's Add button."""

    def setUp(self):
        super().setUp()
        self.login_as_superuser()

    def tearDown(self):
        self.logout()
        super().tearDown()

    def test_add_interface_keeps_selected_module(self):
        device = create_test_device("Add Button Device")
        manufacturer = Manufacturer.objects.create(name="Add Button Manufacturer")
        module_bay = ModuleBay.objects.create(parent_device=device, name="Add Button Bay", position="1")
        module = Module.objects.create(
            module_type=ModuleType.objects.create(manufacturer=manufacturer, model="Add Button Module Type"),
            parent_module_bay=module_bay,
            status=Status.objects.get_for_model(Module).first(),
        )

        self.browser.visit(self.live_server_url + reverse("dcim:interface_add") + f"?device={device.pk}")
        self.assertTrue(self.browser.is_element_present_by_name("_create", wait_time=5), "Page failed to load")
        self.fill_select2_field("module", "Add Button Module Type")
        self.fill_input("name_pattern", "add-button-interface")
        self.fill_select2_field("status", "Active")
        self.fill_select2_field("type", "1000BASE-T")
        self.click_edit_form_create_button()

        interface = Interface.objects.get(name="add-button-interface")
        self.assertEqual(interface.device, device)
        self.assertEqual(interface.module, module)
