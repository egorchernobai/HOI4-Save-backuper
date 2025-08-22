from struct import unpack

TOKEN_MAP = {
    0x2a35: "player",
    0x284a: "date",
    0x2e3e: "ideology",
    0x1: "=",
}


def parse_hoi4_bin(filepath):
    """
    Парсит бинарный файл HOI4 и возвращает значения player и date.
    """
    with open(filepath, "rb") as f:
        if f.read(7) != b'HOI4bin':
            return 0

        depth = 0
        space_count = 0
        MAX_SPACES = 9
        otv = []

        while space_count < MAX_SPACES:
            bytes_ = f.read(2)
            if len(bytes_) != 2:
                break
            code = unpack('<H', bytes_)[0]

            if code == 12:  # int
                token = 12
                text = str(unpack('<i', f.read(4))[0])
            elif code == 13:  # float
                token = 13
                text = str(unpack('<i', f.read(4))[0]/1000)
            elif code == 14:  # bool/short string
                token = 14
                tmp = unpack('B', f.read(1))[0]
                if tmp == 0:
                    text = "no"
                elif tmp == 1:
                    text = "yes"
                else:
                    token = 15
                    length = unpack('<H', f.read(2))[0]
                    text = f.read(length).decode('utf-8')
            elif code == 15:  # string
                token = 15
                length = unpack('<H', f.read(2))[0]
                text = '"' + f.read(length).decode('utf-8') + '"'
            elif code == 20:  # unsigned int
                token = 12
                text = str(unpack('<I', f.read(4))[0])
            elif code == 23:  # token map
                length = unpack('<H', f.read(2))[0]
                text = f.read(length).decode('utf-8')
                token = -1
                for k, v in TOKEN_MAP.items():
                    if v == text:
                        token = k
            elif code == 359:
                token = 359
                text = str(unpack('<q', f.read(8))[0])
            elif code == 668:
                token = 668
                text = str(unpack('<Q', f.read(8))[0])
            else:
                token = code
                text = TOKEN_MAP.get(token, "UNKNOWN_TOKEN_" + str(token))

            if token == 3:  # {
                depth += 1
            elif token == 4:  # }
                depth -= 1
            else:
                otv.append(text)
                space_count += 1  # считаем пробелы

        # Возвращаем только player и date
        player_value = otv[2][1:-1]  # убираем кавычки
        date_value = int(otv[8])
        return [player_value, date_value]
