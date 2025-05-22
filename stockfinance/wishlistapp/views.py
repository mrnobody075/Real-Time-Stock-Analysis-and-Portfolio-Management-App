from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Wishlist, Stock
from .forms import WishlistForm, StockForm
import yfinance as yf
from django.core.paginator import Paginator
from django.contrib import messages

@login_required
def wishlist_list_and_create(request):
    if request.method == 'POST':
        form = WishlistForm(request.POST)
        if form.is_valid():
            wishlist = form.save(commit=False)
            wishlist.user = request.user
            wishlist.save()
            return redirect('wishlistapp:wishlist_list_and_create')  # Redirect to the same page
    else:
        form = WishlistForm()

    wishlists = request.user.wishlists.all()
    return render(request, 'wishlistapp/wishlist_list.html', {
        'wishlists': wishlists,
        'form': form,
    })
@login_required
def wishlist_delete(request, pk):
    wishlist = get_object_or_404(Wishlist, pk=pk, user=request.user)
    if request.method == "POST":
        wishlist.delete()
        return redirect('wishlistapp:wishlist_list_and_create')
    else:
        return redirect('wishlistapp:wishlist_list_and_create')  # Optional: fallback in case of a GET request


@login_required
def wishlist_detail(request, pk):
    wishlist = get_object_or_404(Wishlist, pk=pk)
    stocks = wishlist.stocks.all()
    stock_data = []
    form = StockForm()

    for stock in stocks:
        currency_symbol = ""
        current_price = "N/A"
        price_change = "N/A"
        percent_change = "N/A"

        try:
            # First try the original symbol
            ticker = yf.Ticker(stock.symbol)
            info = ticker.info
            current_price = info.get("regularMarketPrice")

            # If no price, try with .NS (NSE India) and then .BO (BSE India)
            if current_price is None and len(stock.symbol) <= 10:
                for suffix in [".NS", ".BO"]:
                    test_symbol = stock.symbol + suffix
                    test_info = yf.Ticker(test_symbol).info
                    if test_info.get("regularMarketPrice") is not None:
                        stock.symbol = test_symbol  # temporarily update
                        info = test_info
                        current_price = info.get("regularMarketPrice")
                        break  # stop if a working symbol is found

            # If still no price, mark data as not available
            if current_price is None:
                raise ValueError("Price data not available")

            previous_close = info.get("previousClose")
            price_change = current_price - previous_close if previous_close else 0
            percent_change = (price_change / previous_close) * 100 if previous_close else 0

            currency = info.get("currency", "")
            full_name = info.get("longName") or info.get("shortName") or stock.name

            CURRENCY_SYMBOLS = {
                "USD": "$", "INR": "₹", "EUR": "€", "GBP": "£", "JPY": "¥",
            }
            currency_symbol = CURRENCY_SYMBOLS.get(currency, currency)

            stock_data.append({
                "id": stock.id,
                "name": full_name,
                "symbol": stock.symbol,
                "currency": currency_symbol,
                "current_price": round(current_price, 2),
                "price_change": round(price_change, 2),
                "percent_change": round(percent_change, 2),
                "stock_data": stock_data,

            })

        except Exception:
            # On any error or if no valid symbol found
            stock_data.append({
                "id": stock.id,
                "name": stock.name,
                "symbol": stock.symbol,
                "currency": "",
                "current_price": "N/A",
                "price_change": "N/A",
                "percent_change": "N/A",
                "stock_data": stock_data,

            })

    return render(request, 'wishlistapp/wishlist_detail.html', {
        "wishlist": wishlist,
        "stock_data": stock_data,
        'form': form,

    })


@login_required
def stock_add(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)

    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.symbol = stock.symbol.upper()
            stock.name = stock.name.upper()
            stock.wishlist = wishlist

            # Check if the stock already exists in the wishlist
            if Stock.objects.filter(symbol=stock.symbol, wishlist=wishlist).exists():
                messages.error(request, f"The stock with symbol {stock.symbol} already exists in your wishlist.")
                return redirect('wishlistapp:wishlist_detail', pk=wishlist.id)

            stock.save()
            messages.success(request, f"{stock.symbol} added successfully.")
            return redirect('wishlistapp:wishlist_detail', pk=wishlist.id)
        else:
            return HttpResponse("Invalid form submission", status=400)

    return HttpResponse("This page is not accessible through a GET request.", status=405)

@login_required
def stock_delete(request, stock_id, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    stock = get_object_or_404(Stock, id=stock_id, wishlist=wishlist)
    stock.delete()
    return redirect('wishlistapp:wishlist_detail', pk=wishlist.id)

@login_required
def wishlist_delete(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    wishlist.delete()
    return redirect('wishlistapp:wishlist_list_and_create')  # update with correct namespace
