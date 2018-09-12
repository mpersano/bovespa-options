Huh?
----
A simple Python library to query Bovespa stock option data. Uses [mibian](https://code.mibian.net) to compute implied volatility with the Black-Scholes model.

Usage
-----
    >>> from datetime import date, timedelta
    >>> yesterday = date.today() - timedelta(days=1)
    >>> from bovespa import Call, Put
    >>> c = Call('ITSA4', date=yesterday)
    downloading COTAHIST_D11092018.ZIP...
    >>> c.underlying.close_price
    9.290000000000001
    >>> c.expirations()
    [datetime.date(2018, 9, 17), datetime.date(2018, 10, 15), datetime.date(2018, 12, 17), datetime.date(2019, 1, 21)]
    >>> c.set_expiration(date(2018, 10, 15))
    >>> c.strikes()
    [9.33, 9.53, 9.73, 10.08, 10.77]
    >>> c.set_strike(9.73)
    >>> c.ticker
    'ITSAJ995'
    >>> c.close_price
    0.38
    >>> c.implied_volatility()
    47.8515625
