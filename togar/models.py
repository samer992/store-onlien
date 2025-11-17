from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from moduler.models import ModulerUserModel
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File

# Create your models here.

class TagerModel(models.Model):
    usermanage = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tagermanager")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    moduler = models.ForeignKey(ModulerUserModel, on_delete=models.CASCADE, related_name="togarmoduler")
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    shop_name = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=150, verbose_name=_("description"))
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=200, null=True)



    REQUIRED_FIELDS: ["name", "price"]

    def __str__(self):
        return self.name


class NumPhone(models.Model):
    tager = models.ForeignKey(TagerModel, on_delete=models.CASCADE, related_name="tagerphone")
    phone = models.CharField(max_length=50, null=True)

class TagerInvoicModel(models.Model):
    tager = models.ForeignKey(TagerModel, on_delete=models.CASCADE, related_name="tagerinvoice")
    usermanage = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usertagerinvoice")
    moduler = models.ForeignKey(ModulerUserModel, on_delete=models.CASCADE)
    # useremployee = models.ForeignKey(UserEmployee, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    is_finished = models.BooleanField(default=False)
    stay = models.DecimalField(decimal_places=2, max_digits=15, blank=False, default=0)
    Payment = models.DecimalField(decimal_places=2, max_digits=15, blank=False, default=0)
    total = models.DecimalField(decimal_places=2, max_digits=15, blank=False, default=0)
    barcode = models.ImageField(upload_to="images/barcodestager/", blank=True)
    barcode_id = models.CharField(max_length=13, null=True)

    def __str__(self):
        return "User: " + str(self.tager) + ", Order id: " + str(self.id)

    def save(self, *args, **kwargs):
        options = {
            'format': 'PNG',
            'font_size': 20,
            'text_distance': 2.0,
        }
        EAN = barcode.get_barcode_class("ean13")
        ean = EAN(f"{self.barcode_id}", writer=ImageWriter().set_options(options=options))
        buffer = BytesIO()
        ean.write(buffer)
        # print(File(buffer))
        # self.barcode_id = str(ean)
        self.barcode.save(f"{ean}.svg", File(buffer), save=False)

        return super().save(*args, **kwargs)


class TagerInvoicDetails(models.Model):

    invoice = models.ForeignKey(TagerInvoicModel, null=True, on_delete=models.CASCADE, related_name="tagerinvoiceitems")
    name = models.CharField(max_length=150, default="", blank=False)
    description = models.CharField(max_length=150, verbose_name=_("description"))
    price_buy = models.DecimalField(decimal_places=2, max_digits=15, default=0)
    quantity = models.DecimalField(decimal_places=2, max_digits=15, default=0.0)
    time = models.DateTimeField(auto_now_add=True)
    type_quantity = models.CharField(max_length=100, null=True)
    is_finished = models.BooleanField(default=False)


    def __str__(self):
        return "User: " + self.invoice.user.first_name + ", Invoice id: " + str(self.invoic.id)
    # @property
    # def get_full_total_sale(self):
    #     total = self.quantity * self.price
    #     return total

    @property
    def get_full_total_buy(self):
        total = self.quantity * self.price_buy
        return total
    class Meta:
        ordering = ['-id']


class TagerDof3atModel(models.Model):
    tager = models.ForeignKey(TagerModel, on_delete=models.CASCADE, related_name="dof3attager")
    usermanage = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usertagerdof3at")
    description = models.CharField(max_length=150, verbose_name=_("description"))
    dof3a = models.DecimalField(decimal_places=2, max_digits=15, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.dof3a
