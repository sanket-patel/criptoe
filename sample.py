import gdax, time

def main():

    public_client = gdax.PublicClient()

    product = 'ETH-USD'
    order_book = public_client.get_product_order_book(product)
    product_trades = public_client.get_product_trades(product_id=product)
    historic_rates = public_client.get_product_historic_rates(product)
    product_24h_stats = public_client.get_product_24hr_stats(product)

    keys = ['trade_id', 'size', 'side', 'price', 'time']

    for trade in product_trades:
        print '\t'.join([str(trade[key]) for key in keys])


if __name__ == '__main__':
    main()