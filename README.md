Huh?
----
A simple Python library to query Bovespa stock option data. Uses [mibian](https://code.mibian.net) to compute implied volatility with the Black-Scholes model.

Usage
-----
    >>> from datetime import date, timedelta
    >>> yesterday = date.today() - timedelta(days=1)
    >>> from bovespa import Call, Put
    >>> c = Call('ITSA4', date=yesterday)
    downloading COTAHIST_D27082018.ZIP...
    >>> c.underlying.close_price
    9.76
    >>> c.strikes
    [9.21, 9.34, 9.540000000000001, 9.56, 9.66, 9.74, 9.76, 9.96, 10.02, 10.09, 10.24, 10.34, 10.47, 10.53, 10.700000000000001, 11.15, 11.65]
    >>> c.expirations
    [datetime.date(2018, 10, 15), datetime.date(2018, 9, 17)]
    >>> c.set_expiration(date(2018, 9, 17))
    >>> c.set_strike(10.02)
    >>> c.ticker
    'ITSAI52'
    >>> c.close_price
    0.2
    >>> c.implied_volatility()
    31.25
