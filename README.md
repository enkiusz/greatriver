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
using the third command - "parts". For example, let's assume we need to list optocouplers which have the isolation voltage ("Napięcie izloacji") of more than 5kV:

```
2020-05-18T23:08:14.504531Z start                          config={'country_code': 'pl', 'language_code': 'en', 'base_url': 'https://www.tme.eu/', 'currency': 'USD', 'cmd': 'parts', 'cat_id': '112291', 'constraints': ['"Napięcie izolacji" > "5 kV"'], 'sort_field': None, 'sort_order': 'asc', 'item_limit': 20}
2020-05-18T23:08:15.620677Z categories loaded              category_count=1579
2020-05-18T23:08:15.620947Z fetching parameters            category_id=112291 category_name=Transoptory url=/pl/katalog/transoptory_112291/
2020-05-18T23:08:17.121963Z fetching values                category_id=112291 category_name=Transoptory parameter_name=Ilość pinów
2020-05-18T23:08:17.148546Z values parsed                  category_id=112291 category_name=Transoptory count=13 parameter_name=Producent
2020-05-18T23:08:17.148946Z values parsed                  category_id=112291 category_name=Transoptory count=2 parameter_name=Typ elementu półprzewodnikowego
2020-05-18T23:08:17.149331Z values parsed                  category_id=112291 category_name=Transoptory count=2 parameter_name=Montaż
2020-05-18T23:08:17.150641Z values parsed                  category_id=112291 category_name=Transoptory count=18 parameter_name=Rodzaj wyjścia
2020-05-18T23:08:17.152724Z values parsed                  category_id=112291 category_name=Transoptory count=43 parameter_name=Obudowa
2020-05-18T23:08:17.153141Z values parsed                  category_id=112291 category_name=Transoptory count=4 parameter_name=Liczba kanałów
2020-05-18T23:08:17.170388Z values parsed                  category_id=112291 category_name=Transoptory count=28 parameter_name=Napięcie izolacji
2020-05-18T23:08:17.177809Z values parsed                  category_id=112291 category_name=Transoptory count=185 parameter_name=CTR@If
2020-05-18T23:08:17.218813Z values parsed                  category_id=112291 category_name=Transoptory count=87 parameter_name=Czas wyłączania
2020-05-18T23:08:17.263475Z values parsed                  category_id=112291 category_name=Transoptory count=91 parameter_name=Czas załączania
2020-05-18T23:08:17.275475Z values parsed                  category_id=112291 category_name=Transoptory count=27 parameter_name=Napięcie kolektor-emiter
2020-05-18T23:08:17.281487Z values parsed                  category_id=112291 category_name=Transoptory count=12 parameter_name=Prąd wyzwalania
2020-05-18T23:08:17.283907Z values parsed                  category_id=112291 category_name=Transoptory count=3 parameter_name=Napięcie wsteczne maks.
2020-05-18T23:08:17.286847Z values parsed                  category_id=112291 category_name=Transoptory count=5 parameter_name=Napięcie wyjściowe
2020-05-18T23:08:17.291586Z values parsed                  category_id=112291 category_name=Transoptory count=9 parameter_name=Prąd kolektora
2020-05-18T23:08:17.292023Z values parsed                  category_id=112291 category_name=Transoptory count=1 parameter_name=Rodzaj opakowania
2020-05-18T23:08:17.292513Z values parsed                  category_id=112291 category_name=Transoptory count=6 parameter_name=Opis transoptora
2020-05-18T23:08:17.292944Z values parsed                  category_id=112291 category_name=Transoptory count=4 parameter_name=Ilość pinów
2020-05-18T23:08:17.300431Z looking up parts               category_id=112291 category_name=Transoptory mapped_params=430:1549821,1444593,1444637,1444652,1444729,1444633,1548890,1444630,1444635,1548893 url=/pl/katalog/transoptory_112291/
2020-05-18T23:08:18.789986Z parsing product rows           category_id=112291 category_name=Transoptory count=22
Manufacturer                  Symbol        Description
----------------------------  ------------  ------------------------------------------------------------------
VISHAY                        SFH6156-1T    Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV
ON SEMICONDUCTOR (FAIRCHILD)  4N27SR2M      Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 7,5kV
ON SEMICONDUCTOR (FAIRCHILD)  4N27-F-SMD    Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 7,5kV
ON SEMICONDUCTOR (FAIRCHILD)  4N27SR2M      Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 7,5kV
ISOCOM                        4N26XSM       Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV
ISOCOM                        H11AV1XSM     Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV
ISOCOM                        SFH617A-2X    Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV; DIP4
ISOCOM                        SFH617A-4X    Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV; DIP4
ISOCOM                        SFH617A-2XSM  Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV; SO4
ISOCOM                        SFH617A-4-I   Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV; DIP4
ISOCOM                        SFH617A-4X    Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV; DIP4
ISOCOM                        TIL111XSM     Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV
ISOCOM                        CNY17-2XSM    Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV
ISOCOM                        CNY17F-2XSM   Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV
ON SEMICONDUCTOR (FAIRCHILD)  4N28M         Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 7,5kV; DIP6
ON SEMICONDUCTOR (FAIRCHILD)  4N30M         Transoptor; THT; Kanały: 1; Wyj: układ Darlingtona; Uizol: 5,25kV
ON SEMICONDUCTOR (FAIRCHILD)  4N36SM        Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 7,5kV
ON SEMICONDUCTOR (FAIRCHILD)  4N38M         Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 7,5kV; DIP6
ON SEMICONDUCTOR (FAIRCHILD)  4N26M         Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 7,5kV; DIP6
ISOCOM                        4N26X         Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV; DIP6
VISHAY                        CNY17G-2      Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV; DIP6
VISHAY                        SFH6156-1     Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV
(generic) ➜  greatriver git:(master) ✗ 
```

