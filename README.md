# The Great River

Scripts used to automate searching for and purchase of certain products.

## TME parametric search

A tool to do parametric parts search on the https://www.tme.eu parts store. The tool has a number of sub-commands which are
built for the following workflow. Please note, that all of the labels are in Polish as multi-language support is not yet done.

First, check which categories are available:

```
(generic) ➜  greatriver git:(master) ✗ bin/tme-search categories                                                
2020-05-18T22:35:51.032795Z start                          config={'country_code': 'pl', 'language_code': 'en', 'base_url': 'https://www.tme.eu/', 'currency': 'USD', 'cmd': 'categories', 'print_tree': False}
2020-05-18T22:35:52.064065Z categories loaded              category_count=1579
17 Tranzystory unipolarne
19 Tyrystory
21 Osprzęt do półprzewodników
24 Potencjometry
26 Kondensatory
27 Kwarce i filtry
29 Warystory
30 Złącza sygnałowe
31 Złącza do przesyłu danych
33 Złącza przemysłowe
34 Złącza zasilające
[...]
112291 Transoptory
[...]
118088 Rozwiązania kompatybilne z Arduino
118089 Amperomierze
118090 Woltomierze
118091 Mierniki i analizatory parametrów sieci
118092 Liczniki energii elektrycznej
118093 Mierniki panelowe cyfrowe - pozostałe
118094 Zasilacze PoE
(generic) ➜  greatriver git:(master) ✗ 
```

Let's say we want to search for optocuplers ("Transoptory"). The category ID in this case is '112291' and we can use it to query the parameter space available:

```
(generic) ➜  greatriver git:(master) ✗ bin/tme-search parameters 112291
2020-05-18T23:06:15.286857Z start                          config={'country_code': 'pl', 'language_code': 'en', 'base_url': 'https://www.tme.eu/', 'currency': 'USD', 'cmd': 'parameters', 'categories': ['112291'], 'all_values': False}
2020-05-18T23:06:16.337996Z categories loaded              category_count=1579
2020-05-18T23:06:16.338219Z fetching parameters            category_id=112291 category_name=Transoptory url=/pl/katalog/transoptory_112291/
2020-05-18T23:06:17.741949Z fetching values                category_id=112291 category_name=Transoptory parameter_name=Ilość pinów
2020-05-18T23:06:17.770453Z values parsed                  category_id=112291 category_name=Transoptory count=13 parameter_name=Producent
2020-05-18T23:06:17.770826Z values parsed                  category_id=112291 category_name=Transoptory count=2 parameter_name=Typ elementu półprzewodnikowego
2020-05-18T23:06:17.771171Z values parsed                  category_id=112291 category_name=Transoptory count=2 parameter_name=Montaż
2020-05-18T23:06:17.772064Z values parsed                  category_id=112291 category_name=Transoptory count=18 parameter_name=Rodzaj wyjścia
2020-05-18T23:06:17.774078Z values parsed                  category_id=112291 category_name=Transoptory count=43 parameter_name=Obudowa
2020-05-18T23:06:17.774497Z values parsed                  category_id=112291 category_name=Transoptory count=4 parameter_name=Liczba kanałów
2020-05-18T23:06:17.791695Z values parsed                  category_id=112291 category_name=Transoptory count=28 parameter_name=Napięcie izolacji
2020-05-18T23:06:17.799801Z values parsed                  category_id=112291 category_name=Transoptory count=185 parameter_name=CTR@If
2020-05-18T23:06:17.845255Z values parsed                  category_id=112291 category_name=Transoptory count=87 parameter_name=Czas wyłączania
2020-05-18T23:06:17.889745Z values parsed                  category_id=112291 category_name=Transoptory count=91 parameter_name=Czas załączania
2020-05-18T23:06:17.903804Z values parsed                  category_id=112291 category_name=Transoptory count=27 parameter_name=Napięcie kolektor-emiter
2020-05-18T23:06:17.909575Z values parsed                  category_id=112291 category_name=Transoptory count=12 parameter_name=Prąd wyzwalania
2020-05-18T23:06:17.911103Z values parsed                  category_id=112291 category_name=Transoptory count=3 parameter_name=Napięcie wsteczne maks.
2020-05-18T23:06:17.913398Z values parsed                  category_id=112291 category_name=Transoptory count=5 parameter_name=Napięcie wyjściowe
2020-05-18T23:06:17.917822Z values parsed                  category_id=112291 category_name=Transoptory count=9 parameter_name=Prąd kolektora
2020-05-18T23:06:17.918275Z values parsed                  category_id=112291 category_name=Transoptory count=1 parameter_name=Rodzaj opakowania
2020-05-18T23:06:17.918825Z values parsed                  category_id=112291 category_name=Transoptory count=6 parameter_name=Opis transoptora
2020-05-18T23:06:17.919467Z values parsed                  category_id=112291 category_name=Transoptory count=4 parameter_name=Ilość pinów
Parameter                        Unit    Example values
-------------------------------  ------  ------------------------------------------------------------
Producent                                TOSHIBA
Typ elementu półprzewodnikowego          transoptor
Montaż                                   THT
Rodzaj wyjścia                           tranzystorowe
Obudowa                                  SSOP4, SOP8L, DIP4
Liczba kanałów                           4
Napięcie izolacji                V       1.6kV, 4.5kV
CTR@If                                   7.5%@10mA, 50%@5mA, 20-50%@16mA, 50-300%@10mA, 600-7500%@1mA
Czas wyłączania                  s       60ns, 55µs, 60µs, 7µs, 8.6µs
Czas załączania                  s       18ns, 12ns, 20ns, 90ns, 40µs
Napięcie kolektor-emiter         V       30V, 120V
Prąd wyzwalania                  A       5mA
Napięcie wsteczne maks.          V       3V
Napięcie wyjściowe               V       0...35V
Prąd kolektora                   A       2mA
Rodzaj opakowania                        rolka
Opis transoptora                         K3=0.557-1.618
Ilość pinów                              4
(generic) ➜  greatriver git:(master) ✗ 
```

