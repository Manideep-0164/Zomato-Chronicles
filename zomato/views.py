from django.shortcuts import render, redirect
from django.http import HttpResponse
import json

# Create your views here.

zomatoDB = {
    "menu" : [
    {"id": 1, "name": "Margherita Pizza", "price": 250, "availability": True, "image": "https://img.freepik.com/free-photo/top-view-pepperoni-pizza-with-mushroom-sausages-bell-pepper-olive-corn-black-wooden_141793-2158.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
    {"id": 2, "name": "Pasta Alfredo", "price": 300, "availability": True, "image": "https://img.freepik.com/free-photo/pasta-gourmet-comida-gastronomy-yummy_1350-66.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
    {"id": 3, "name": "Classic Burger", "price": 200, "availability": True, "image": "https://img.freepik.com/free-photo/front-view-burger-stand_141793-15542.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
    {"id": 4, "name": "Caesar Salad", "price": 150, "availability": False, "image": "https://img.freepik.com/free-photo/chopped-minced-chicken-mushroom-salad-with-colorful-bell-peppers-fresh-parsley_114579-1873.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
    {"id": 5, "name": "Sushi Platter", "price": 350, "availability": True, "image": "https://img.freepik.com/free-photo/top-view-sushi-set-with-soy-sauce-chopsticks-wooden-serving-board_176474-3466.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
    {"id": 6, "name": "Mango Tango Smoothie", "price": 200, "availability": True, "image": "https://img.freepik.com/free-photo/panna-cotta-with-pineapple-slices_140725-2172.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
    {"id": 7, "name": "Chocolate Lava Cake", "price": 250, "availability": True, "image": "https://img.freepik.com/free-photo/chocolate-fondue-with-whipping-cream-mint-icecream-ball-with-red-sauce_114579-3624.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
    {"id": 8, "name": "Chicken Tikka Masala", "price": 350, "availability": True, "image": "https://img.freepik.com/free-photo/chicken-skewers-with-slices-apples-chili_2829-19997.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
    # Add more dishes here
],
"orders":[
    {"id":1, "customer_name":"john", "dishes":[
        {"id": 1, "name": "Margherita Pizza", "price": 250, "availability": True, "image": "https://img.freepik.com/free-photo/top-view-pepperoni-pizza-with-mushroom-sausages-bell-pepper-olive-corn-black-wooden_141793-2158.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
        {"id": 3, "name": "Classic Burger", "price": 200, "availability": True, "image": "https://img.freepik.com/free-photo/front-view-burger-stand_141793-15542.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"},
        {"id": 7, "name": "Chocolate Lava Cake", "price": 250, "availability": True, "image": "https://img.freepik.com/free-photo/chocolate-fondue-with-whipping-cream-mint-icecream-ball-with-red-sauce_114579-3624.jpg?size=626&ext=jpg&ga=GA1.2.1600854318.1683615096&semt=ais"}
    ],
    "status":"received",
    "total_amount":700.0
    }
]
}


def home(request):
    return render(request, "zomato/index.html")

def menu(request):
    context = {"menu":zomatoDB["menu"]}
    # print(context)
    return render(request, "zomato/menu.html", context=context)

def add_dish(request):
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        image = request.POST.get("image")
        availability = request.POST.get("availability") == "on"
        max_id = max(dish["id"] for dish in zomatoDB["menu"])
        id = int(max_id + 1)
        dish = {"id": id, "name": name, "price": price, "availability": availability, "image": image}
        zomatoDB["menu"].append(dish)
        return redirect("menu")
    return render(request, "zomato/add_dish.html")

def delete_dish(request, dish_id):
    menuIterater = filter(lambda dish: dish["id"] != dish_id, zomatoDB["menu"])
    dishes = list(menuIterater)
    zomatoDB["menu"] = dishes
    return redirect("menu")

def update_dish(request, dish_id):
    selectedDish = None
    dishIterator = filter(lambda dish: dish["id"] == dish_id, zomatoDB["menu"])
    selectedDish = list(dishIterator)[0]
    if request.method == "POST":
        selectedDish["name"] = request.POST.get("name")
        selectedDish["price"] = request.POST.get("price")
        selectedDish["image"] = request.POST.get("image")
        selectedDish["availability"] = request.POST.get("availability") == "on"  # to get the checkbox value
        return redirect("menu")
    return render(request, "zomato/update_dish.html", {"dish":selectedDish})

def orders_list(request):
    return render(request, "zomato/orders.html", {"orders":zomatoDB["orders"]})

def process_order(request):
    if request.method == "POST":
        customer_name = request.POST.get("name")
        dish_ids = request.POST.get("ids").split(",")
        dish_ids = [int(id) for id in dish_ids]
        total_amount = 0
        order_dishes = []
        # Check dish availability and calculate total amount
        for dish_id in dish_ids:
            dish = next((item for item in zomatoDB["menu"] if item["id"] == dish_id), None)
            if dish and dish["availability"]:
                total_amount += float(dish["price"])
                order_dishes.append(dish)
            else:
                return HttpResponse("Some items are not available please check.")

        # Create a new order with a unique order ID
        order_id = len(zomatoDB["orders"]) + 1
        order = {
            "id": order_id,
            "customer_name": customer_name,
            "dishes": order_dishes,
            "status": "received",
            "total_amount":total_amount
        }
        zomatoDB["orders"].append(order)
        # print(zomatoDB["orders"])
        return redirect("orders_list")
    return render(request, "zomato/process_order.html", {"menu":json.dumps(zomatoDB["menu"])})

def update_status(request, order_id):
    orderIterator = filter(lambda customer: int(customer["id"]) == order_id, zomatoDB["orders"])
    order = next(orderIterator, None)
    statuses = ["received", "ready for pickup", "preparing", "delivered"]
    statuses = list(filter(lambda status: status != order["status"], statuses))
    if request.method == "POST":
        if order != None:
            order["status"] = request.POST.get("updated_status")
        else:
            return HttpResponse("Order not found.")
        return redirect("orders_list")
    return render(request, "zomato/updatestatus.html", {"order":order, "statuses":statuses})
