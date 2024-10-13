import csv

def cleaner(text: str) -> list:
    """Bring the location landmark in the dataset to a common format.

        Keyword arguments:
        text -- string with the list of addresses closest to the road sign
        streets_list -- list of street names where the road sign is located
        """
    streets_list = []
    s = text.replace('Б.', 'Бол').replace('М.', 'Мал').replace('Ср.', 'Сред').replace('ё', 'е').split(', ')  ##bring "Большой", "Малый" and "Средний" indices to a common format and split string
    for i in range(len(s)):
        if (s[i].islower() == False):  ##automatically remove all elements that do not contain capital letters
            if ' ' in s[i]:
                dot_index = s[i].find('.')  ##find the dot from 'ул.', 'пер.'
                space = dot_index - s[i][dot_index::-1].find(' ')
                s[i] = s[i][:space]  ##delete words 'ул.', 'пер.' etc. and all everything that is contained further
                new_space = len(s[i]) - s[i][::-1].find(' ')
                if s[i][new_space:].isalpha() and s[i][new_space:].islower():  ##check for the content of the full spelling of words 'улица', 'переулок' etc., and leave only the proper name (with capital letters) in the line
                    s[i] = s[i][:new_space - 1]
            streets_list.append(s[i])
    return streets_list

def make_format(text: str) -> str:
    """Remove the standart number from the type of road sign

            Keyword arguments:
            text -- string with the type of road sign
            name -- string with the name of road sign
            """
    index = text.find(' ')
    name = text[index + 1:]
    return name

def len_format(text: str) -> str:
    """Bring the street name in the table with lengths to a common format.

            Keyword arguments:
            text -- string with the street name
            streets_list -- string with the street name in a format comparable to the dataset
            """
    street = ''
    index = ''
    s = text.replace('(', '').replace(')', '').replace('ё', 'е').split(' ') ##bring "Большой" and "Малый" indices to a common format and split string
    for element in s:
        if 'бол' in element.lower():  ##change indices 'Большой' for 'Бол' and 'Малый' for 'Мал'
            index = 'Бол '
            element = element.lower()
        if 'мал' in element.lower():
            index = 'Мал '
            element = element.lower()
        if 'сред' in element.lower():  ##change indices 'Большой' for 'Бол' and 'Малый' for 'Мал'
            index = 'Сред '
            element = element.lower()
        if (element.islower() == False) or (element.isalpha() == False):  ##delete words 'улица', 'переулок' etc., and leave only the proper name (with capital letters) in the line
            street += element + ' '  ##write the components of the street name in a line
    street += index  ##don't forget about the index
    return street[:-1]

signs_dict = {}
dict_streets = {}
print('Примечание: название не должно содержать слов "улица, переулок", индексы ("1-й", "2-ая") и приставки ("Академика", "Генерала") вводятся после названия улицы (пр. "Понтрягина Академика"), индексы Большой(-ая), Средний(-яя) и Малый(-ая) вводятся в формате "Бол", "Сред" и "Мал", для приставок недоступен расчет плотности знака.')
print('Введите название улицы, проезда, переулка на русском:')
street_name = input()
with open('data/data-62681-2024-09-20.csv', 'r', newline='') as csvfile:  ##unpack the dataset
    csvreader = csv.reader(csvfile, delimiter=';')
    for row in csvreader:
        row[3] = cleaner(row[3])  ##bring the text of the location landmark to a common format
        row[4] = make_format(row[4])  ##bring the type of road sign to a common format
        for element in row[3]:
            if element.lower() == street_name.lower():  ##take the street we need from the location reference
                if row[4] not in signs_dict:  ##new type of road sign added to dictionary
                    signs_dict[row[4]] = 1
                elif row[4] in signs_dict:  ##road sign already exists? add to counter
                    signs_dict[row[4]] += 1
                break  ##The peculiarity of the location landmark is the presence of several addresses on one street, so the cycle closes after finding one required
sorted_signs = sorted(signs_dict.items(), key=lambda item: item[1], reverse=True)  ##sort in descending order by number of signs

with open('data/street_len_meters.csv', 'r', newline='') as lenfile: ##unpack the table with lengths
    lenreader = csv.reader(lenfile, delimiter=',')
    for row2 in lenreader:
        row2[1] = len_format(row2[1])  ##bring the street name to a common format
        if '.' in row2[11]:
            if row2[1] not in dict_streets:  ##calculate the total length of each street
                dict_streets[row2[1]] = float(row2[11])
            elif row2[1] in dict_streets:
                dict_streets[row2[1]] += float(row2[11])

with open(f'data/{street_name}.csv', 'w', newline='') as resfile:  ##open a new csv for recording
    filewriter = csv.writer(resfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    filewriter.writerow(['Тип дорожного знака', 'Количество знаков', 'Плотность знаков на улице (метров дороги на один знак), м'])
    if street_name in dict_streets:
        for keys, values in sorted_signs:  ##if the street length is available, we write down the quantity of signs and their density
            filewriter.writerow([keys, values, (dict_streets[street_name]/values)])
    else:
        for keys, values in sorted_signs:  ##if not, we only write down the quantity and 'Null' for density
            filewriter.writerow([keys, values, 'Null'])