The parameters sub-command prints a name, unit and example values for each parameter. Parameter values are used to add constraints on the parts we will list
using the third command - "parts". For example, let's assume we need to list optocouplers which have the isolation voltage ("Napięcie izolacji") of more than 5kV:

```
(tme) ➜  greatriver git:(master) bin/tme-search parts -c 112291 -P '"Napięcie izolacji" > "5 kV"' 
2020-05-20T22:05:50.286151Z start                          config={'country_code': 'pl', 'language_code': 'en', 'base_url': 'https://www.tme.eu/', 'currency': 'USD', 'cmd': 'parts', 'cat_id': '112291', 'constraints': ['"Napięcie izolacji" > "5 kV"'], 'sort_field': None, 'sort_order': 'asc', 'item_limit': 20}
2020-05-20T22:05:51.467174Z categories loaded              category_count=1579
2020-05-20T22:05:51.467342Z fetching parameters            category_id=112291 category_name=Transoptory url=/pl/katalog/transoptory_112291/
2020-05-20T22:05:53.119858Z fetching values                category_id=112291 category_name=Transoptory parameter_name=Ilość pinów
2020-05-20T22:05:53.148731Z values parsed                  category_id=112291 category_name=Transoptory count=13 parameter_name=Producent
2020-05-20T22:05:53.149107Z values parsed                  category_id=112291 category_name=Transoptory count=2 parameter_name=Typ elementu półprzewodnikowego
2020-05-20T22:05:53.149457Z values parsed                  category_id=112291 category_name=Transoptory count=2 parameter_name=Montaż
2020-05-20T22:05:53.150394Z values parsed                  category_id=112291 category_name=Transoptory count=18 parameter_name=Rodzaj wyjścia
2020-05-20T22:05:53.152285Z values parsed                  category_id=112291 category_name=Transoptory count=43 parameter_name=Obudowa
2020-05-20T22:05:53.152749Z values parsed                  category_id=112291 category_name=Transoptory count=4 parameter_name=Liczba kanałów
2020-05-20T22:05:53.170709Z values parsed                  category_id=112291 category_name=Transoptory count=28 parameter_name=Napięcie izolacji
2020-05-20T22:05:53.178658Z values parsed                  category_id=112291 category_name=Transoptory count=185 parameter_name=CTR@If
2020-05-20T22:05:53.221155Z values parsed                  category_id=112291 category_name=Transoptory count=87 parameter_name=Czas wyłączania
2020-05-20T22:05:53.266127Z values parsed                  category_id=112291 category_name=Transoptory count=91 parameter_name=Czas załączania
2020-05-20T22:05:53.279611Z values parsed                  category_id=112291 category_name=Transoptory count=27 parameter_name=Napięcie kolektor-emiter
2020-05-20T22:05:53.285586Z values parsed                  category_id=112291 category_name=Transoptory count=12 parameter_name=Prąd wyzwalania
2020-05-20T22:05:53.287355Z values parsed                  category_id=112291 category_name=Transoptory count=3 parameter_name=Napięcie wsteczne maks.
2020-05-20T22:05:53.289755Z values parsed                  category_id=112291 category_name=Transoptory count=5 parameter_name=Napięcie wyjściowe
2020-05-20T22:05:53.294230Z values parsed                  category_id=112291 category_name=Transoptory count=9 parameter_name=Prąd kolektora
2020-05-20T22:05:53.294729Z values parsed                  category_id=112291 category_name=Transoptory count=1 parameter_name=Rodzaj opakowania
2020-05-20T22:05:53.295693Z values parsed                  category_id=112291 category_name=Transoptory count=6 parameter_name=Opis transoptora
2020-05-20T22:05:53.296202Z values parsed                  category_id=112291 category_name=Transoptory count=4 parameter_name=Ilość pinów
2020-05-20T22:05:53.304103Z looking up parts               category_id=112291 category_name=Transoptory mapped_params=430:1549821,1444593,1444637,1444652,1444729,1444633,1548890,1444630,1444635,1548893 url=/pl/katalog/transoptory_112291/
2020-05-20T22:05:54.961380Z parsing product rows           category_id=112291 category_name=Transoptory count=22
2020-05-20T22:05:54.969329Z fetching pricing information   category_id=112291 category_name=Transoptory symbol_count=20
Manufacturer                  Symbol        Pricing
----------------------------  ------------  --------------------------------------------------------------------------------------------
VISHAY                        SFH6156-1T    {'1000+': '0.1485', '3000+': '0.1336'}
ON SEMICONDUCTOR (FAIRCHILD)  4N27SR2M      {'2+': '0.16', '10+': '0.11', '50+': '0.09', '1000+': '0.08'}
ON SEMICONDUCTOR (FAIRCHILD)  4N27-F-SMD    {'2+': '0.1700', '10+': '0.1170', '25+': '0.1084', '100+': '0.0991', '500+': '0.0899'}
ISOCOM                        4N26XSM       {'2+': '0.1700', '10+': '0.1290', '65+': '0.1118'}
ISOCOM                        H11AV1XSM     {'2+': '0.1750', '10+': '0.1290', '65+': '0.1088', '260+': '0.0972', '1040+': '0.0936'}
ISOCOM                        SFH617A-2X    {'2+': '0.18', '10+': '0.12', '50+': '0.11', '250+': '0.09'}
ISOCOM                        SFH617A-4X    {'2+': '0.18', '10+': '0.12', '50+': '0.11', '250+': '0.09'}
ISOCOM                        SFH617A-2XSM  {'2+': '0.1800', '10+': '0.1570', '50+': '0.1432', '250+': '0.1222'}
ISOCOM                        SFH617A-4-I   {'1+': '0.18', '3+': '0.17', '10+': '0.15', '25+': '0.14', '100+': '0.13'}
ISOCOM                        TIL111XSM     {'2+': '0.19', '10+': '0.17', '50+': '0.15', '250+': '0.13'}
ISOCOM                        CNY17-2XSM    {'2+': '0.2000', '10+': '0.1570', '50+': '0.1390', '250+': '0.1222'}
ISOCOM                        CNY17F-2XSM   {'2+': '0.2000', '10+': '0.1570', '65+': '0.1391', '260+': '0.1222'}
ON SEMICONDUCTOR (FAIRCHILD)  4N28M         {'2+': '0.22', '10+': '0.18', '50+': '0.16', '250+': '0.15', '1000+': '0.14'}
ON SEMICONDUCTOR (FAIRCHILD)  4N30M         {'2+': '0.23', '10+': '0.18', '50+': '0.16', '250+': '0.13'}
ON SEMICONDUCTOR (FAIRCHILD)  4N36SM        {'2+': '0.23', '10+': '0.15', '50+': '0.14', '250+': '0.13'}
ON SEMICONDUCTOR (FAIRCHILD)  4N38M         {'2+': '0.23', '10+': '0.18', '50+': '0.16', '250+': '0.14', '1000+': '0.13'}
ON SEMICONDUCTOR (FAIRCHILD)  4N26M         {'2+': '0.2894', '10+': '0.2524', '50+': '0.2233', '250+': '0.1816', '1000+': '0.1685'}
ISOCOM                        4N26X         {'2+': '0.29', '10+': '0.20', '65+': '0.18', '260+': '0.15', '1040+': '0.14'}
VISHAY                        CNY17G-2      {'2+': '0.30638', '10+': '0.20462', '50+': '0.16851', '250+': '0.14881', '1000+': '0.13787'}
VISHAY                        SFH6156-1     {'2+': '0.30704', '10+': '0.20711', '50+': '0.18317', '250+': '0.14881'}
```

