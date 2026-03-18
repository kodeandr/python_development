import asyncio
from converters import *

def main():    
    amount = int(input('Введите значение в USD: \n'))
    
    converter = UsdRubConverter()
    print(f"{amount} USD to RUB: {converter.convert_usd_to_rub(amount)}")
    
    converter = UsdEurConverter()
    print(f"{amount} USD to EUR: {converter.convert_usd_to_eur(amount)}")
    
    converter = UsdGbpConverter()
    print(f"{amount} USD to GBP: {converter.convert_usd_to_gbp(amount)}")
    
    converter = UsdCnyConverter()
    print(f"{amount} USD to CNY: {converter.convert_usd_to_cny(amount)}")

if __name__ == "__main__":
    main()