from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import reverse
from django.template.defaultfilters import slugify

User = get_user_model()


class Address(models.Model):
    ADDRESS_CHOICES = (
        ("B", "Billing"),
        ("S", "Shipping"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=150)
    address_line_2 = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.address_line_1}, {self.address_line_2}, {self.city}, {self.zip_code}"

    class Meta:
        verbose_name_plural = "Addresses"


class ColourVariation(models.Model):
    name = models.CharField(max_length=50)

    # class Meta:
    #     verbose_name = ""
    #     verbose_name_plural = ""

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse("_detail", kwargs={"pk": self.pk})


class SizeVariation(models.Model):
    name = models.CharField(max_length=50)

    # class Meta:
    #     verbose_name = ""
    #     verbose_name_plural = ""

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse("_detail", kwargs={"pk": self.pk})


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # slug = models.SlugField(unique=True, blank=True, null=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category-detail", kwargs={"slug": self.slug})

    # def save(self, *args, **kwargs):
    #     to_assign = slugify(self.name)

    #     if Category.objects.filter(slug=to_assign).count() < 2:
    #         self.slug = to_assign
    #     to_assign = to_assign + str(Category.objects.all().count())
    #     super().save(*args, **kwargs)


class Product(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True, null=True)
    primary_category = models.ForeignKey(
        Category, related_name="primary_products", on_delete=models.CASCADE
    )
    secondary_category = models.ManyToManyField(Category, blank=True)
    image = models.ImageField(upload_to="product_images")
    description = models.TextField()
    price = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)
    available_colours = models.ManyToManyField(ColourVariation)
    available_sizes = models.ManyToManyField(SizeVariation)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("cart:product-detail", kwargs={"slug": self.slug})

    def get_update_url(self):
        return reverse("staff:product-update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse("staff:product-delete", kwargs={"pk": self.pk})

    def get_price(self):
        return "{:.2f}".format(self.price / 100)

    def save(self, *args, **kwargs):
        to_assign = slugify(self.title)

        if Product.objects.filter(slug=to_assign).count() < 2:
            self.slug = to_assign
        to_assign = to_assign + str(Product.objects.all().count())
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey("Order", related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.ForeignKey)
    quantity = models.PositiveIntegerField(default=1)
    colour = models.ForeignKey(ColourVariation, on_delete=models.CASCADE)
    size = models.ForeignKey(SizeVariation, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

    def get_raw_total_item_price(self):
        return self.quantity * self.product.price

    def get_total_item_price(self):
        price = self.get_raw_total_item_price()  # 1000
        return "{:.2f}".format(price / 100)


class Order(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)

    billing_address = models.ForeignKey(
        Address,
        related_name="billing_address",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    shipping_address = models.ForeignKey(
        Address,
        related_name="shipping_address",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.reference_number

    @property
    def reference_number(self):
        return f"ORDER-{self.pk}"

    def get_raw_subtotal(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_raw_total_item_price()
        return total

    def get_subtotal(self):
        subtotal = self.get_raw_subtotal()
        return "{:.2f}".format(subtotal / 100)

    def get_raw_total(self):
        subtotal = self.get_raw_subtotal()
        # add tax, add delivery, subtract discounts
        # total = subtotal - discounts + tax + delivery
        return subtotal

    def get_total(self):
        subtotal = self.get_raw_subtotal()
        return "{:.2f}".format(subtotal / 100)


class Payment(models.Model):
    order = models.ForeignKey(Order, related_name="payments", on_delete=models.CASCADE)
    payment_method = models.CharField(
        max_length=20,
        choices=(("PayPal", "PayPal"),),
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)
    amount = models.FloatField()
    raw_response = models.TextField()

    def __str__(self):
        return self.reference_number

    @property
    def reference_number(self):
        return f"PAYMENT-{self.order}-{self.pk}"

    class Meta:
        verbose_name_plural = "Payments"

    # def get_absolute_url(self):
    #     return reverse("_detail", kwargs={"pk": self.pk})
