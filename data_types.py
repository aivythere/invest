import appcolor


def decorateNumberDigits(string):
    if type(string) is str:
        string = string.replace(",", "")
    return '{:,}'.format(round(float(string),2)).replace(',', ' ')


currency_meanings = {"RUB": "₽", "USD": "$"}


class TooFewValues(Exception):
    pass


class PriceData:
    def __init__(self, currency: str, price=None, last_change_percent=None, last_change_amount=None, ai_change=None):

        self.price = round(float(price), 2) if price is not None else None
        self.last_change_amount = round(float(last_change_amount), 2) if last_change_amount is not None else None
        self.currency = currency if currency is not None else None
        self.percent = round(float(last_change_percent), 2) if last_change_percent is not None else None
        self.ai_change = round(float(ai_change), 2) if ai_change is not None else None

        if self.price is not None and self.last_change_amount is None and self.percent is None:
            self.price_text = f"{decorateNumberDigits(self.price)} {currency_meanings[self.currency]}"

        elif self.price is not None and self.last_change_amount is not None and self.percent is not None:

            if self.last_change_amount > 0:  # если акция выросла, зеленый цвет

                self.last_change_text_raw = f"{decorateNumberDigits(self.last_change_amount)} " \
                                            f"{currency_meanings[self.currency]}" + "  " + f"{self.percent}%"
                self.last_change_text = appcolor.green_upprice_html_bb.format(self.last_change_text_raw)
                self.combined_onlypercent = f"{decorateNumberDigits(self.price)} {currency_meanings[self.currency]}" + \
                                            "  " + appcolor.green_upprice_html_bb.format(f"{self.percent}%")
                self.combined_full = f"[b]{decorateNumberDigits(self.price)} {currency_meanings[self.currency]}[/b]" + \
                                     "\n" + f"{appcolor.green_upprice_html_bb.format(self.last_change_amount)} {appcolor.green_upprice_html_bb.format(currency_meanings[self.currency])}" \
                                     + "  " + appcolor.green_upprice_html_bb.format(f"{self.percent}%")

            elif self.last_change_amount < 0:  # если упала, красный цвет
                self.last_change_text_raw = f"{decorateNumberDigits(self.last_change_amount)} " \
                                            f"{currency_meanings[self.currency]}" + "  " + f"{self.percent}%"
                self.last_change_text = appcolor.red_downprice_html_bb.format(self.last_change_text_raw)
                self.combined_onlypercent = f"{decorateNumberDigits(self.price)} {currency_meanings[self.currency]}" + \
                                            "  " + appcolor.red_downprice_html_bb.format(f"{self.percent}%")

                self.combined_full = f"[b]{decorateNumberDigits(self.price)} {currency_meanings[self.currency]}[/b]" + "\n" + \
                                     f"{appcolor.red_downprice_html_bb.format(self.last_change_amount)} {appcolor.red_downprice_html_bb.format(currency_meanings[self.currency])}" \
                                     + "  " + appcolor.red_downprice_html_bb.format(f"{self.percent}%")
            else:  # Если цена не менялась
                self.last_change_text_raw = f"{decorateNumberDigits(self.last_change_amount)} " \
                                            f"{currency_meanings[self.currency]}" + "  " + f"{self.percent}%"
                self.last_change_text = self.last_change_text_raw
                self.combined_onlypercent = f"{decorateNumberDigits(self.price)} {currency_meanings[self.currency]}" + \
                                            "  " + f"{self.percent}%"

                self.combined_full = f"[b]{decorateNumberDigits(self.price)} {currency_meanings[self.currency]}[/b]" + "\n" + \
                                     f"{self.last_change_amount} {(currency_meanings[self.currency])}" \
                                     + "  " + f"{self.percent}%"
        elif self.price is None and self.last_change_amount is not None and self.percent is not None:

            if self.last_change_amount > 0:  # если акция выросла, зеленый цвет

                self.last_change_text_raw = f"{decorateNumberDigits(self.last_change_amount)} " \
                                            f"{currency_meanings[self.currency]}" + "  " + f"{self.percent}%"
                self.last_change_text = appcolor.green_upprice_html_bb.format(self.last_change_text_raw)

            elif self.last_change_amount < 0:  # если упала, красный цвет
                self.last_change_text_raw = f"{decorateNumberDigits(self.last_change_amount)} " \
                                            f"{currency_meanings[self.currency]}" + "  " + f"{self.percent}%"
                self.last_change_text = appcolor.red_downprice_html_bb.format(self.last_change_text_raw)

            else:  # Если цена не менялась
                self.last_change_text_raw = f"{decorateNumberDigits(self.last_change_amount)} " \
                                            f"{currency_meanings[self.currency]}" + "  " + f"{self.percent}%"
                self.last_change_text = self.last_change_text_raw

        elif ai_change is not None and price is None and last_change_amount is None and last_change_percent is None:
            # только вход цены с нейронки
            if self.ai_change > 0:  # если акция выросла, зеленый цвет

                self.ai_change_text_raw = f"+{decorateNumberDigits(self.ai_change)} " \
                                          f"{currency_meanings[self.currency]}"
                self.ai_change_text = appcolor.green_upprice_html_bb.format(self.ai_change_text_raw)

            elif self.ai_change < 0:  # если упала, красный цвет
                self.ai_change_text_raw = f"{decorateNumberDigits(self.ai_change)} " \
                                          f"{currency_meanings[self.currency]}"
                self.ai_change_text = appcolor.red_downprice_html_bb.format(self.ai_change_text_raw)
        else:
            print(currency, price, last_change_amount, last_change_percent, 'onexception (PRICEDATA)')
            raise TooFewValues()


class StockHavingData:
    def __init__(self, currency, count, current_price=None, multiply=False):
        if count is not None and current_price is not None and currency is not None and not multiply:
            self.stockhaving_text = f"{count} шт." + "  " + f"{decorateNumberDigits(current_price)} {currency_meanings[currency]}"
        elif count is not None and current_price is not None and currency is not None and multiply:
            self.stockhaving_text = f"{count} шт." + "  " + f"{decorateNumberDigits(count * current_price)} {currency_meanings[currency]}"