As you can see the -P flag is used to define constraints with a pretty self-explanatory syntac. Simple comparison operations are possible: - = < > and the tool handles units thanks to the https://github.com/hgrecco/pint module. For example, instead of 5kV you can specify a value of 5000V:

```
(generic) ➜  greatriver git:(master) ✗ bin/tme-search parts -c 112291 -P '"Napięcie izolacji" > "5000V"' 
2020-05-18T23:10:07.498729Z start                          config={'country_code': 'pl', 'language_code': 'en', 'base_url': 'https://www.tme.eu/', 'currency': 'USD', 'cmd': 'parts', 'cat_id': '112291', 'constraints': ['"Napięcie izolacji" > "5000V"'], 'sort_field': None, 'sort_order': 'asc', 'item_limit': 20}
2020-05-18T23:10:08.537121Z categories loaded              category_count=1579
2020-05-18T23:10:08.537325Z fetching parameters            category_id=112291 category_name=Transoptory url=/pl/katalog/transoptory_112291/
2020-05-18T23:10:10.163614Z fetching values                category_id=112291 category_name=Transoptory parameter_name=Ilość pinów
2020-05-18T23:10:10.189122Z values parsed                  category_id=112291 category_name=Transoptory count=13 parameter_name=Producent
2020-05-18T23:10:10.189558Z values parsed                  category_id=112291 category_name=Transoptory count=2 parameter_name=Typ elementu półprzewodnikowego
2020-05-18T23:10:10.189904Z values parsed                  category_id=112291 category_name=Transoptory count=2 parameter_name=Montaż
2020-05-18T23:10:10.190802Z values parsed                  category_id=112291 category_name=Transoptory count=18 parameter_name=Rodzaj wyjścia
2020-05-18T23:10:10.192584Z values parsed                  category_id=112291 category_name=Transoptory count=43 parameter_name=Obudowa
2020-05-18T23:10:10.193000Z values parsed                  category_id=112291 category_name=Transoptory count=4 parameter_name=Liczba kanałów
2020-05-18T23:10:10.211442Z values parsed                  category_id=112291 category_name=Transoptory count=28 parameter_name=Napięcie izolacji
2020-05-18T23:10:10.220585Z values parsed                  category_id=112291 category_name=Transoptory count=185 parameter_name=CTR@If
2020-05-18T23:10:10.268091Z values parsed                  category_id=112291 category_name=Transoptory count=87 parameter_name=Czas wyłączania
2020-05-18T23:10:10.317439Z values parsed                  category_id=112291 category_name=Transoptory count=91 parameter_name=Czas załączania
2020-05-18T23:10:10.334434Z values parsed                  category_id=112291 category_name=Transoptory count=27 parameter_name=Napięcie kolektor-emiter
2020-05-18T23:10:10.341528Z values parsed                  category_id=112291 category_name=Transoptory count=12 parameter_name=Prąd wyzwalania
2020-05-18T23:10:10.343274Z values parsed                  category_id=112291 category_name=Transoptory count=3 parameter_name=Napięcie wsteczne maks.
2020-05-18T23:10:10.346322Z values parsed                  category_id=112291 category_name=Transoptory count=5 parameter_name=Napięcie wyjściowe
2020-05-18T23:10:10.353794Z values parsed                  category_id=112291 category_name=Transoptory count=9 parameter_name=Prąd kolektora
2020-05-18T23:10:10.354345Z values parsed                  category_id=112291 category_name=Transoptory count=1 parameter_name=Rodzaj opakowania
2020-05-18T23:10:10.355083Z values parsed                  category_id=112291 category_name=Transoptory count=6 parameter_name=Opis transoptora
2020-05-18T23:10:10.355622Z values parsed                  category_id=112291 category_name=Transoptory count=4 parameter_name=Ilość pinów
2020-05-18T23:10:10.365020Z looking up parts               category_id=112291 category_name=Transoptory mapped_params=430:1549821,1444593,1444637,1444652,1444729,1444633,1548890,1444630,1444635,1548893 url=/pl/katalog/transoptory_112291/
2020-05-18T23:10:12.112667Z parsing product rows           category_id=112291 category_name=Transoptory count=22
Manufacturer                  Symbol        Description
----------------------------  ------------  ------------------------------------------------------------------
VISHAY                        SFH6156-1T    Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV
ON SEMICONDUCTOR (FAIRCHILD)  4N27SR2M      Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 7,5kV
ON SEMICONDUCTOR (FAIRCHILD)  4N27-F-SMD    Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 7,5kV
ON SEMICONDUCTOR (FAIRCHILD)  4N27SR2M      Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 7,5kV
ISOCOM                        4N26XSM       Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV
ISOCOM                        H11AV1XSM     Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV
ISOCOM                        SFH617A-2X    Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV; DIP4
ISOCOM                        SFH617A-4X    Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV; DIP4
ISOCOM                        SFH617A-2XSM  Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV; SO4
ISOCOM                        SFH617A-4-I   Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV; DIP4
ISOCOM                        SFH617A-4X    Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV; DIP4
ISOCOM                        TIL111XSM     Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV
ISOCOM                        CNY17-2XSM    Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV
ISOCOM                        CNY17F-2XSM   Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV
ON SEMICONDUCTOR (FAIRCHILD)  4N28M         Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 7,5kV; DIP6
ON SEMICONDUCTOR (FAIRCHILD)  4N30M         Transoptor; THT; Kanały: 1; Wyj: układ Darlingtona; Uizol: 5,25kV
ON SEMICONDUCTOR (FAIRCHILD)  4N36SM        Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 7,5kV
ON SEMICONDUCTOR (FAIRCHILD)  4N38M         Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 7,5kV; DIP6
ON SEMICONDUCTOR (FAIRCHILD)  4N26M         Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 7,5kV; DIP6
ISOCOM                        4N26X         Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV; DIP6
VISHAY                        CNY17G-2      Transoptor; THT; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV; DIP6
VISHAY                        SFH6156-1     Transoptor; SMD; Kanały: 1; Wyj: tranzystorowe; Uizol: 5,3kV
(generic) ➜  greatriver git:(master) ✗ 
```

Unfortunately, fetching the prices is not yet implemented due to the fact that the price information is fetched as Javascript code and it's not yet clear to 
me how to parse this in a simple way.

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
