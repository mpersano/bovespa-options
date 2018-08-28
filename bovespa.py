import os.path
import datetime
import urllib
from zipfile import ZipFile
from collections import namedtuple
import mibian
import scipy

StockQuote = namedtuple('Entry', 'ticker date share_type open_price high_price low_price close_price')
OptionQuote = namedtuple('Entry', 'ticker date share_type open_price high_price low_price close_price strike expiration')

class QuoteCache:
    _URL_BASE = 'http://bvmf.bmfbovespa.com.br/InstDados/SerHist'

    def __init__(self, date):
        self.date = date
        self.stocks = {}
        self.calls = []
        self.puts = []
        self._read_quote_file()

    def _read_quote_file(self):
        base_filename = 'COTAHIST_D%02d%02d%02d' % (self.date.day, self.date.month, self.date.year)
        zip_filename = base_filename + '.ZIP'

        # download it if not available
        if not os.path.isfile(zip_filename):
            print "downloading %s..." % zip_filename
            url = "%s/%s" % (self._URL_BASE, zip_filename)
            urllib.urlretrieve(url, zip_filename)

        with ZipFile(zip_filename, 'r') as zf:
            with zf.open(base_filename + '.TXT', 'r') as f:
                for line in f:
                    self._parse_quote_line(line)

    def _to_datetime(self, s):
        y, m, d = int(s[:4]), int(s[4:6]), int(s[6:])
        return datetime.date(y, m, d)

    def _parse_quote_line(self, line):
        if line[:2] != '01':
            return
        
        ticker = line[12:24].strip()
        date = self._to_datetime(line[2:10])
        open_price = 0.01 * float(line[56:69])
        high_price = 0.01 * float(line[69:82])
        low_price = 0.01 * float(line[82:95])
        close_price = 0.01 * float(line[108:121])
        
        name = line[27:39].strip()
        spec = line[39:48].strip()
        share_type = spec.split()[0]
        
        # 010: vista
        # 070: opcoes de compra
        # 080: opcoes de venda
        market_type = line[24:27]
        
        if market_type == '010':
            stock = StockQuote(ticker, date, share_type, open_price, high_price, low_price, close_price)
            self.stocks[ticker] = stock
        elif market_type == '070' or market_type == '080':
            strike = 0.01 * float(line[188:201])
            expiration = self._to_datetime(line[202:210])
            option = OptionQuote(ticker, date, share_type, open_price, high_price, low_price, close_price, strike, expiration)
            if market_type == '070':
                self.calls.append(option)
            else:
                self.puts.append(option)

_quotes = {}
def quote_cache(date):
    return _quotes.setdefault(date, QuoteCache(date))

class Option:
    def __init__(self, ticker, date=datetime.date.today(), expiration=None, strike=None, interest_rate=6.4):
        self.expiration = expiration

        quotes = quote_cache(date)

        self.underlying = quotes.stocks[ticker]

        if self._opt_type() == 'Call':
            data = quotes.calls
        else:
            assert self._opt_type() == 'Put'
            data = quotes.puts
        self._data = [q for q in data if q.ticker[:4] == ticker[:4] and self.underlying.share_type == q.share_type]

        self.expirations = list(set(q.expiration for q in self._data))
        self.strikes = sorted([q.strike for q in self._data])

        self.expiration = None
        self.strike = None
        if expiration:
            self.set_expiration(expiration)
        if strike:
            self.set_strike(strike)

        self._interest_rate = interest_rate

    def set_expiration(self, expiration):
        if expiration not in self.expirations:
            raise ValueError('Expiration dates for this option: %s' % ', '.join([d.strftime('%d-%m-%Y') for d in self.expirations]))
        self.expiration = expiration
        if self.expiration and self.strike:
            self._set_quote()

    def set_strike(self, strike):
        closest = min(self._data, key=lambda q:abs(q.strike - strike))
        if closest.strike - strike >= 0.005:
            raise ValueError('Strikes for this option: %s' % ', '.join(['%.02f' % q.strike for q in self._data]))
        self.strike = closest.strike
        if self.expiration and self.strike:
            self._set_quote()

    def _set_quote(self):
        assert self.expiration
        assert self.strike

        quotes = [q for q in self._data if q.expiration == self.expiration]
        quote = min(quotes, key=lambda q:abs(q.strike - self.strike))

        self.ticker = quote.ticker

        self.date = quote.date

        self.open_price = quote.open_price
        self.high_price = quote.high_price
        self.low_price = quote.low_price
        self.close_price = quote.close_price

    def days_to_expiration(self):
        assert self.expiration
        return (self.expiration - self.date).days

    def implied_volatility(self):
        return self._black_scholes().impliedVolatility

class Call(Option):
    def _black_scholes(self):
        return mibian.BS([self.underlying.close_price, self.strike, self._interest_rate, self.days_to_expiration()], callPrice=self.close_price)

    def _opt_type(self):
        return 'Call'

class Put(Option):
    def _black_scholes(self):
        return mibian.BS([self.underlying.close_price, self.strike, self._interest_rate, self.days_to_expiration()], putPrice=self.close_price)

    def _opt_type(self):
        return 'Put'