As you can see the -P flag is used to define constraints with a pretty self-explanatory syntac. Simple comparison operations are possible: - = < > and the tool handles units thanks to the https://github.com/hgrecco/pint module. For example, instead of 5kV you can specify a value of 5000V:

```
(tme) ➜  greatriver git:(master) bin/tme-search parts -c 112291 -P '"Napięcie izolacji" > "5000V"'
2020-05-20T22:07:07.905001Z start                          config={'country_code': 'pl', 'language_code': 'en', 'base_url': 'https://www.tme.eu/', 'currency': 'USD', 'cmd': 'parts', 'cat_id': '112291', 'constraints': ['"Napięcie izolacji" > "5000V"'], 'sort_field': None, 'sort_order': 'asc', 'item_limit': 20}
2020-05-20T22:07:09.007152Z categories loaded              category_count=1579
2020-05-20T22:07:09.007331Z fetching parameters            category_id=112291 category_name=Transoptory url=/pl/katalog/transoptory_112291/
2020-05-20T22:07:10.541609Z fetching values                category_id=112291 category_name=Transoptory parameter_name=Ilość pinów
2020-05-20T22:07:10.569299Z values parsed                  category_id=112291 category_name=Transoptory count=13 parameter_name=Producent
2020-05-20T22:07:10.569683Z values parsed                  category_id=112291 category_name=Transoptory count=2 parameter_name=Typ elementu półprzewodnikowego
2020-05-20T22:07:10.570025Z values parsed                  category_id=112291 category_name=Transoptory count=2 parameter_name=Montaż
2020-05-20T22:07:10.570922Z values parsed                  category_id=112291 category_name=Transoptory count=18 parameter_name=Rodzaj wyjścia
2020-05-20T22:07:10.572796Z values parsed                  category_id=112291 category_name=Transoptory count=43 parameter_name=Obudowa
2020-05-20T22:07:10.573215Z values parsed                  category_id=112291 category_name=Transoptory count=4 parameter_name=Liczba kanałów
2020-05-20T22:07:10.590842Z values parsed                  category_id=112291 category_name=Transoptory count=28 parameter_name=Napięcie izolacji
2020-05-20T22:07:10.599653Z values parsed                  category_id=112291 category_name=Transoptory count=185 parameter_name=CTR@If
2020-05-20T22:07:10.643336Z values parsed                  category_id=112291 category_name=Transoptory count=87 parameter_name=Czas wyłączania
2020-05-20T22:07:10.688924Z values parsed                  category_id=112291 category_name=Transoptory count=91 parameter_name=Czas załączania
2020-05-20T22:07:10.705041Z values parsed                  category_id=112291 category_name=Transoptory count=27 parameter_name=Napięcie kolektor-emiter
2020-05-20T22:07:10.713954Z values parsed                  category_id=112291 category_name=Transoptory count=12 parameter_name=Prąd wyzwalania
2020-05-20T22:07:10.715814Z values parsed                  category_id=112291 category_name=Transoptory count=3 parameter_name=Napięcie wsteczne maks.
2020-05-20T22:07:10.719067Z values parsed                  category_id=112291 category_name=Transoptory count=5 parameter_name=Napięcie wyjściowe
2020-05-20T22:07:10.724682Z values parsed                  category_id=112291 category_name=Transoptory count=9 parameter_name=Prąd kolektora
2020-05-20T22:07:10.725390Z values parsed                  category_id=112291 category_name=Transoptory count=1 parameter_name=Rodzaj opakowania
2020-05-20T22:07:10.726427Z values parsed                  category_id=112291 category_name=Transoptory count=6 parameter_name=Opis transoptora
2020-05-20T22:07:10.727140Z values parsed                  category_id=112291 category_name=Transoptory count=4 parameter_name=Ilość pinów
2020-05-20T22:07:10.736474Z looking up parts               category_id=112291 category_name=Transoptory mapped_params=430:1549821,1444593,1444637,1444652,1444729,1444633,1548890,1444630,1444635,1548893 url=/pl/katalog/transoptory_112291/
2020-05-20T22:07:12.625406Z parsing product rows           category_id=112291 category_name=Transoptory count=22
2020-05-20T22:07:12.636431Z fetching pricing information   category_id=112291 category_name=Transoptory symbol_count=20
Manufacturer                  Symbol        Pricing
----------------------------  ------------  --------------------------------------------------------------------------------------------
VISHAY                        SFH6156-1T    {'1000+': '0.1485', '3000+': '0.1336'}
ON SEMICONDUCTOR (FAIRCHILD)  4N27SR2M      {'2+': '0.16', '10+': '0.11', '50+': '0.09', '1000+': '0.08'}
ON SEMICONDUCTOR (FAIRCHILD)  4N27-F-SMD    {'2+': '0.1700', '10+': '0.1170', '25+': '0.1084', '100+': '0.0991', '500+': '0.0899'}
ISOCOM                        4N26XSM       {'2+': '0.1700', '10+': '0.1290', '65+': '0.1118'}
ISOCOM                        H11AV1XSM     {'2+': '0.1750', '10+': '0.1290', '65+': '0.1088', '260+': '0.0972', '1040+': '0.0936'}
ISOCOM                        SFH617A-2X    {'2+': '0.18', '10+': '0.12', '50+': '0.11', '250+': '0.09'}
ISOCOM                        SFH617A-4X    {'2+': '0.18', '10+': '0.12', '50+': '0.11', '250+': '0.09'}
ISOCOM                        SFH617A-2XSM  {'2+': '0.1800', '10+': '0.1570', '50+': '0.1432', '250+': '0.1222'}
ISOCOM                        SFH617A-4-I   {'1+': '0.18', '3+': '0.17', '10+': '0.15', '25+': '0.14', '100+': '0.13'}
ISOCOM                        TIL111XSM     {'2+': '0.19', '10+': '0.17', '50+': '0.15', '250+': '0.13'}
ISOCOM                        CNY17-2XSM    {'2+': '0.2000', '10+': '0.1570', '50+': '0.1390', '250+': '0.1222'}
ISOCOM                        CNY17F-2XSM   {'2+': '0.2000', '10+': '0.1570', '65+': '0.1391', '260+': '0.1222'}
ON SEMICONDUCTOR (FAIRCHILD)  4N28M         {'2+': '0.22', '10+': '0.18', '50+': '0.16', '250+': '0.15', '1000+': '0.14'}
ON SEMICONDUCTOR (FAIRCHILD)  4N30M         {'2+': '0.23', '10+': '0.18', '50+': '0.16', '250+': '0.13'}
ON SEMICONDUCTOR (FAIRCHILD)  4N36SM        {'2+': '0.23', '10+': '0.15', '50+': '0.14', '250+': '0.13'}
ON SEMICONDUCTOR (FAIRCHILD)  4N38M         {'2+': '0.23', '10+': '0.18', '50+': '0.16', '250+': '0.14', '1000+': '0.13'}
ON SEMICONDUCTOR (FAIRCHILD)  4N26M         {'2+': '0.2894', '10+': '0.2524', '50+': '0.2233', '250+': '0.1816', '1000+': '0.1685'}
ISOCOM                        4N26X         {'2+': '0.29', '10+': '0.20', '65+': '0.18', '260+': '0.15', '1040+': '0.14'}
VISHAY                        CNY17G-2      {'2+': '0.30638', '10+': '0.20462', '50+': '0.16851', '250+': '0.14881', '1000+': '0.13787'}
VISHAY                        SFH6156-1     {'2+': '0.30704', '10+': '0.20711', '50+': '0.18317', '250+': '0.14881'}
```

