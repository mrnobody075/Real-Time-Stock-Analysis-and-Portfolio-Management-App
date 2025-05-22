from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Wishlist, Stock
from .forms import WishlistForm
import yfinance as yf
from django.core.paginator import Paginator

@login_required
def wishlist_list(request):
    wishlists = request.user.wishlists.all()
    return render(request, 'wishlistapp/wishlist_list.html', {'wishlists': wishlists})

@login_required
def wishlist_create(request):
    if request.method == 'POST':
        form = WishlistForm(request.POST)
        if form.is_valid():
            wishlist = form.save(commit=False)
            wishlist.user = request.user
            wishlist.save()
            return redirect('wishlist_list')
    else:
        form = WishlistForm()
    return render(request, 'wishlistapp/wishlist_form.html', {'form': form})

@login_required
def wishlist_detail(request, pk):
    wishlist = get_object_or_404(Wishlist, pk=pk)
    all_wishlists = Wishlist.objects.all().order_by("name")

    # Paginate the wishlist list
    paginator = Paginator(all_wishlists, 5)  # Show 5 wishlists per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    wishlist = get_object_or_404(Wishlist, pk=pk, user=request.user)
    stocks = wishlist.stocks.all()
    stock_data = []

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
            if current_price is None and len(stock.symbol) <= 5:
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
                "wishlist": wishlist,
                "stock_data": stock_data,
                "page_obj": page_obj,
                "all_wishlists": all_wishlists
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
                "wishlist": wishlist,
                "stock_data": stock_data,
                "page_obj": page_obj,
                "all_wishlists": all_wishlists
            })

    return render(request, 'wishlistapp/wishlist_detail.html', {
        "wishlist": wishlist,
        "stock_data": stock_data
    })

@login_required
def stock_add(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)

    if request.method == 'POST':
        stock_name = request.POST.get('name')
        stock_symbol = request.POST.get('symbol')

        if not stock_name or not stock_symbol:
            return render(request, 'wishlistapp/stock_form.html', {
                'wishlist': wishlist,
                'error': 'Both name and symbol are required.'
            })

        stock = Stock(name=stock_name.upper(), symbol=stock_symbol.upper(), wishlist=wishlist)
        stock.save()
        return redirect('wishlist_detail', pk=wishlist.id)

    return render(request, 'wishlistapp/stock_form.html', {'wishlist': wishlist})

@login_required
def stock_delete(request, stock_id, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    stock = get_object_or_404(Stock, id=stock_id, wishlist=wishlist)
    stock.delete()
    return redirect('wishlist_detail', pk=wishlist.id)
