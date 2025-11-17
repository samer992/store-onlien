
from barcode.writer import ImageWriter
from io import BytesIO
import barcode
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.core.files import File
from django.shortcuts import render, get_object_or_404
from rest_framework import status
# from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from accounts.models import *
from accounts.serializers import ProfileSerializer
from clients.views import clientOrder
from mandob.views import mntgat_mandob
from moduler.models import ModulerUserModel
from .serializers import ProductsSerializer, CatgoryProductTypeSerializer, OrderSerializer, OrderBackDetailsSerializer, \
    ClosedDaySerializer
from rest_framework.response import Response
from .models import Products, PriceBuyProduct, CatgoryProductType, Order, OrderDetails, ClosedEmp, ClosedDay, OrderBackDetails
from rest_framework.parsers import MultiPartParser, FormParser
import random
# Create your views here.
################### ==> Products <== ###################
class productsView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductsSerializer
    # parsers_classes = [MultiPartParser, FormParser]
    print("xxxxxxxxxxxxxxxxxxxxxxxxxx")

    # @swagger_auto_schema(operation_summary="Get all Orders")
    def post(self, request, format=None):

        if request.user.manager:
            use = request.user.manageid
            user_man = User.objects.get(id=use)
            product_data = request.data
            print(request.data["barcode_id"])
            data = request.data.copy()
            if data["barcode_id"]:
                print("ok")
            else:
                contary_code = 6
                segl_tgary = 123456
                id_pro = random.randint(11111, 99999)
                data["barcode_id"] = f"{contary_code}{segl_tgary}{id_pro}"
                print('not ok')
                # print(number)
            # print(request.data["id_pro"])
            userman = UserManage.objects.get(user=user_man)
            moduler = ModulerUserModel.objects.get(usermanage=userman, id=product_data["moduler"])
            products = Products.objects.all().filter(usermanage=user_man, moduler=moduler)
            # print(len(products))

            if len(products) < moduler.num_products:
                produc = Products.objects.all().filter(usermanage=user_man, barcode_id=product_data["barcode_id"], moduler=moduler)
                if produc:
                    print(produc)
                    print(product_data)
                    old_product = Products.objects.get(usermanage=user_man, id=produc[0].id, barcode_id=product_data["barcode_id"], moduler=moduler)
                    if product_data["product_picture"]:
                        old_product.product_picture = product_data["product_picture"]
                        print(product_data["product_picture"])

                    if product_data["name"] != "undefined" and product_data["name"] != old_product.name and product_data["name"] != "":
                        old_product.name = product_data["name"]
                        print(product_data["name"])

                    if product_data["description"] != "undefined" and product_data["description"] != old_product.description and product_data["description"] != "":
                        old_product.description = product_data["description"]
                        print(product_data["description"])

                    if product_data["price_sale"] != "undefined" and float(product_data["price_sale"]) != old_product.price_sale and product_data["price_sale"] != "":
                        old_product.price_sale = product_data["price_sale"]
                        print(product_data["price_sale"])

                    if product_data["is_active"] != str(old_product.is_active):
                        old_product.is_active = product_data["is_active"]
                        print(product_data["is_active"])

                    if product_data["quantity"] != "" and product_data["price_buy"] != "" and product_data["quantity"] != "undefined" and product_data["price_buy"] != "undefined" :
                        price_BuyProduct = PriceBuyProduct.objects.all().filter(product=old_product, price_buy=product_data["price_buy"])
                        total_quantity = float(old_product.total_quantity) + float(product_data["quantity"])
                        print(product_data["quantity"])
                        if price_BuyProduct:
                            old_price_BuyProduct = PriceBuyProduct.objects.get(product=old_product, price_buy=product_data["price_buy"])
                            quantity = float(old_price_BuyProduct.quantity) + float(product_data["quantity"])
                            print(old_product)
                            old_price_BuyProduct.quantity = quantity
                            old_price_BuyProduct.quantity_total = quantity
                            old_price_BuyProduct.total_buy = float(quantity)*float(product_data["price_buy"])
                            old_price_BuyProduct.is_finished = False
                            old_price_BuyProduct.save()
                            print(price_BuyProduct)
                            print("فيه سعر منتج قديم")
                        else:
                            priceBuyProduct = PriceBuyProduct.objects.create(
                                product=old_product,
                                quantity=product_data["quantity"],
                                quantity_total=product_data["quantity"],
                                price_buy=product_data["price_buy"],
                                total_buy=float(product_data["quantity"])*float(product_data["price_buy"]),
                            )
                            priceBuyProduct.save()
                            print(" سعر منتج جديد")

                        old_product.total_quantity = total_quantity
                        old_product.total_sale = float(product_data["price_sale"])*total_quantity

                    old_product.save()

                    print("فيه منتج قديم")

                else:
                    print("منتج جديد")
                    # print(os.getcwd())
                    # print(settings.MEDIA_ROOT)

                    options = {
                        'format': 'PNG',
                        'font_size': 20,
                        'text_distance': 2.0,
                    }
                    xxx = barcode.get_barcode_class("code128")
                    xcv = xxx(data["barcode_id"], writer=ImageWriter().set_options(options=options))
                    buffer = BytesIO()
                    xcv.write(buffer)
                    # print(File(buffer).read)
                    path_fol = settings.MEDIA_ROOT + "/images/"
                    print(path_fol)

                    xcv.save(path_fol+product_data['name'], File(buffer))
                    # print(product_data["product_picture"])

                    pro = Products()
                    pro.user = request.user
                    pro.name = product_data["name"]
                    pro.description = product_data["description"]
                    pro.price_sale = product_data["price_sale"]
                    pro.barcode_id = xcv #str(my_code)
                    pro.total_quantity = product_data["quantity"]
                    pro.quantity_box = product_data["quantity_box"]
                    pro.type = product_data["type"]
                    pro.product_picture = product_data["product_picture"]
                    pro.is_active = product_data["is_active"]
                    pro.barcode = f"images/{product_data['name']}.svg"
                    pro.total_sale = float(product_data["price_sale"])*float(product_data["quantity"])
                    pro.type_id = product_data["type_id"]
                    pro.type_quantity = product_data["type_quantity"]
                    pro.moduler = moduler
                    pro.usermanage = user_man

                    pro.save()
                    priceBuyProduct = PriceBuyProduct.objects.create(
                        product=pro,
                        quantity=product_data["quantity"],
                        quantity_total=product_data["quantity"],
                        price_buy=float(product_data["price_buy"]),
                        total_buy=float(product_data["quantity"]) * float(product_data["price_buy"]),
                    )
                    priceBuyProduct.save()
                return Response({
                    'data': "product",
                    'message': f"تم اضافه {request.data['name']} بنجاح",
                    "status": "Your account regestrathion susccessfuly"
                }, status=status.HTTP_201_CREATED)
            else:
                # print(len(products))
                return Response({
                    'data': "المنتجات خلصت زود منتجات",
                    'message': f"لم يتم اضافه {request.data['name']} ",
                }, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"data": "انته مش مدير"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            use = request.user.manageid
            user_man = User.objects.get(id=use)
        #     pro = Products.objects.filter(usermanage=user_man)
        # else:
        pro = Products.objects.filter(usermanage=user_man, moduler=request.GET["moduler"])

        # product_data = request.data

        serializer = self.serializer_class(instance=pro, many=True)
        # if serializer.is_valid(raise_exception=True):
            # serializer.save()
        product = serializer.data
        # print(product)

        return Response({"data": product}, status=status.HTTP_200_OK)
        # return Response({product})



class CatgoryProductTypeViw(GenericAPIView):
    print("saaaaaaaaaaammm")
    permission_classes = [IsAuthenticated]
    serializer_class = CatgoryProductTypeSerializer

    def post(self, request):
        print(request.data)
        if request.user.is_authenticated:
            use = request.user.manageid
            user_man = User.objects.get(id=use)
            # print(user_man)
            manage = UserManage.objects.get(user=user_man)
            moduler_user = ModulerUserModel.objects.get(usermanage=manage, id=request.data["moduler"])
            catgoryproduct = CatgoryProductType.objects.create(
                user=request.user,
                name=request.data["name"],
                moduler=moduler_user,
            )
            catgoryproduct.save()

        print("request poooooooooooooost")
        return Response({"data": "تم الأضافه بنجاح"}, status=status.HTTP_201_CREATED)

    def get(self, request):
        print(request.user)
        user = request.user
        if user.manager:
            user_man=user
            # print(user)
        else:
            # print(user)
            user = user.manageid
            user_man = User.objects.get(id=user)
        manage = UserManage.objects.get(user=user_man)
        print(request.GET["moduler"])
        moduler_user = ModulerUserModel.objects.get(usermanage=manage, id=request.GET["moduler"])
        catgory = CatgoryProductType.objects.filter(user=user_man, moduler=moduler_user)

        serializer = self.serializer_class(instance=catgory, many=True)

        catgoryproduct = serializer.data
        print("request geeeeeeeeeeeeeeeeet")

        return Response({"data": catgoryproduct}, status=status.HTTP_200_OK)

    def delete(self, request):
        print(request.GET["id"])
        # print(id)
        catgoryProductType = get_object_or_404(CatgoryProductType, id=request.GET["id"])
        # print(product_2.user)
        # product = get_object_or_404(User, id=product_2.user_id)
        # print(product)

        #
        # if product.user != request.user:
        #     return Response({"error": "Sorry you can not update this product"}
        #                     , status=status.HTTP_403_FORBIDDEN)
        #
        catgoryProductType.delete()
        # product_2.delete()
        return Response({"details": "Delete action is done"}, status=status.HTTP_200_OK)


#################### ==> Orders <== ####################
# from rest_framework.authtoken.models import Token
class Cart(GenericAPIView):
    permission_classes = [IsAuthenticated]
    ########################post tb3on al cart#####################
    # [
    #     {
    #         "barcode_id": "111111111111",
    #         "Payment": "100",
    #         "moduler": 1,
    #         "product": [
    #             {
    #                 "quantity": 3,
    #                 "barcode_pro": "620240432617"
    #             },
    #             {
    #                 "quantity": 50,
    #                 "barcode_pro": "620240462955"
    #             }
    #         ]
    #
    #     }
    # ]
    def checkOrder(self, req, man, use, closedE, closeD, mang):
        for order_request in req:
            print(order_request["moduler"])
            print(mang)
            moduler_user = ModulerUserModel.objects.get(usermanage=mang, id=order_request["moduler"])
            order_request_barcode = order_request["barcode_id"]
            order_request_payment = float(order_request["Payment"])
            order_request_orderItems = order_request["orderItems"]

            order_total = []
            for request_orderItem in order_request_orderItems:
                order_request_orderItem_price = float(request_orderItem["price"])
                order_request_orderItem_quantity = float(request_orderItem["quantity"])
                order_total.append(order_request_orderItem_quantity*order_request_orderItem_price)

            new_order = Order()
            new_order.user = use
            new_order.usermanage = man
            new_order.order_date = datetime.datetime.now()
            new_order.is_finished = True
            new_order.barcode_id = order_request_barcode
            new_order.close_emp = closedE
            new_order.close_day = closeD
            total = sum(order_total)
            stay = order_request_payment - float(sum(order_total))
            new_order.total = total
            new_order.stay = stay
            new_order.moduler = moduler_user
            new_order.Payment = order_request_payment
            print(f"xxxxxxTOTALxxxxxx: {total}")
            print(f"xxxxxxSTAYxxxxxxx: {stay}")




            for order_request_orderItem in order_request_orderItems:
                order_request_orderItem_barcode = order_request_orderItem["product"]
                order_request_orderItem_price = float(order_request_orderItem["price"])
                order_request_orderItem_quantity = float(order_request_orderItem["quantity"])
                order_total.append(order_request_orderItem_quantity*order_request_orderItem_price)


                product = Products.objects.get(barcode_id=order_request_orderItem_barcode)

                Price_Buy_Products = PriceBuyProduct.objects.all().filter(product=product, is_finished=False)

                total_quantity_price_Buy = 0
                for price_Buy_Product in Price_Buy_Products:
                    total_quantity_price_Buy += price_Buy_Product.quantity

                if order_request_orderItem_quantity <= total_quantity_price_Buy:

                    print(f"order_request_orderItem_quantity ==> {order_request_orderItem_quantity}")
                    print(f"total_quantity_price_Buy_Product ==> {total_quantity_price_Buy}")
                    if order_request_orderItem_quantity != 0:
                        # new_order.save()
                        for price_Buy_Product_InQty in Price_Buy_Products:
                            price_Buy_Product_qty = float(price_Buy_Product_InQty.quantity)
                            print(price_Buy_Product_InQty.quantity)


                            if order_request_orderItem_quantity <= price_Buy_Product_InQty.quantity:
                                price_Buy_Product_qty -= order_request_orderItem_quantity

                                quantity_to_order_details = order_request_orderItem_quantity
                                order_request_orderItem_quantity = 0
                                print(f"<= {price_Buy_Product_qty}")
                            else:
                                order_request_orderItem_quantity -= price_Buy_Product_qty
                                print(f"> {order_request_orderItem_quantity}")

                                quantity_to_order_details = price_Buy_Product_qty


                    else:
                        return Response(f" {product}ادخل كميه",
                                        status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response(f"الكميه {product} غير كافيه باقى {total_quantity_price_Buy}", status=status.HTTP_400_BAD_REQUEST)


            print("saaaaaaaaaaam")
            return Response(status=status.HTTP_200_OK)


    def post(self, request):
        print(request.data)

        user = request.user

        if user.emp:
            user_man = User.objects.get(id=user.manageid)
            # print("its emp")
        else:
            use = request.user.manageid
            user_man = User.objects.get(id=use)
        # print(user_man)
        manage = UserManage.objects.get(user=user_man)
        print(request.data[0]["moduler"])
        print(manage)
        moduler = ModulerUserModel.objects.get(usermanage=manage, id=request.data[0]["moduler"])

        if not ClosedDay.objects.filter(usermanage=user_man, is_finished=False, moduler=moduler).exists():
            closeDay = ClosedDay()
            closeDay.usermanage = user_man
            closeDay.moduler = moduler
            closeDay.save()

        else:
            closeDay = ClosedDay.objects.get(usermanage=user_man, is_finished=False, moduler=moduler)


        if not ClosedEmp.objects.filter(user=user, is_finished=False, moduler=moduler).exists():
            print(closeDay)
            closedEmp = ClosedEmp()
            closedEmp.usermanage = user_man
            closedEmp.user = request.user
            closedEmp.emp_name = request.user.get_full_name
            closedEmp.close_day = closeDay
            closedEmp.moduler = moduler
            closedEmp.save()
            # print(closedEmp)
            print("wwwwwwwwwwwwwwwwwwwwwwwwwww")
        else:
            closedEmp = ClosedEmp.objects.get(user=user, is_finished=False, moduler=moduler)
            # print(closeDay)
            # print(closedEmp)
            print("nnnnnnnnnnnnnnnnnnnnnnnn")
        print(self.checkOrder(request.data, user_man, request.user, closedEmp, closeDay, manage).data)
        if self.checkOrder(request.data, user_man, request.user, closedEmp, closeDay, manage).status_code == 200:
            for order_request in request.data:
                moduler_user = ModulerUserModel.objects.get(usermanage=manage, id=order_request["moduler"])
                order_request_barcode = order_request["barcode_id"]
                order_request_payment = float(order_request["Payment"])
                order_request_orderItems = order_request["orderItems"]

                # print(order_request_barcode)
                # print(order_request_payment)
                # print("orders_items_request")
                order_total = []
                for request_orderItem in order_request_orderItems:
                    order_request_orderItem_price = float(request_orderItem["price"])
                    order_request_orderItem_quantity = float(request_orderItem["quantity"])
                    order_total.append(order_request_orderItem_quantity*order_request_orderItem_price)

                if order_request["type_order"] == "clints":
                    if order_request["is_agel"]:
                        print("yes")
                        print(order_request_payment)

                        Payment_order = order_request_payment

                    else:
                        print("nooooooooooo")
                        print(sum(order_total))
                        Payment_order = sum(order_total)

                if order_request["type_order"] == "cash":
                    print(sum(order_total))
                    Payment_order = sum(order_total)

                if order_request["type_order"] == "mandob":
                    print(order_request_payment)
                    Payment_order = order_request_payment

                new_order = Order()
                new_order.user = request.user
                new_order.usermanage = user_man
                new_order.order_date = datetime.datetime.now()
                new_order.is_finished = True
                new_order.barcode_id = order_request_barcode
                new_order.close_emp = closedEmp
                new_order.close_day = closeDay
                total = sum(order_total)
                stay = order_request_payment - float(sum(order_total))
                new_order.total = total
                new_order.stay = stay
                new_order.moduler = moduler_user
                new_order.Payment = order_request_payment
                new_order.type_order = order_request["type_order"]
                new_order.Payment_order = Payment_order
                print(f"xxxxxxTOTALxxxxxx: {total}")
                print(f"xxxxxxSTAYxxxxxxx: {stay}")
                pro_det = []




                for order_request_orderItem in order_request_orderItems:
                    order_request_orderItem_barcode = order_request_orderItem["product"]
                    order_request_orderItem_price = float(order_request_orderItem["price"])
                    order_request_orderItem_quantity = float(order_request_orderItem["quantity"])
                    order_total.append(order_request_orderItem_quantity*order_request_orderItem_price)
                    # print(order_request_orderItem_barcode)
                    # print(order_request_orderItem_price)

                    product = Products.objects.get(barcode_id=order_request_orderItem_barcode)

                    Price_Buy_Products = PriceBuyProduct.objects.all().filter(product=product, is_finished=False)
                    # print("Price_Buy_Products################################")
                    total_quantity_price_Buy = 0
                    pro_det = []
                    for price_Buy_Product in Price_Buy_Products:
                        total_quantity_price_Buy += price_Buy_Product.quantity

                    if order_request_orderItem_quantity <= total_quantity_price_Buy:

                        print(f"order_request_orderItem_quantity ==> {order_request_orderItem_quantity}")
                        print(f"total_quantity_price_Buy_Product ==> {total_quantity_price_Buy}")
                        if order_request_orderItem_quantity != 0:
                            new_order.save()
                            for price_Buy_Product_InQty in Price_Buy_Products:
                                price_Buy_Product_qty = float(price_Buy_Product_InQty.quantity)
                                print(price_Buy_Product_InQty.quantity)


                                if order_request_orderItem_quantity < price_Buy_Product_InQty.quantity:
                                    price_Buy_Product_qty -= order_request_orderItem_quantity
                                    price_Buy_Product_InQty.quantity = price_Buy_Product_qty
                                    price_Buy_Product_InQty.save()
                                    quantity_to_order_details = order_request_orderItem_quantity

                                    order_request_orderItem_quantity = 0

                                    print(f"<= {price_Buy_Product_qty}")
                                else:
                                    order_request_orderItem_quantity -= price_Buy_Product_qty
                                    # pro_det.append({
                                    #     "quantity": order_request_orderItem_quantity,
                                    #     "price_buy": price_Buy_Product_InQty.price_buy
                                    # })
                                    print(f"> {order_request_orderItem_quantity}")
                                    price_Buy_Product_InQty.quantity = 0
                                    price_Buy_Product_InQty.is_finished = True
                                    price_Buy_Product_InQty.save()
                                    quantity_to_order_details = price_Buy_Product_qty
                                pro_det.append({
                                    "quantity": quantity_to_order_details,
                                    "price_buy": price_Buy_Product_InQty.price_buy
                                })

                                order_details = OrderDetails.objects.create(
                                    product=product,
                                    order=new_order,
                                    name=product.name,
                                    img=product.product_picture,
                                    price=order_request_orderItem_price,
                                    quantity=quantity_to_order_details,
                                    price_buy=price_Buy_Product_InQty.price_buy,
                                    dec_product=product.description,
                                    type_quantity=product.type_quantity,
                                )
                                order_details.save()

                        else:
                            return Response(f" {product}ادخل كميه",
                                            status=status.HTTP_400_BAD_REQUEST)

                    else:
                        return Response(f"الكميه {product} غير كافيه باقى {total_quantity_price_Buy}", status=status.HTTP_400_BAD_REQUEST)
                    break


                print("saaaaaaaaaaam")
                if order_request["type_order"] == "mandob":
                    print("in functhion mntgat_mandob")
                    print(pro_det)
                    mntgat_mandob(order_request_orderItem_barcode, user_man, moduler_user, order_request["emp_id"], request.user, pro_det, order_request_orderItem["quantity"])

                if order_request["type_order"] == "clints":
                    print("in functhion client")
                    print(pro_det)
                    clientOrder(request.data, user_man, request.user, order_request["emp_id"], closeDay, manage)
                    # order_client(order_request_orderItem_barcode, user_man, moduler_user, order_request["emp_id"], request.user, pro_det, order_request_orderItem["quantity"])



                serializer = OrderSerializer(instance=new_order)
                print(serializer.data)
            return Response("تمت عمليه الدفع", status=status.HTTP_201_CREATED)
        else:
            return Response(self.checkOrder(request.data, user_man, request.user, closedEmp, closeDay, manage).data, status=status.HTTP_400_BAD_REQUEST)

##################################################################################
    def get(self, request):
        user = request.user
        print(user)
        print(request.GET["order_barcode"])

        if user.emp:
            user_man = User.objects.get(id=user.manageid)
            print("its emp")
        else:
            user_man = request.user.manageid
        print(user_man)


        ordr = Order.objects.filter(barcode_id=request.GET["order_barcode"], usermanage=user.manageid, moduler=request.GET["moduler"])
        if ordr:
            order = Order.objects.get(barcode_id=request.GET["order_barcode"])
            user_order = User.objects.get(id=order.user_id)

            serializer = OrderSerializer(instance=order)

            return Response({"order": serializer.data, "user_order": user_order.get_full_name}, status=status.HTTP_200_OK)
        else:
            return Response("لا يوجد فاتوره", status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
# @authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def orderDay(request):
    user = request.user
    if user.emp:
        user_man = User.objects.get(id=user.manageid)
        # print("its emp")
    else:
        user_man = request.user
    print(user)
    closeDay = ClosedDay.objects.get(usermanage=user_man, is_finished=False, moduler=request.GET["moduler"])
    orders = Order.objects.filter(usermanage=user_man, is_finished=True, moduler=request.GET["moduler"], close_day=closeDay)

    name_order = []
    for order in orders:
        # print(order.order_date)

        user_order = User.objects.get(id=order.user_id)
        name_order.append(user_order.get_full_name)
        # print(user_order.get_full_name)
    serializer = OrderSerializer(instance=orders, many=True)


    # print(serializer.data["ordermanager"])
    return Response({"data": serializer.data, "user_order": name_order}, status=status.HTTP_200_OK)


@api_view(['POST'])
# @authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def backorder(request):
    user = request.user
    print(request.data["id_order"])
    print(request.data["orderItemsListEdit"])# امان ميرحوش فاضى يعمل error
    if user.emp:
        user_man = User.objects.get(id=user.manageid)
        # print("its emp")
    else:
        user_man = request.user
    orders = Order.objects.filter(usermanage=user_man, id=request.data["id_order"])
    # print(orders)
    if orders:

        for i in request.data["orderItemsListEdit"]:
            print(i["orderItems_id"])

            order_detl = OrderDetails.objects.get(id=i["orderItems_id"], order=request.data["id_order"])
            xx = float(order_detl.quantity) - i["quantity"]
            print(xx)
            order_detl.quantity = xx
            if xx == 0:
                order_detl.is_finished = True


            order_detl.save()
        # print(order_detl)
            order = orders[0]
            orderbackdetails = OrderBackDetails.objects.create(
                product=order_detl.product,
                order=order,
                name=order_detl.name,
                img=order_detl.img,
                price=order_detl.price,
                quantity=i["quantity"],
                price_buy=order_detl.price_buy,
                dec_product=order_detl.dec_product,
                type_quantity=order_detl.type_quantity,
                usermanage=order.usermanage,
                moduler=order.moduler,
            )
            orderbackdetails.save()
        # print(orderbackdetails)
        orderdetails = OrderDetails.objects.filter(order=order, is_finished=False)
        print(order)
        print(orderdetails)
        total_order = 0
        if orderdetails:
            for orderdetail in orderdetails:
                total_order += orderdetail.quantity*orderdetail.price
            print(total_order)
            order.total = total_order
            order.Payment_order = total_order

            order.save()
        else:
            order.delete()

    else:
        print("noooooooooooo order hnaaaaaaaaaaaa")

    return Response({"data"}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
# @authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def backproduct(request):
    user = request.user
    if user.emp:
        user_man = User.objects.get(id=user.manageid)
        # print("its emp")
    else:
        user_man = request.user
    print(user)
    orders = OrderBackDetails.objects.filter(usermanage=user_man, is_finished=False, moduler=request.GET["moduler"])

    serializer = OrderBackDetailsSerializer(instance=orders, many=True)


    # print(serializer.data["ordermanager"])
    return Response({"data": serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
# @authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def closebackorder(request):
    print(request.data["id"])
    orderBackDetails = OrderBackDetails.objects.get(usermanage=request.user, is_finished=False, id=request.data["id"])
    orderBackDetails.is_finished = True
    orderBackDetails.save()
    return Response({"data": "تمت العمليه بنجاح"}, status=status.HTTP_200_OK)


# accounting############################3
class AccountingView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.manager:
            if ClosedDay.objects.filter(usermanage=user, is_finished=False, moduler=request.GET["moduler"]).exists():
                closeDay = ClosedDay.objects.filter(usermanage=user, is_finished=False, moduler=request.GET["moduler"])

                serializer = ClosedDaySerializer(closeDay, many=True)
                # print(serializer.data[0])

                return Response({"close_day_info": serializer.data[0]})
            else:
                print("store")
                return Response({"close_day_info": []},status=status.HTTP_404_NOT_FOUND)
            # return Response({"msg": "no data closeDay", "totalall": float(0)})

@api_view(['POST'])
# @authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def close_emp(request):
    user = request.user
    idemp = request.data["idemp"]
    print(idemp)
    print(user)
    closeDay = ClosedDay.objects.get(usermanage=user, is_finished=False, moduler=request.data["moduler"])
    closeemp = ClosedEmp.objects.get(id=idemp, is_finished=False, usermanage=user, moduler=request.data["moduler"])

    order = Order.objects.all().filter(close_emp=closeemp, close_day=closeDay, is_finished=False, moduler=request.data["moduler"])
    if order:
        print("فواتير مفتوحه")


        return Response({"mesg": f"فاتوره رقم {order[0].barcode_id} مفتوحه"})
    else:
        closeemp.is_finished = True
        closeemp.save()
        print(closeemp)
        print("##########################################")

        print("فواتير clossssssssssssssssssse")
        return Response({"mesg": "تم بنجاح"})


@api_view(['POST'])
# @authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def close_day(request):
    user = request.user
    idday = request.data["idday"]
    print(idday)
    print(user)
    close_day = ClosedDay.objects.get(id=idday, usermanage=user, is_finished=False, moduler=request.data["moduler"])
    casher = ClosedEmp.objects.all().filter(usermanage=user, is_finished=False, moduler=request.data["moduler"])
    # buyManager = BuyManager.objects.all().filter(user=user, close_day=close_day, is_finished=False)


    if casher:
        print(casher)
        for i in casher:
            print(i.emp_name)
        return Response({"mesg": f"{i.emp_name} مش مقفل "},status=status.HTTP_400_BAD_REQUEST)
    else:
        close_day.is_finished = True
        close_day.save()
        # for msrof in buyManager:
        #     msrof.is_finished = True
        #     msrof.save()
        print("كله مقفل ")
    print(close_day)


    return Response({"mesg": "تم بنجاح الفنش الكبير الاول والاخير"})


@api_view(['GET'])
# @authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def close_day_accounting(request):
    user = request.user
    # idday = request.data["idday"]
    print(user)
    if user.manager:
        closeDay = ClosedDay.objects.all().filter(usermanage=user, moduler=request.GET["moduler"])
        serializer = ClosedDaySerializer(instance=closeDay, many=True)
        print(closeDay)
        if closeDay:

            return Response({"close_day_info": serializer.data})
        else:
            return Response({"close_day_info": []},status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"report_product": "انته مش مدير"})