The last column presents pricing information with unit prices depending on the ordered amount.

## Allegro scripts

Tools to search concluded offers on the https://allegro.pl auction site

First run the catsearch.py to create a default configuration file as well as the category ID cache:

```
$ catsearch.py
INFO:root:Creating a new configuration file in '/home/enki/.config/allegro-prodsearch/config.ini'
WARNING:root:Cache file '/home/enki/.cache/allegro-prodsearch/country-1/categories-latest.pickle' could not be found, requesting categories tree from server
INFO:root:Cached categories tree version '1.4.72' in '/home/enki/.cache/allegro-prodsearch/country-1/categories-1.4.72.pickle'
INFO:root:Loaded 23895 categories
$
```

This step will allow you to lookup numeric category IDs:

```
$ catsearch.py Thriller
INFO:root:Loaded 23895 categories
20616   /Allegro/Filmy/Kasety wideo/Thrillery
89066   /Allegro/Filmy/Płyty Blu-ray/Thrillery
100121  /Allegro/Filmy/Płyty DVD/Thrillery
20675   /Allegro/Filmy/Płyty VCD/Thrillery
97766   /Allegro/Książki i Komiksy/Audiobooki - CD/Kryminały, thrillery i sensacyjne
250173  /Allegro/Książki i Komiksy/Ebooki/Kryminał i sensacja/Thriller
91480   /Allegro/Książki i Komiksy/Książki obcojęzyczne/Po angielsku/Thrillery, sensacyjne
79166   /Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne
92476   /Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Polskie
92475   /Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne
$ 
```

