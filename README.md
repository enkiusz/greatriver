# The Great River

Scripts used to automate searching for and purchase of certain products.


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
