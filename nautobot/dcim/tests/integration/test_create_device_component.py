from django.urls import reverse

from nautobot.core.testing.integration import SeleniumTestCase
from nautobot.dcim.models import Interface, Manufacturer, Module, ModuleBay, ModuleType
from nautobot.extras.models import Status
from nautobot.extras.tests.integration import create_test_device


class CreateDeviceComponentTestCase(SeleniumTestCase):
    """Test adding an interface to a device from the device's Add button."""

    def test_create_interface_on_module_from_device_add_button(self):
        self.login_as_superuser()

        device = create_test_device("Test Device Add Interface Module")
        module_bay = ModuleBay.objects.create(parent_device=device, name="Add Interface Bay", position="1")
        module = Module.objects.create(
            module_type=ModuleType.objects.create(
                manufacturer=Manufacturer.objects.first(), model="Add Interface Module Type"
            ),
            parent_module_bay=module_bay,
            status=Status.objects.get_for_model(Module).first(),
        )

        self.browser.visit(self.live_server_url + reverse("dcim:device", kwargs={"pk": device.pk}))
        self.browser.find_by_css("#device-add-components-button").click()
        self.browser.find_by_xpath(
            "//*[@id='device-add-components-button']/following-sibling::*//a[normalize-space()='Interfaces']"
        ).click()

        self.browser.find_by_css("#id_name_pattern").first.fill("Module Interface 1")
        for field_name, value in (("status", ""), ("type", "1000BASE-T (1GE)"), ("module", str(module))):
            self.scroll_element_into_view(xpath=f"//select[@id='id_{field_name}']/following-sibling::span")
            self.fill_select2_field(field_name, value)
        create_button = self.browser.find_by_xpath("//button[normalize-space()='Create']")
        self.scroll_element_into_view(element=create_button)
        create_button.first.click()

        self.assertTrue(self.browser.is_text_present("Module Interface 1", wait_time=5))
        interface = Interface.objects.get(name="Module Interface 1")
        self.assertEqual(interface.module, module)
        self.assertEqual(interface.device, device)
