from django.urls import path
from .views import modulers, addmoduler, localdata

urlpatterns = [
    # path("add-cart/", add_to_cart, name="add-cart"),
    # path("cart/", Cart.as_view(), name="cart"),
    path("modulers/", modulers, name="modulers"),
    path("addmoduler<int:modu>", addmoduler, name="addmoduler"),
    path("localdata/", localdata, name="localdata"),
    # path("backproduct/", backproduct, name="backproduct"),
    # path("closebackorder/", closebackorder, name="closebackorder"),

]