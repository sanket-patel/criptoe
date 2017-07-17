import gdax
import datetime as dt

class historic_data(gdax.PublicClient):

    def daterange(self, start_date, end_date):
        for n in range(int ((end_date - start_date).days + 1)):
            yield start_date + dt.timedelta(days=n)

    def interday_data(self, start_date, end_date, product, output):
        # NOTE: these dates are inclusive
        start = dt.datetime.strptime(start_date, '%Y-%m-%d')    # start
        end = dt.datetime.strptime(end_date, '%Y-%m-%d')        # end

        with open(output, 'a') as f:
            f.write('time,low,high,open,close,volume\n')            # titles

        for d in self.daterange(start, end):
            data = self.get_product_historic_rates(product, d.isoformat(), \
            (d + dt.timedelta(days=1)).isoformat(), '300')
            print(d)
            with open(output, 'a') as f:
                data = [[str((dt.datetime(1970, 1, 1, 0, 0, 0) + dt.timedelta(seconds=row[0])))] + \
                        [str(item) for item in row[1:]] for row in data]

                [f.write(','.join(line) + '\n') for line in reversed(data)]


    def scheduled_pull(self, interval, granularity, products):
        if not isinstance(products, list):
            products = [products]

        for p in products:
            output_end = p + '_' + (dt.datetime.now()-dt.timedelta(hours=interval)).strftime('%Y-%m-%dT%H:%M:%S')
            output_end = output_end.replace(':', '').replace('-', '')
            outfile = 'M:\\nilay\\criptoe\\historical_data\\%s.csv' % output_end

            with open(outfile, 'a') as f:
                f.write('time,low,high,open,close,volume\n')            # titles

            data = self.get_product_historic_rates(p, (dt.datetime.now()-dt.timedelta(hours=interval, minutes=2)).isoformat(), dt.datetime.now().isoformat(), str(60*granularity))
            with open(outfile, 'a') as f:
                data = [[str((dt.datetime(1970, 1, 1, 0, 0, 0) + dt.timedelta(seconds=int(row[0]))))] + \
                [str(item) for item in row[1:]] for row in data]
                [f.write(','.join(line) + '\n') for line in reversed(data)]
