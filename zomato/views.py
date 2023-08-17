from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
from pymongo.mongo_client import MongoClient
from decouple import config
from bson import ObjectId


client = MongoClient(config("MONGO_URL"))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


dbname = client['ZomatoChronicles']

menuData = dbname['menu']

totalOrders = dbname['orders']


def dummy(request):
    menuData.insert_many(
        [
            {"name": "Margherita Pizza", "price": 250, "availability": True,
                "image": "https://img.freepik.com/free-photo/top-view-pepperoni-pizza-with-mushroom-sausages-bell-pepper-olive-corn-black-wooden_141793-2158.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
            {"name": "Pasta Alfredo", "price": 300, "availability": True,
                "image": "https://img.freepik.com/free-photo/pasta-gourmet-comida-gastronomy-yummy_1350-66.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
            {"name": "Classic Burger", "price": 200, "availability": True,
                "image": "https://img.freepik.com/free-photo/front-view-burger-stand_141793-15542.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
            {"name": "Caesar Salad", "price": 150, "availability": False,
                "image": "https://img.freepik.com/free-photo/chopped-minced-chicken-mushroom-salad-with-colorful-bell-peppers-fresh-parsley_114579-1873.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
            {"name": "Sushi Platter", "price": 350, "availability": True,
                "image": "https://img.freepik.com/free-photo/top-view-sushi-set-with-soy-sauce-chopsticks-wooden-serving-board_176474-3466.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
            {"name": "Mango Tango Smoothie", "price": 200, "availability": True,
                "image": "https://img.freepik.com/free-photo/panna-cotta-with-pineapple-slices_140725-2172.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
            {"name": "Chocolate Lava Cake", "price": 250, "availability": True,
                "image": "https://img.freepik.com/free-photo/chocolate-fondue-with-whipping-cream-mint-icecream-ball-with-red-sauce_114579-3624.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
            {"name": "Chicken Tikka Masala", "price": 350, "availability": True,
                "image": "https://img.freepik.com/free-photo/chicken-skewers-with-slices-apples-chili_2829-19997.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
        ]
    )
    menu_cursor = menuData.find({})
    menu_data = list(
        map(lambda item: {
            "id": str(item["_id"]),
            "name": item["name"],
            "price": item["price"],
            "availability": item["availability"],
            "image": item["image"]}, menu_cursor))
    return JsonResponse({"data": menu_data}, safe=False)


def home(request):
    return render(request, "zomato/index.html")


def menu(request):
    try:
        menu_curser = menuData.find({})
        zomatoMenu = list(map(lambda item: {
            "id": str(item["_id"]),
            "name": item["name"],
            "price": item["price"],
            "availability": item["availability"],
            "image": item["image"]}, menu_curser))
        context = {"menu": zomatoMenu}
        return render(request, "zomato/menu.html", context=context)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def add_dish(request):
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        image = request.POST.get("image")
        availability = request.POST.get("availability") == "on"
        dish = {"name": name, "price": price,
                "availability": availability, "image": image}
        menuData.insert_one(dish)
        return redirect("menu")
    return render(request, "zomato/add_dish.html")


def delete_dish(request, dish_id):
    dish_id = ObjectId(dish_id)
    try:
        menuData.find_one_and_delete({"_id": dish_id})
        return redirect("menu")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def update_dish(request, dish_id):
    dish_id = ObjectId(dish_id)
    item = menuData.find_one({"_id": dish_id})
    item["_id"] = str(item["_id"])
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        image = request.POST.get("image")
        availability = request.POST.get(
            "availability") == "on"  # to get the checkbox value
        updatedDish = {
            "$set": {
                "name": name,
                "price": price,
                "availability": availability,
                "image": image}
        }
        menuData.find_one_and_update({"_id": dish_id}, updatedDish)
        return redirect("menu")
    return render(request, "zomato/update_dish.html", {"dish": item})


def orders_list(request):
    try:
        orders = totalOrders.find({})
        orders = list(map(lambda item: {
            "id": str(item["_id"]),
            "customer_name": item["customer_name"],
            "dishes": item["dishes"],
            "status": item["status"],
            "total_amount": item["total_amount"]}, orders)
        )
        return render(request, "zomato/orders.html", {"orders": orders})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def process_order(request):
    menuItems = menuData.find({"availability": True})
    menuItems = list(map(lambda item: {
        "id": str(item["_id"]),
        "name": item["name"],
        "price": item["price"],
        "availability": item["availability"],
        "image": item["image"]}, menuItems)
    )
    if request.method == "POST":
        customer_name = request.POST.get("name")
        dish_ids = request.POST.getlist("selected_ids")
        total_amount = 0
        order_dishes = []
        # Check dish availability and calculate total amount
        for dish_id in dish_ids:
            dish = next(
                (item for item in menuItems if item["id"] == dish_id), None)
            if dish and dish["availability"]:
                total_amount += float(dish["price"])
                order_dishes.append(dish)
            else:
                return HttpResponse("Some items are not available please check.")

        order = {
            "customer_name": customer_name,
            "dishes": order_dishes,
            "status": "received",
            "total_amount": total_amount
        }
        totalOrders.insert_one(order)
        return redirect("orders_list")
    return render(request, "zomato/process_order.html", {"menu": menuItems})


def update_status(request, order_id):
    try:
        order_id = ObjectId(order_id)
        order = totalOrders.find_one({"_id": order_id})
        statuses = ["received", "ready for pickup", "preparing", "delivered"]
        statuses = list(filter(lambda status: status !=
                        order["status"], statuses))
        if request.method == "POST":
            if order != None:
                newStatus = request.POST.get("updated_status")
                totalOrders.find_one_and_update(
                    {"_id": order_id}, {"$set": {"status": newStatus}})
                return redirect("orders_list")
            return JsonResponse({"message": "Order not found."}, status=404)
        return render(request, "zomato/updatestatus.html", {"order": order, "statuses": statuses})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
