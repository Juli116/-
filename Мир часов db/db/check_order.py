def check_order(variant, quantity, stock):
    if variant is None:
        return "Ошибка: выберите вариант исполнения"
    if quantity <= 0:
        return "Ошибка: количество должно быть больше 0"
    if quantity > stock:
        return "Ошибка: недостаточно товара на складе"
    return "OK"
