from factory import ConverterFactory

def main() -> None:
    try:
        amount = float(input("Введите сумму в USD: "))
    except ValueError:
        print("Ошибка: введите число.")
        return

    # Создаём конвертеры с кэшированием и повторными попытками (по умолчанию)
    converters = {
        "RUB": ConverterFactory.create_converter("RUB"),
        "EUR": ConverterFactory.create_converter("EUR"),
        "GBP": ConverterFactory.create_converter("GBP"),
        "CNY": ConverterFactory.create_converter("CNY"),
    }

    for name, conv in converters.items():
        try:
            result = conv.convert(amount)
            print(f"{amount} USD to {name}: {result:.2f}")
        except Exception as e:
            print(f"Ошибка при конвертации в {name}: {e}")

if __name__ == "__main__":
    main()