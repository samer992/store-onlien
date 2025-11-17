from time import strftime
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from moduler.models import ModulerUserModel
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
# from creditcards.models import CardNumberField
import os
# from io import BytesIO
# from time import strftime
from PIL import Image, ImageDraw, ImageFont
# from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from django_resized import ResizedImageField
# from django.utils.translation import gettext_lazy as _
# Create your models here.
################### ==> Products <== ###################
# from PIL import Image
def upload_to(instance, filename):
    return f"profile_pictures/{strftime('%y/%m/%d')}/{filename}"

class Products(models.Model):
    usermanage = models.ForeignKey(User, on_delete=models.CASCADE, related_name="productmanager")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    moduler = models.ForeignKey(ModulerUserModel, on_delete=models.CASCADE, related_name="productsmoduler")
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    description = models.CharField(max_length=150, verbose_name=_("description"))
    price_sale = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    total_quantity = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    quantity_box = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    type_quantity = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=100, null=True, default="qta3e")
    # product_picture = models.ImageField(upload_to=upload_to, default="profile_img/store_logo.png")
    product_picture = ResizedImageField(upload_to=upload_to, size=[300, 300], quality=75, force_format='JPEG', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type_id = models.IntegerField(default=1)
    barcode = models.ImageField(upload_to="images/", blank=True)
    barcode_id = models.CharField(max_length=13, null=True)
    total_sale = models.DecimalField(decimal_places=2, max_digits=50, default=0)



    REQUIRED_FIELDS: ["name", "price"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.product_picture:
            image = self.generate_initial_image(self.name)
            img_io = BytesIO()
            image.save(img_io, format='PNG')
            image_name = f"{self.name.lower().replace(' ', '_')}_auto.png"
            self.product_picture.save(image_name, ContentFile(img_io.getvalue()), save=False)

        super().save(*args, **kwargs)

    def generate_initial_image(self, text):
        width, height = 300, 300
        text_color = (255, 255, 255)  # نص أبيض
        font_size = 120

        # ألوان Google Contacts
        colors = [
            (244, 67, 54), (233, 30, 99), (156, 39, 176),
            (63, 81, 181), (33, 150, 243), (0, 188, 212),
            (0, 150, 136), (76, 175, 80), (139, 195, 74),
            (205, 220, 57), (255, 235, 59), (255, 193, 7),
            (255, 152, 0), (121, 85, 72), (96, 125, 139)
        ]

        # أول حرف
        initial = text.strip()[0].upper() if text else '?'
        color_index = ord(initial) % len(colors)
        background_color = colors[color_index]

        # إنشاء الصورة
        image = Image.new('RGB', (width, height), color=background_color)
        draw = ImageDraw.Draw(image)

        # الخط (يدعم عربي وإنجليزي)
        font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Cairo-Regular.ttf')
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()

        # أبعاد النص (bbox)
        bbox = draw.textbbox((0, 0), initial, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # حساب المركز مع مراعاة baseline
        x = (width - text_width) / 2 - bbox[0]
        y = (height - text_height) / 2 - bbox[1]

        # رسم النص
        draw.text((x, y), initial, fill=text_color, font=font)

        return image


class PriceBuyProduct(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="productitems")
    quantity = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    quantity_total = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    price_buy = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    total_buy = models.DecimalField(decimal_places=2, max_digits=50, default=0)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class CatgoryProductType(models.Model):
    # usermanage = models.ForeignKey(User, on_delete=models.CASCADE, related_name="catpromanager")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    moduler = models.ForeignKey(ModulerUserModel, on_delete=models.CASCADE, related_name="modulercatgoryitems")

    REQUIRED_FIELDS: ["name", "price"]

    def __str__(self):
        return self.name

################### ==> Order <== ###################

class ClosedDay(models.Model):
    usermanage = models.ForeignKey(User, on_delete=models.CASCADE)
    moduler = models.ForeignKey(ModulerUserModel, on_delete=models.CASCADE, null=True, related_name="modulerclosed")
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(auto_now_add=True)
    is_finished = models.BooleanField(default=False)
    # buyManager_total = models.DecimalField(decimal_places=2, max_digits=7, blank=False, default=0)
    # closeDay_total = models.DecimalField(decimal_places=2, max_digits=7, blank=False, default=0)

class ClosedEmp(models.Model):
    usermanage = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user")
    moduler = models.ForeignKey(ModulerUserModel, on_delete=models.CASCADE, null=True)
    # order = models.ManyToManyField(ClosedDay, through="Order")
    close_day = models.ForeignKey(ClosedDay, on_delete=models.CASCADE, related_name="closeempitems")
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(auto_now_add=True)
    emp_name = models.CharField(max_length=150, blank=False)


class Order(models.Model):
    usermanage = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ordermanager")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orderuser")
    moduler = models.ForeignKey(ModulerUserModel, on_delete=models.CASCADE, null=True)
    close_day = models.ForeignKey(ClosedDay, on_delete=models.CASCADE)
    close_emp = models.ForeignKey(ClosedEmp, on_delete=models.CASCADE, related_name="closeordersitems")
    order_date = models.DateTimeField(auto_now_add=True)
    details = models.ManyToManyField(Products, through="OrderDetails")
    type_order = models.CharField(max_length=130)
    is_finished = models.BooleanField(default=False)
    stay = models.DecimalField(decimal_places=2, max_digits=7, blank=False, default=0)
    Payment = models.DecimalField(decimal_places=2, max_digits=7, blank=False, default=0)
    Payment_order = models.DecimalField(decimal_places=2, max_digits=7, blank=False, default=0)
    total = models.DecimalField(decimal_places=2, max_digits=7, blank=False, default=0)
    barcode = models.ImageField(upload_to="images/", blank=True, default="profile_pictures/barcode.png")
    barcode_id = models.CharField(max_length=13, null=True)

    def __str__(self):
        return "User: " + self.user.first_name + ", Order id: " + str(self.id)


# مع الدفع########barcode in defulet############
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
# Create your models here.

class OrderDetails(models.Model):
    product = models.ForeignKey(Products, on_delete=models.PROTECT, related_name="orderitems")
    # priceBuyProduct = models.ForeignKey(PriceBuyProduct, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, null=True, on_delete=models.CASCADE, related_name="orderitems")
    name = models.CharField(max_length=150, default="", blank=False)
    price = models.DecimalField(decimal_places=2, max_digits=7, blank=False)
    price_buy = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    quantity = models.DecimalField(decimal_places=2, max_digits=7, default=0.0)
    img = models.CharField(max_length=200, default="", blank=False)
    time = models.DateTimeField(auto_now_add=True)
    type_quantity = models.CharField(max_length=100, null=True)
    dec_product = models.TextField()
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return "User: " + self.order.user.first_name + "Product: " + self.product.name + ", Order id: " + str(self.order.id)
    @property
    def get_full_total_sale(self):
        total = self.quantity * self.price
        return total

    @property
    def get_puer_total_sale(self):
        total = self.quantity * self.product.price_sale
        return total

    @property
    def get_full_total_buy(self):
        total = self.quantity * self.price_buy
        return total
    class Meta:
        ordering = ['-id']


class OrderBackDetails(models.Model):
    is_finished = models.BooleanField(default=False)
    product = models.ForeignKey(Products, on_delete=models.PROTECT, related_name="orderbackproductitems")
    moduler = models.ForeignKey(ModulerUserModel, on_delete=models.CASCADE)
    # priceBuyProduct = models.ForeignKey(PriceBuyProduct, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL, related_name="orderbackitems")
    name = models.CharField(max_length=150, default="", blank=False)
    price = models.DecimalField(decimal_places=2, max_digits=7, blank=False)
    price_buy = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    quantity = models.DecimalField(decimal_places=2, max_digits=7, default=0.0)
    img = models.CharField(max_length=200, default="", blank=False)
    time = models.DateTimeField(auto_now_add=True)
    type_quantity = models.CharField(max_length=100, null=True)
    dec_product = models.TextField()
    usermanage = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orderbackmanager")
    def __str__(self):
        return "User: " + self.order.user.first_name + "Product: " + self.product.name + ", Order id: " + str(self.order.id)

# class Payment(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     shipment_address = models.CharField(max_length=150)
#     shipment_phone = models.CharField(max_length=50)
#     card_number = CardNumberField()
#     expire =
#     security_code =