You can use the numeric IDs to efficiently search for items on the Allegro site:

```
$ prodsearch.py -c 92475 forsyth clancy 
INFO:root:Searching for 'forsyth' in category '92475'
INFO:root:Search returned 905 offers (result set is limited to 100)
INFO:root:Searching for 'clancy' in category '92475'
INFO:root:Search returned 808 offers (result set is limited to 100)
INFO:root:Summarizing 200 returned offers, 39 offers concluded
+----------------------------------------------------|-----------------------------------------------------------------------------------------------------------|---------|------------|-------+
| Auction title                                      |                                                  Category                                                 | Bidders |  Finished  | Price |
+----------------------------------------------------|-----------------------------------------------------------------------------------------------------------|---------|------------|-------+
| Zwierciadło  - Tom Clancy -12                      | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-22 |  17.0 |
| Kardynał z Kremla Tom Clancy                       | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-22 |  7.2  |
| NEGOCJATOR FREDERICK FORSYTH                       | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-21 |  4.99 |
| Forsyth x 2 książki zestaw Negocjator... - Forsyth | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-21 |  5.4  |
| Zwiadowcy: Walkiria Clancy Tom *                   | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-20 |  11.0 |
| Wandale Tom Clancy  W-wa Ochota                    | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-20 |  2.5  |
| TOM CLANCY SPLINTER CELL SZACH-MAT 24h             | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-20 |  12.9 |
| Słowo białego człowieka Forsyth powieść sensacja   | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-20 |  16.9 |
| POLOWANIE NA CZERWONY PAŹDZIERNIK - Clancy BDB +GR | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-20 |  10.0 |
| Net Force Tom Clancy Steve Pieczenik               | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-20 |  4.0  |
| NET FORCE  -  Tom Clancy                           | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-20 |  17.0 |
| MISJA HONORU TOM CLANCY                            | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-20 | 21.99 |
| Frederick Forsyth, Czwarty protokół                | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-20 |  1.9  |
| Forsyth, Akta Odessy                               | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-20 |  2.9  |
| FREDERICK FORSYTH IKONA ______!                    | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-20 |  5.9  |
| FREDERICK FORSYTH FAŁSZERZ ______!                 | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-20 |  1.3  |
| FREDERICK FORSYTH AKTA ODESSY ____!                | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-20 |  1.2  |
| F. FORSYTH KOBRA _________!                        | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-20 |  4.89 |
| ENDWAR Tom Clancy     BDB-     WOW 2               | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-20 |  9.9  |
| Upiór Manhattanu - Frederick Forsyth 1999          | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-19 |  4.99 |
| Słowo białego człowieka - Frederick Forsyth 1996   | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-19 |  7.2  |
| Splinter cell Operacja Barakuda - Tom Clancy 2006  | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-19 |  7.99 |
| Mściciel - Frederick Forsyth 2004                  | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-19 |  4.0  |
| Kobra - Frederick Forsyth 2013                     | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-19 |  3.3  |
| Forsyth Frederick Mściciel                         | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-19 |  2.5  |
| Dzień Szakala - Frederick Forsyth 1979             | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-19 |  2.7  |
| Czysta robota - Frederick Forsyth 1994             | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-19 |  4.99 |
| CLANCY CZARNA SERIA AIB  ZESTAW 11 TOMÓW   WOW 2   | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-19 |  49.0 |
| UPIÓR MANHATTANU - FREDERICK FORSYTH BDB 72138     | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-18 |  4.5  |
| NEGOCJATOR - FREDERICK FORSYTH 68267               | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-18 |  2.0  |
| MŚCICIEL - FREDERICK FORSYTH BDB 72139             | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-18 |  4.0  |
| FREDERICK FORSYTH WETERAN ______!                  | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-18 |  3.8  |
| FORSYTH diabelska alternatywa,czwarty protokół     | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-18 |  2.5  |
| CZYSTA ROBOTA Forsyth                              | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-18 |  4.39 |
| CLANCY CZERWONY SZTORM                             | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-18 |  3.5  |
| AKTA ODESSY FORSYTH                                | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-18 |  4.0  |
| Słowo białego człowieka Forsyth W-wa               | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-17 |  2.5  |
| Frederick Forsyth - Czarna lista                   | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-17 |  4.49 |
| FREDERICK FORSYTH PSY WOJNY                        | 92475 (/Allegro/Książki i Komiksy/Literatura piękna, popularna i faktu/Thrillery, sensacyjne/Zagraniczne) |    1    | 2017-06-17 |  8.0  |
+----------------------------------------------------|-----------------------------------------------------------------------------------------------------------|---------|------------|-------+
```
