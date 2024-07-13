Default settings with total optimizer timeout == 300 seconds

======================================================

$ pack.py -total-timeout=300 --match '
.state.self_discharge.assessment == "PASS" and 
.state.internal_resistance.v < 70 and 
(.props.tags.corrosion == true | not) and 
(.props.tags.precharge_fail == true | not) and 
(.props.tags.excessive_heat == true | not)' -a -S 10 -P 20

2021-10-03 17:32.58 [info     ] optimization finished
STR~4221857932	capa[sum   515 Ah, mean 51.53, stdev 13.17236 mAh (0.03 %)]	IR[max 1.92 mΩ, mean 1.84, stdev 0.04840 (2.63 %)]
	BL~2049587153	20P	capa[sum 51517 mAh, mean 2575.85 stdev 288.39 (11.2 %)]	IR[parallel 1.80 mΩ, mean 42.12, stdev 15.46 mΩ (36.7 %)]
	BL~1993787717	20P	capa[sum 51543 mAh, mean 2577.15 stdev 270.68 (10.5 %)]	IR[parallel 1.88 mΩ, mean 43.34, stdev 12.92 mΩ (29.8 %)]
	BL~6718782181	20P	capa[sum 51521 mAh, mean 2576.05 stdev 202.78 (7.9 %)]	IR[parallel 1.88 mΩ, mean 42.08, stdev 13.19 mΩ (31.3 %)]
	BL~0962442943	20P	capa[sum 51539 mAh, mean 2576.95 stdev 167.33 (6.5 %)]	IR[parallel 1.75 mΩ, mean 42.70, stdev 15.45 mΩ (36.2 %)]
	BL~6968793483	20P	capa[sum 51502 mAh, mean 2575.10 stdev 192.75 (7.5 %)]	IR[parallel 1.82 mΩ, mean 42.28, stdev 14.76 mΩ (34.9 %)]
	BL~7469909574	20P	capa[sum 51525 mAh, mean 2576.25 stdev 184.33 (7.2 %)]	IR[parallel 1.86 mΩ, mean 42.27, stdev 14.53 mΩ (34.4 %)]
	BL~6143836147	20P	capa[sum 51543 mAh, mean 2577.15 stdev 163.12 (6.3 %)]	IR[parallel 1.92 mΩ, mean 44.68, stdev 16.27 mΩ (36.4 %)]
	BL~5482356552	20P	capa[sum 51528 mAh, mean 2576.40 stdev 163.77 (6.4 %)]	IR[parallel 1.87 mΩ, mean 42.92, stdev 13.46 mΩ (31.4 %)]
	BL~9461878509	20P	capa[sum 51522 mAh, mean 2576.10 stdev 168.69 (6.5 %)]	IR[parallel 1.83 mΩ, mean 44.04, stdev 15.89 mΩ (36.1 %)]
	BL~3889874410	20P	capa[sum 51538 mAh, mean 2576.90 stdev 166.49 (6.5 %)]	IR[parallel 1.83 mΩ, mean 42.61, stdev 14.36 mΩ (33.7 %)]
2021-10-03 17:32.58 [info     ] pack layout                    energy_capacity=1.86 kWh
$

======================================================

$ pack.py -total-timeout=300 --match '
.state.self_discharge.assessment == "PASS" and 
.state.internal_resistance.v < 70 and 
(.props.tags.corrosion == true | not) and 
(.props.tags.precharge_fail == true | not) and 
(.props.tags.excessive_heat == true | not)' -a -S 10 -P 80

2021-10-03 17:51.46 [info     ] optimization finished
STR~6229373188	capa[sum  1738 Ah, mean 173.83, stdev 4.07704 mAh (0.00 %)]	IR[max 0.47 mΩ, mean 0.41, stdev 0.10415 (25.18 %)]
	BL~1115051327	80P	capa[sum 173840 mAh, mean 2173.00 stdev 328.04 (15.1 %)]	IR[parallel 0.44 mΩ, mean 40.39, stdev 13.97 mΩ (34.6 %)]
	BL~0357219578	80P	capa[sum 173835 mAh, mean 2172.94 stdev 327.35 (15.1 %)]	IR[parallel 0.42 mΩ, mean 40.50, stdev 14.97 mΩ (37.0 %)]
	BL~5306704346	80P	capa[sum 173833 mAh, mean 2172.91 stdev 292.21 (13.4 %)]	IR[parallel 0.45 mΩ, mean 41.08, stdev 13.99 mΩ (34.0 %)]
	BL~4727408492	80P	capa[sum 173828 mAh, mean 2172.85 stdev 292.03 (13.4 %)]	IR[parallel 0.44 mΩ, mean 41.64, stdev 15.58 mΩ (37.4 %)]
	BL~7811597008	80P	capa[sum 173840 mAh, mean 2173.00 stdev 289.26 (13.3 %)]	IR[parallel 0.47 mΩ, mean 43.64, stdev 14.73 mΩ (33.8 %)]
	BL~2902362666	80P	capa[sum 173836 mAh, mean 2172.95 stdev 290.31 (13.4 %)]	IR[parallel 0.44 mΩ, mean 41.86, stdev 15.06 mΩ (36.0 %)]
	BL~7328603387	80P	capa[sum 173835 mAh, mean 2172.94 stdev 291.25 (13.4 %)]	IR[parallel 0.12 mΩ, mean 45.80, stdev 15.16 mΩ (33.1 %)]
	BL~6473723074	80P	capa[sum 173829 mAh, mean 2172.86 stdev 285.85 (13.2 %)]	IR[parallel 0.45 mΩ, mean 43.09, stdev 15.28 mΩ (35.5 %)]
	BL~0871136791	80P	capa[sum 173835 mAh, mean 2172.94 stdev 285.64 (13.1 %)]	IR[parallel 0.45 mΩ, mean 42.89, stdev 15.32 mΩ (35.7 %)]
	BL~3487854730	80P	capa[sum 173831 mAh, mean 2172.89 stdev 285.00 (13.1 %)]	IR[parallel 0.44 mΩ, mean 41.54, stdev 15.62 mΩ (37.6 %)]
2021-10-03 17:51.46 [info     ] pack layout                    energy_capacity=6.26 kWh
$



======================================================

$ pack.py --total-timeout=300 --match '
.state.self_discharge.assessment == "PASS" and 
.state.internal_resistance.v < 70 and 
(.props.tags.corrosion == true | not) and 
(.props.tags.precharge_fail == true | not) and 
(.props.tags.excessive_heat == true | not)' -a -S 10 -P 160

2021-10-03 18:08.18 [info     ] optimization finished
STR~7129061209	capa[sum  2837 Ah, mean 283.69, stdev 2.95146 mAh (0.00 %)]	IR[max 0.21 mΩ, mean 0.11, stdev 0.04442 (40.86 %)]
	BL~7784340115	160P	capa[sum 283690 mAh, mean 1773.06 stdev 501.85 (28.3 %)]	IR[parallel 0.05 mΩ, mean 47.23, stdev 15.34 mΩ (32.5 %)]
	BL~6056695756	160P	capa[sum 283696 mAh, mean 1773.10 stdev 500.12 (28.2 %)]	IR[parallel 0.11 mΩ, mean 47.47, stdev 15.45 mΩ (32.5 %)]
	BL~6004749087	160P	capa[sum 283691 mAh, mean 1773.07 stdev 492.22 (27.8 %)]	IR[parallel 0.12 mΩ, mean 48.29, stdev 14.58 mΩ (30.2 %)]
	BL~5025546505	160P	capa[sum 283692 mAh, mean 1773.08 stdev 490.76 (27.7 %)]	IR[parallel 0.05 mΩ, mean 47.93, stdev 15.92 mΩ (33.2 %)]
	BL~9726838227	160P	capa[sum 283691 mAh, mean 1773.07 stdev 488.00 (27.5 %)]	IR[parallel 0.21 mΩ, mean 47.47, stdev 14.94 mΩ (31.5 %)]
	BL~0722678642	160P	capa[sum 283690 mAh, mean 1773.06 stdev 491.55 (27.7 %)]	IR[parallel 0.12 mΩ, mean 46.60, stdev 15.97 mΩ (34.3 %)]
	BL~8459982888	160P	capa[sum 283694 mAh, mean 1773.09 stdev 499.21 (28.2 %)]	IR[parallel 0.09 mΩ, mean 50.51, stdev 14.83 mΩ (29.4 %)]
	BL~7511610448	160P	capa[sum 283696 mAh, mean 1773.10 stdev 489.02 (27.6 %)]	IR[parallel 0.11 mΩ, mean 48.24, stdev 14.93 mΩ (31.0 %)]
	BL~4865235122	160P	capa[sum 283687 mAh, mean 1773.04 stdev 488.12 (27.5 %)]	IR[parallel 0.11 mΩ, mean 48.68, stdev 15.09 mΩ (31.0 %)]
	BL~6697189439	160P	capa[sum 283689 mAh, mean 1773.06 stdev 490.44 (27.7 %)]	IR[parallel 0.12 mΩ, mean 47.72, stdev 15.37 mΩ (32.2 %)]
2021-10-03 18:08.18 [info     ] pack layout                    energy_capacity=10.21 kWh
$


======================================================

$ pack.py --total-timeout=600 --match '
.state.self_discharge.assessment == "PASS" and 
.state.internal_resistance.v < 70 and 
(.props.tags.corrosion == true | not) and 
(.props.tags.precharge_fail == true | not) and 
(.props.tags.excessive_heat == true | not)' -a -S 10 -P 160


2021-10-03 18:40.25 [info     ] optimization finished
STR~9670586235	capa[sum  2838 Ah, mean 283.77, stdev 0.99443 mAh (0.00 %)]	IR[max 0.23 mΩ, mean 0.12, stdev 0.05470 (46.70 %)]
	BL~3051631587	160P	capa[sum 283769 mAh, mean 1773.56 stdev 499.03 (28.1 %)]	IR[parallel 0.08 mΩ, mean 48.90, stdev 14.56 mΩ (29.8 %)]
	BL~9422440483	160P	capa[sum 283768 mAh, mean 1773.55 stdev 493.42 (27.8 %)]	IR[parallel 0.11 mΩ, mean 47.88, stdev 15.39 mΩ (32.1 %)]
	BL~0957776005	160P	capa[sum 283769 mAh, mean 1773.56 stdev 494.68 (27.9 %)]	IR[parallel 0.12 mΩ, mean 48.18, stdev 14.96 mΩ (31.1 %)]
	BL~0819657120	160P	capa[sum 283769 mAh, mean 1773.56 stdev 491.05 (27.7 %)]	IR[parallel 0.05 mΩ, mean 47.02, stdev 16.79 mΩ (35.7 %)]
	BL~9962008393	160P	capa[sum 283768 mAh, mean 1773.55 stdev 491.61 (27.7 %)]	IR[parallel 0.23 mΩ, mean 48.18, stdev 14.45 mΩ (30.0 %)]
	BL~6105717955	160P	capa[sum 283769 mAh, mean 1773.56 stdev 489.22 (27.6 %)]	IR[parallel 0.16 mΩ, mean 46.61, stdev 15.57 mΩ (33.4 %)]
	BL~9396475745	160P	capa[sum 283771 mAh, mean 1773.57 stdev 489.07 (27.6 %)]	IR[parallel 0.04 mΩ, mean 48.03, stdev 15.65 mΩ (32.6 %)]
	BL~7940634967	160P	capa[sum 283770 mAh, mean 1773.56 stdev 488.91 (27.6 %)]	IR[parallel 0.15 mΩ, mean 47.53, stdev 15.33 mΩ (32.3 %)]
	BL~3527218112	160P	capa[sum 283768 mAh, mean 1773.55 stdev 494.25 (27.9 %)]	IR[parallel 0.12 mΩ, mean 49.90, stdev 14.40 mΩ (28.9 %)]
	BL~5948783643	160P	capa[sum 283768 mAh, mean 1773.55 stdev 496.92 (28.0 %)]	IR[parallel 0.12 mΩ, mean 47.70, stdev 15.16 mΩ (31.8 %)]
2021-10-03 18:40.25 [info     ] pack layout                    energy_capacity=10.22 kWh
$

======================================================

$ pack.py --total-timeout=300 --match '


.state.self_discharge.assessment == "PASS" and 
.state.internal_resistance.v < 70 and 
(.props.tags.corrosion == true | not) and 
(.props.tags.precharge_fail == true | not) and 
(.props.tags.excessive_heat == true | not)' -a -S 10 -P 240

2021-10-03 18:18.34 [info     ] optimization finished
STR~0292520919	capa[sum  2982 Ah, mean 298.19, stdev 2.48551 mAh (0.00 %)]	IR[max 0.03 mΩ, mean 0.02, stdev 0.00454 (19.43 %)]
	BL~2675235733	179P	capa[sum 298190 mAh, mean 1665.87 stdev 568.48 (34.1 %)]	IR[parallel 0.02 mΩ, mean 47.65, stdev 17.46 mΩ (36.6 %)]
	BL~2286979052	179P	capa[sum 298188 mAh, mean 1665.85 stdev 570.76 (34.3 %)]	IR[parallel 0.03 mΩ, mean 45.67, stdev 17.74 mΩ (38.9 %)]
	BL~7161769619	179P	capa[sum 298195 mAh, mean 1665.89 stdev 563.93 (33.9 %)]	IR[parallel 0.02 mΩ, mean 48.00, stdev 16.72 mΩ (34.8 %)]
	BL~2061459068	179P	capa[sum 298190 mAh, mean 1665.87 stdev 564.17 (33.9 %)]	IR[parallel 0.02 mΩ, mean 47.01, stdev 19.01 mΩ (40.4 %)]
	BL~3314178331	179P	capa[sum 298188 mAh, mean 1665.85 stdev 565.10 (33.9 %)]	IR[parallel 0.03 mΩ, mean 47.67, stdev 16.82 mΩ (35.3 %)]
	BL~2700279328	179P	capa[sum 298187 mAh, mean 1665.85 stdev 555.37 (33.3 %)]	IR[parallel 0.03 mΩ, mean 47.12, stdev 17.09 mΩ (36.3 %)]
	BL~9908303787	179P	capa[sum 298186 mAh, mean 1665.84 stdev 560.68 (33.7 %)]	IR[parallel 0.02 mΩ, mean 48.28, stdev 17.60 mΩ (36.5 %)]
	BL~1941752203	179P	capa[sum 298190 mAh, mean 1665.87 stdev 563.35 (33.8 %)]	IR[parallel 0.02 mΩ, mean 47.02, stdev 17.82 mΩ (37.9 %)]
	BL~5495887605	179P	capa[sum 298190 mAh, mean 1665.87 stdev 565.36 (33.9 %)]	IR[parallel 0.02 mΩ, mean 48.62, stdev 17.91 mΩ (36.8 %)]
	BL~3647591365	179P	capa[sum 298188 mAh, mean 1665.85 stdev 575.80 (34.6 %)]	IR[parallel 0.03 mΩ, mean 46.55, stdev 17.93 mΩ (38.5 %)]
2021-10-03 18:18.34 [info     ] pack layout                    energy_capacity=10.73 kWh
$

======================================================

pack.py --total-timeout=600 --match '
.state.self_discharge.assessment == "PASS" and 
.state.internal_resistance.v < 70 and 
(.props.tags.corrosion == true | not) and 
(.props.tags.precharge_fail == true | not) and 
(.props.tags.excessive_heat == true | not)' -a -S 10 -P 240

2021-10-03 18:29.42 [info     ] optimization finished
STR~7147020597	capa[sum  2982 Ah, mean 298.19, stdev 1.47573 mAh (0.00 %)]	IR[max 0.03 mΩ, mean 0.02, stdev 0.00380 (16.40 %)]
	BL~4041546020	179P	capa[sum 298188 mAh, mean 1665.85 stdev 567.11 (34.0 %)]	IR[parallel 0.02 mΩ, mean 47.70, stdev 17.10 mΩ (35.9 %)]
	BL~3038119675	179P	capa[sum 298189 mAh, mean 1665.86 stdev 564.72 (33.9 %)]	IR[parallel 0.03 mΩ, mean 45.62, stdev 17.69 mΩ (38.8 %)]
	BL~1263743997	179P	capa[sum 298190 mAh, mean 1665.87 stdev 561.18 (33.7 %)]	IR[parallel 0.02 mΩ, mean 48.87, stdev 16.57 mΩ (33.9 %)]
	BL~1048614756	179P	capa[sum 298191 mAh, mean 1665.87 stdev 567.29 (34.1 %)]	IR[parallel 0.02 mΩ, mean 48.24, stdev 18.92 mΩ (39.2 %)]
	BL~2178758196	179P	capa[sum 298190 mAh, mean 1665.87 stdev 562.70 (33.8 %)]	IR[parallel 0.03 mΩ, mean 47.29, stdev 17.61 mΩ (37.2 %)]
	BL~4519057550	179P	capa[sum 298189 mAh, mean 1665.86 stdev 567.93 (34.1 %)]	IR[parallel 0.03 mΩ, mean 47.15, stdev 17.53 mΩ (37.2 %)]
	BL~5967258592	179P	capa[sum 298191 mAh, mean 1665.87 stdev 563.94 (33.9 %)]	IR[parallel 0.02 mΩ, mean 48.14, stdev 17.28 mΩ (35.9 %)]
	BL~9414411096	179P	capa[sum 298187 mAh, mean 1665.85 stdev 566.99 (34.0 %)]	IR[parallel 0.02 mΩ, mean 46.48, stdev 17.91 mΩ (38.5 %)]
	BL~2354968838	179P	capa[sum 298190 mAh, mean 1665.87 stdev 564.00 (33.9 %)]	IR[parallel 0.02 mΩ, mean 47.95, stdev 17.47 mΩ (36.4 %)]
	BL~3726788487	179P	capa[sum 298187 mAh, mean 1665.85 stdev 567.33 (34.1 %)]	IR[parallel 0.03 mΩ, mean 46.15, stdev 17.96 mΩ (38.9 %)]
2021-10-03 18:29.42 [info     ] pack layout                    energy_capacity=10.73 kWh

======================================================

$ pack.py --match '.props.brand == "SAMSUNG" and .state.self_discharge.assessment == "PASS" and .props.tags.likely_fake == true and (.props.tags.corrosion == true | not) and (.props.tags.precharge_fail == true | not) and (.props.tags.excessive_heat == true | not)' -S 10 -

STR~9578084455	capa[sum   735 Ah, mean 73.45, stdev 0.73786 mAh (0.00 %)]	IR[max 0.05 mΩ, mean 0.04, stdev 0.00637 (17.48 %)]
	BL~1519794500	73P	capa[sum 73453 mAh, mean 1006.21 stdev 330.93 (32.9 %)]	IR[parallel 0.05 mΩ, mean 67.06, stdev 28.51 mΩ (42.5 %)]
	BL~0291671743	73P	capa[sum 73453 mAh, mean 1006.21 stdev 326.77 (32.5 %)]	IR[parallel 0.03 mΩ, mean 70.85, stdev 34.36 mΩ (48.5 %)]
	BL~9991207598	73P	capa[sum 73455 mAh, mean 1006.23 stdev 322.00 (32.0 %)]	IR[parallel 0.04 mΩ, mean 71.74, stdev 33.29 mΩ (46.4 %)]
	BL~5178284660	73P	capa[sum 73455 mAh, mean 1006.23 stdev 317.81 (31.6 %)]	IR[parallel 0.03 mΩ, mean 69.67, stdev 37.26 mΩ (53.5 %)]
	BL~7631827443	73P	capa[sum 73454 mAh, mean 1006.22 stdev 314.06 (31.2 %)]	IR[parallel 0.03 mΩ, mean 70.91, stdev 32.48 mΩ (45.8 %)]
	BL~8560279722	73P	capa[sum 73454 mAh, mean 1006.22 stdev 318.86 (31.7 %)]	IR[parallel 0.04 mΩ, mean 67.69, stdev 26.33 mΩ (38.9 %)]
	BL~2151580203	73P	capa[sum 73455 mAh, mean 1006.23 stdev 300.46 (29.9 %)]	IR[parallel 0.04 mΩ, mean 71.77, stdev 33.78 mΩ (47.1 %)]
	BL~3516213102	73P	capa[sum 73454 mAh, mean 1006.22 stdev 308.67 (30.7 %)]	IR[parallel 0.03 mΩ, mean 74.72, stdev 36.46 mΩ (48.8 %)]
	BL~0793121934	73P	capa[sum 73454 mAh, mean 1006.22 stdev 320.09 (31.8 %)]	IR[parallel 0.04 mΩ, mean 67.08, stdev 29.13 mΩ (43.4 %)]
	BL~5357031790	73P	capa[sum 73454 mAh, mean 1006.22 stdev 322.80 (32.1 %)]	IR[parallel 0.04 mΩ, mean 70.05, stdev 31.19 mΩ (44.5 %)]
2021-10-07 20:50.56 [info     ] pack layout                    energy_capacity=2.64 kWh
2021-10-07 20:50.56 [info     ] optimizer timeout
2021-10-07 20:50.56 [info     ] optimization finished
STR~5695852023	capa[sum   735 Ah, mean 73.45, stdev 0.73786 mAh (0.00 %)]	IR[max 0.05 mΩ, mean 0.04, stdev 0.00637 (17.48 %)]
	BL~1893262997	73P	capa[sum 73453 mAh, mean 1006.21 stdev 330.93 (32.9 %)]	IR[parallel 0.05 mΩ, mean 67.06, stdev 28.51 mΩ (42.5 %)]
	BL~2525937763	73P	capa[sum 73453 mAh, mean 1006.21 stdev 326.77 (32.5 %)]	IR[parallel 0.03 mΩ, mean 70.85, stdev 34.36 mΩ (48.5 %)]
	BL~1993074158	73P	capa[sum 73455 mAh, mean 1006.23 stdev 322.00 (32.0 %)]	IR[parallel 0.04 mΩ, mean 71.74, stdev 33.29 mΩ (46.4 %)]
	BL~7713221983	73P	capa[sum 73455 mAh, mean 1006.23 stdev 317.81 (31.6 %)]	IR[parallel 0.03 mΩ, mean 69.67, stdev 37.26 mΩ (53.5 %)]
	BL~6036858182	73P	capa[sum 73454 mAh, mean 1006.22 stdev 314.06 (31.2 %)]	IR[parallel 0.03 mΩ, mean 70.91, stdev 32.48 mΩ (45.8 %)]
	BL~3653452377	73P	capa[sum 73454 mAh, mean 1006.22 stdev 318.86 (31.7 %)]	IR[parallel 0.04 mΩ, mean 67.69, stdev 26.33 mΩ (38.9 %)]
	BL~3470524244	73P	capa[sum 73455 mAh, mean 1006.23 stdev 300.46 (29.9 %)]	IR[parallel 0.04 mΩ, mean 71.77, stdev 33.78 mΩ (47.1 %)]
	BL~2974059673	73P	capa[sum 73454 mAh, mean 1006.22 stdev 308.67 (30.7 %)]	IR[parallel 0.03 mΩ, mean 74.72, stdev 36.46 mΩ (48.8 %)]
	BL~0609487262	73P	capa[sum 73454 mAh, mean 1006.22 stdev 320.09 (31.8 %)]	IR[parallel 0.04 mΩ, mean 67.08, stdev 29.13 mΩ (43.4 %)]
	BL~6685618259	73P	capa[sum 73454 mAh, mean 1006.22 stdev 322.80 (32.1 %)]	IR[parallel 0.04 mΩ, mean 70.05, stdev 31.19 mΩ (44.5 %)]
2021-10-07 20:50.56 [info     ] pack layout                    energy_capacity=2.64 kWh
➜  greatriver git:(master) ✗ 

$ pack.py --match '.props.brand == "SAMSUNG" and .state.self_discharge.assessment == "PASS" and .props.tags.likely_fake == true and (.props.tags.corrosion == true | not) and (.props.tags.precharge_fail == true | not) and (.props.tags.excessive_heat == true | not)' -S 10 -

STR~5507226453	capa[sum   735 Ah, mean 73.45, stdev 0.87560 mAh (0.00 %)]	IR[max 0.06 mΩ, mean 0.04, stdev 0.00956 (25.62 %)]
	BL~4319066639	73P	capa[sum 73455 mAh, mean 1006.23 stdev 315.54 (31.4 %)]	IR[parallel 0.06 mΩ, mean 67.12, stdev 27.20 mΩ (40.5 %)]
	BL~7902423162	73P	capa[sum 73455 mAh, mean 1006.23 stdev 311.94 (31.0 %)]	IR[parallel 0.02 mΩ, mean 67.89, stdev 31.36 mΩ (46.2 %)]
	BL~3451139411	73P	capa[sum 73455 mAh, mean 1006.23 stdev 320.99 (31.9 %)]	IR[parallel 0.03 mΩ, mean 73.60, stdev 35.58 mΩ (48.3 %)]
	BL~9538601806	73P	capa[sum 73453 mAh, mean 1006.21 stdev 319.44 (31.7 %)]	IR[parallel 0.03 mΩ, mean 73.05, stdev 36.48 mΩ (49.9 %)]
	BL~5741516008	73P	capa[sum 73454 mAh, mean 1006.22 stdev 309.21 (30.7 %)]	IR[parallel 0.04 mΩ, mean 69.73, stdev 30.55 mΩ (43.8 %)]
	BL~2896554240	73P	capa[sum 73455 mAh, mean 1006.23 stdev 321.25 (31.9 %)]	IR[parallel 0.04 mΩ, mean 69.32, stdev 31.68 mΩ (45.7 %)]
	BL~7195061180	73P	capa[sum 73454 mAh, mean 1006.22 stdev 315.22 (31.3 %)]	IR[parallel 0.04 mΩ, mean 70.72, stdev 33.35 mΩ (47.2 %)]
	BL~8716725358	73P	capa[sum 73454 mAh, mean 1006.22 stdev 316.49 (31.5 %)]	IR[parallel 0.03 mΩ, mean 75.75, stdev 38.69 mΩ (51.1 %)]
	BL~4994490946	73P	capa[sum 73453 mAh, mean 1006.21 stdev 318.03 (31.6 %)]	IR[parallel 0.04 mΩ, mean 66.41, stdev 27.35 mΩ (41.2 %)]
	BL~9543602945	73P	capa[sum 73453 mAh, mean 1006.21 stdev 334.76 (33.3 %)]	IR[parallel 0.04 mΩ, mean 67.95, stdev 29.68 mΩ (43.7 %)]
2021-10-07 21:17.55 [info     ] pack layout                    energy_capacity=2.64 kWh
2021-10-07 21:17.55 [info     ] optimizer timeout
2021-10-07 21:17.55 [info     ] optimization finished
STR~0773646167	capa[sum   735 Ah, mean 73.45, stdev 0.87560 mAh (0.00 %)]	IR[max 0.06 mΩ, mean 0.04, stdev 0.00956 (25.62 %)]
	BL~6406648336	73P	capa[sum 73455 mAh, mean 1006.23 stdev 315.54 (31.4 %)]	IR[parallel 0.06 mΩ, mean 67.12, stdev 27.20 mΩ (40.5 %)]
	BL~1759349847	73P	capa[sum 73455 mAh, mean 1006.23 stdev 311.94 (31.0 %)]	IR[parallel 0.02 mΩ, mean 67.89, stdev 31.36 mΩ (46.2 %)]
	BL~5370706098	73P	capa[sum 73455 mAh, mean 1006.23 stdev 320.99 (31.9 %)]	IR[parallel 0.03 mΩ, mean 73.60, stdev 35.58 mΩ (48.3 %)]
	BL~6423078709	73P	capa[sum 73453 mAh, mean 1006.21 stdev 319.44 (31.7 %)]	IR[parallel 0.03 mΩ, mean 73.05, stdev 36.48 mΩ (49.9 %)]
	BL~1104086932	73P	capa[sum 73454 mAh, mean 1006.22 stdev 309.21 (30.7 %)]	IR[parallel 0.04 mΩ, mean 69.73, stdev 30.55 mΩ (43.8 %)]
	BL~6384212397	73P	capa[sum 73455 mAh, mean 1006.23 stdev 321.25 (31.9 %)]	IR[parallel 0.04 mΩ, mean 69.32, stdev 31.68 mΩ (45.7 %)]
	BL~7727451285	73P	capa[sum 73454 mAh, mean 1006.22 stdev 315.22 (31.3 %)]	IR[parallel 0.04 mΩ, mean 70.72, stdev 33.35 mΩ (47.2 %)]
	BL~7733910790	73P	capa[sum 73454 mAh, mean 1006.22 stdev 316.49 (31.5 %)]	IR[parallel 0.03 mΩ, mean 75.75, stdev 38.69 mΩ (51.1 %)]
	BL~8041882450	73P	capa[sum 73453 mAh, mean 1006.21 stdev 318.03 (31.6 %)]	IR[parallel 0.04 mΩ, mean 66.41, stdev 27.35 mΩ (41.2 %)]
	BL~8425763802	73P	capa[sum 73453 mAh, mean 1006.21 stdev 334.76 (33.3 %)]	IR[parallel 0.04 mΩ, mean 67.95, stdev 29.68 mΩ (43.7 %)]
2021-10-07 21:17.55 [info     ] pack layout                    energy_capacity=2.64 kWh
➜  greatriver git:(master) ✗ 

$ pack.py --match '.props.brand == "SAMSUNG" and .state.self_discharge.assessment == "PASS" and .props.tags.likely_fake == true and (.props.tags.corrosion == true | not) and (.props.tags.precharge_fail == true | not) and (.props.tags.excessive_heat == true | not)' -S 10 -

STR~6287296502	capa[sum   735 Ah, mean 73.45, stdev 0.87560 mAh (0.00 %)]	IR[max 0.04 mΩ, mean 0.04, stdev 0.00548 (15.14 %)]
	BL~2093708810	73P	capa[sum 73453 mAh, mean 1006.21 stdev 316.26 (31.4 %)]	IR[parallel 0.03 mΩ, mean 70.71, stdev 31.37 mΩ (44.4 %)]
	BL~1602354286	73P	capa[sum 73453 mAh, mean 1006.21 stdev 315.06 (31.3 %)]	IR[parallel 0.03 mΩ, mean 69.07, stdev 30.65 mΩ (44.4 %)]
	BL~8185216162	73P	capa[sum 73454 mAh, mean 1006.22 stdev 320.71 (31.9 %)]	IR[parallel 0.04 mΩ, mean 72.63, stdev 33.36 mΩ (45.9 %)]
	BL~9050760903	73P	capa[sum 73455 mAh, mean 1006.23 stdev 315.26 (31.3 %)]	IR[parallel 0.04 mΩ, mean 71.29, stdev 36.04 mΩ (50.6 %)]
	BL~8608069086	73P	capa[sum 73454 mAh, mean 1006.22 stdev 314.86 (31.3 %)]	IR[parallel 0.03 mΩ, mean 72.34, stdev 34.66 mΩ (47.9 %)]
	BL~1557360663	73P	capa[sum 73454 mAh, mean 1006.22 stdev 314.77 (31.3 %)]	IR[parallel 0.04 mΩ, mean 66.47, stdev 25.26 mΩ (38.0 %)]
	BL~1228370779	73P	capa[sum 73454 mAh, mean 1006.22 stdev 315.55 (31.4 %)]	IR[parallel 0.04 mΩ, mean 68.68, stdev 32.83 mΩ (47.8 %)]
	BL~1019570956	73P	capa[sum 73456 mAh, mean 1006.25 stdev 327.11 (32.5 %)]	IR[parallel 0.03 mΩ, mean 74.84, stdev 38.95 mΩ (52.0 %)]
	BL~2402888858	73P	capa[sum 73454 mAh, mean 1006.22 stdev 319.35 (31.7 %)]	IR[parallel 0.04 mΩ, mean 67.08, stdev 27.68 mΩ (41.3 %)]
	BL~0333681096	73P	capa[sum 73454 mAh, mean 1006.22 stdev 324.35 (32.2 %)]	IR[parallel 0.04 mΩ, mean 68.44, stdev 31.35 mΩ (45.8 %)]
2021-10-07 21:23.13 [info     ] pack layout                    energy_capacity=2.64 kWh
2021-10-07 21:23.13 [info     ] optimizer timeout
2021-10-07 21:23.13 [info     ] optimization finished
STR~3897717818	capa[sum   735 Ah, mean 73.45, stdev 0.87560 mAh (0.00 %)]	IR[max 0.04 mΩ, mean 0.04, stdev 0.00548 (15.14 %)]
	BL~5124149863	73P	capa[sum 73453 mAh, mean 1006.21 stdev 316.26 (31.4 %)]	IR[parallel 0.03 mΩ, mean 70.71, stdev 31.37 mΩ (44.4 %)]
	BL~9264969583	73P	capa[sum 73453 mAh, mean 1006.21 stdev 315.06 (31.3 %)]	IR[parallel 0.03 mΩ, mean 69.07, stdev 30.65 mΩ (44.4 %)]
	BL~0080407525	73P	capa[sum 73454 mAh, mean 1006.22 stdev 320.71 (31.9 %)]	IR[parallel 0.04 mΩ, mean 72.63, stdev 33.36 mΩ (45.9 %)]
	BL~2714298088	73P	capa[sum 73455 mAh, mean 1006.23 stdev 315.26 (31.3 %)]	IR[parallel 0.04 mΩ, mean 71.29, stdev 36.04 mΩ (50.6 %)]
	BL~9461355682	73P	capa[sum 73454 mAh, mean 1006.22 stdev 314.86 (31.3 %)]	IR[parallel 0.03 mΩ, mean 72.34, stdev 34.66 mΩ (47.9 %)]
	BL~8903347177	73P	capa[sum 73454 mAh, mean 1006.22 stdev 314.77 (31.3 %)]	IR[parallel 0.04 mΩ, mean 66.47, stdev 25.26 mΩ (38.0 %)]
	BL~5609007881	73P	capa[sum 73454 mAh, mean 1006.22 stdev 315.55 (31.4 %)]	IR[parallel 0.04 mΩ, mean 68.68, stdev 32.83 mΩ (47.8 %)]
	BL~9758336418	73P	capa[sum 73456 mAh, mean 1006.25 stdev 327.11 (32.5 %)]	IR[parallel 0.03 mΩ, mean 74.84, stdev 38.95 mΩ (52.0 %)]
	BL~6986011224	73P	capa[sum 73454 mAh, mean 1006.22 stdev 319.35 (31.7 %)]	IR[parallel 0.04 mΩ, mean 67.08, stdev 27.68 mΩ (41.3 %)]
	BL~6469620497	73P	capa[sum 73454 mAh, mean 1006.22 stdev 324.35 (32.2 %)]	IR[parallel 0.04 mΩ, mean 68.44, stdev 31.35 mΩ (45.8 %)]
2021-10-07 21:23.13 [info     ] pack layout                    energy_capacity=2.64 kWh
➜  greatriver git:(master) ✗ 

$ pack.py --match '.props.brand == "SAMSUNG" and .state.self_discharge.assessment == "PASS" and .props.tags.likely_fake == true and (.props.tags.corrosion == true | not) and (.props.tags.precharge_fail == true | not) and (.props.tags.excessive_heat == true | not)' -S 10 -

STR~6287296502	capa[sum   735 Ah, mean 73.45, stdev 0.87560 mAh (0.00 %)]	IR[max 0.04 mΩ, mean 0.04, stdev 0.00548 (15.14 %)]
	BL~2093708810	73P	capa[sum 73453 mAh, mean 1006.21 stdev 316.26 (31.4 %)]	IR[parallel 0.03 mΩ, mean 70.71, stdev 31.37 mΩ (44.4 %)]
	BL~1602354286	73P	capa[sum 73453 mAh, mean 1006.21 stdev 315.06 (31.3 %)]	IR[parallel 0.03 mΩ, mean 69.07, stdev 30.65 mΩ (44.4 %)]
	BL~8185216162	73P	capa[sum 73454 mAh, mean 1006.22 stdev 320.71 (31.9 %)]	IR[parallel 0.04 mΩ, mean 72.63, stdev 33.36 mΩ (45.9 %)]
	BL~9050760903	73P	capa[sum 73455 mAh, mean 1006.23 stdev 315.26 (31.3 %)]	IR[parallel 0.04 mΩ, mean 71.29, stdev 36.04 mΩ (50.6 %)]
	BL~8608069086	73P	capa[sum 73454 mAh, mean 1006.22 stdev 314.86 (31.3 %)]	IR[parallel 0.03 mΩ, mean 72.34, stdev 34.66 mΩ (47.9 %)]
	BL~1557360663	73P	capa[sum 73454 mAh, mean 1006.22 stdev 314.77 (31.3 %)]	IR[parallel 0.04 mΩ, mean 66.47, stdev 25.26 mΩ (38.0 %)]
	BL~1228370779	73P	capa[sum 73454 mAh, mean 1006.22 stdev 315.55 (31.4 %)]	IR[parallel 0.04 mΩ, mean 68.68, stdev 32.83 mΩ (47.8 %)]
	BL~1019570956	73P	capa[sum 73456 mAh, mean 1006.25 stdev 327.11 (32.5 %)]	IR[parallel 0.03 mΩ, mean 74.84, stdev 38.95 mΩ (52.0 %)]
	BL~2402888858	73P	capa[sum 73454 mAh, mean 1006.22 stdev 319.35 (31.7 %)]	IR[parallel 0.04 mΩ, mean 67.08, stdev 27.68 mΩ (41.3 %)]
	BL~0333681096	73P	capa[sum 73454 mAh, mean 1006.22 stdev 324.35 (32.2 %)]	IR[parallel 0.04 mΩ, mean 68.44, stdev 31.35 mΩ (45.8 %)]
2021-10-07 21:23.13 [info     ] pack layout                    energy_capacity=2.64 kWh
2021-10-07 21:23.13 [info     ] optimizer timeout
2021-10-07 21:23.13 [info     ] optimization finished
STR~3897717818	capa[sum   735 Ah, mean 73.45, stdev 0.87560 mAh (0.00 %)]	IR[max 0.04 mΩ, mean 0.04, stdev 0.00548 (15.14 %)]
	BL~5124149863	73P	capa[sum 73453 mAh, mean 1006.21 stdev 316.26 (31.4 %)]	IR[parallel 0.03 mΩ, mean 70.71, stdev 31.37 mΩ (44.4 %)]
	BL~9264969583	73P	capa[sum 73453 mAh, mean 1006.21 stdev 315.06 (31.3 %)]	IR[parallel 0.03 mΩ, mean 69.07, stdev 30.65 mΩ (44.4 %)]
	BL~0080407525	73P	capa[sum 73454 mAh, mean 1006.22 stdev 320.71 (31.9 %)]	IR[parallel 0.04 mΩ, mean 72.63, stdev 33.36 mΩ (45.9 %)]
	BL~2714298088	73P	capa[sum 73455 mAh, mean 1006.23 stdev 315.26 (31.3 %)]	IR[parallel 0.04 mΩ, mean 71.29, stdev 36.04 mΩ (50.6 %)]
	BL~9461355682	73P	capa[sum 73454 mAh, mean 1006.22 stdev 314.86 (31.3 %)]	IR[parallel 0.03 mΩ, mean 72.34, stdev 34.66 mΩ (47.9 %)]
	BL~8903347177	73P	capa[sum 73454 mAh, mean 1006.22 stdev 314.77 (31.3 %)]	IR[parallel 0.04 mΩ, mean 66.47, stdev 25.26 mΩ (38.0 %)]
	BL~5609007881	73P	capa[sum 73454 mAh, mean 1006.22 stdev 315.55 (31.4 %)]	IR[parallel 0.04 mΩ, mean 68.68, stdev 32.83 mΩ (47.8 %)]
	BL~9758336418	73P	capa[sum 73456 mAh, mean 1006.25 stdev 327.11 (32.5 %)]	IR[parallel 0.03 mΩ, mean 74.84, stdev 38.95 mΩ (52.0 %)]
	BL~6986011224	73P	capa[sum 73454 mAh, mean 1006.22 stdev 319.35 (31.7 %)]	IR[parallel 0.04 mΩ, mean 67.08, stdev 27.68 mΩ (41.3 %)]
	BL~6469620497	73P	capa[sum 73454 mAh, mean 1006.22 stdev 324.35 (32.2 %)]	IR[parallel 0.04 mΩ, mean 68.44, stdev 31.35 mΩ (45.8 %)]
2021-10-07 21:23.13 [info     ] pack layout                    energy_capacity=2.64 kWh
➜  greatriver git:(master) ✗ 

========
optimize IR stdev and capa stdev separately

$ pack.py --match '.props.brand == "SAMSUNG" and .state.self_discharge.assessment == "PASS" and .props.tags.likely_fake == true and (.props.tags.corrosion == true | not) and (.props.tags.precharge_fail == true | not) and (.props.tags.excessive_heat == true | not)' -S 10 -

STR~4944009088	capa[sum   735 Ah, mean 73.45, stdev 6.95142 mAh (0.01 %)]	IR[max 0.04 mΩ, mean 0.04, stdev 0.00503 (13.93 %)]
	BL~2776994923	73P	capa[sum 73459 mAh, mean 1006.29 stdev 328.65 (32.7 %)]	IR[parallel 0.04 mΩ, mean 70.51, stdev 30.46 mΩ (43.2 %)]
	BL~7492475414	73P	capa[sum 73448 mAh, mean 1006.14 stdev 329.30 (32.7 %)]	IR[parallel 0.03 mΩ, mean 68.74, stdev 32.13 mΩ (46.7 %)]
	BL~2534402988	73P	capa[sum 73451 mAh, mean 1006.18 stdev 316.29 (31.4 %)]	IR[parallel 0.04 mΩ, mean 71.03, stdev 32.55 mΩ (45.8 %)]
	BL~1196407542	73P	capa[sum 73442 mAh, mean 1006.05 stdev 317.26 (31.5 %)]	IR[parallel 0.04 mΩ, mean 73.42, stdev 37.34 mΩ (50.9 %)]
	BL~8578398035	73P	capa[sum 73453 mAh, mean 1006.21 stdev 317.75 (31.6 %)]	IR[parallel 0.03 mΩ, mean 68.34, stdev 30.60 mΩ (44.8 %)]
	BL~7312166219	73P	capa[sum 73454 mAh, mean 1006.22 stdev 314.70 (31.3 %)]	IR[parallel 0.04 mΩ, mean 69.78, stdev 30.27 mΩ (43.4 %)]
	BL~7441770238	73P	capa[sum 73459 mAh, mean 1006.29 stdev 312.30 (31.0 %)]	IR[parallel 0.03 mΩ, mean 71.01, stdev 35.23 mΩ (49.6 %)]
	BL~7713045564	73P	capa[sum 73461 mAh, mean 1006.32 stdev 316.62 (31.5 %)]	IR[parallel 0.04 mΩ, mean 71.85, stdev 34.39 mΩ (47.9 %)]
	BL~4963611841	73P	capa[sum 73465 mAh, mean 1006.37 stdev 310.73 (30.9 %)]	IR[parallel 0.03 mΩ, mean 67.97, stdev 28.68 mΩ (42.2 %)]
	BL~9484431534	73P	capa[sum 73449 mAh, mean 1006.15 stdev 319.40 (31.7 %)]	IR[parallel 0.04 mΩ, mean 68.90, stdev 32.29 mΩ (46.9 %)]
2021-10-07 21:46.33 [info     ] pack layout                    energy_capacity=2.64 kWh
2021-10-07 21:46.34 [info     ] progress                       iterations=3113
2021-10-07 21:46.36 [info     ] progress                       iterations=3226
2021-10-07 21:46.38 [info     ] progress                       iterations=3339
2021-10-07 21:46.40 [info     ] progress                       iterations=3452
2021-10-07 21:46.42 [info     ] progress                       iterations=3565
2021-10-07 21:46.43 [info     ] optimizer timeout
2021-10-07 21:46.43 [info     ] optimization finished
STR~9703572584	capa[sum   735 Ah, mean 73.45, stdev 4.40833 mAh (0.01 %)]	IR[max 0.04 mΩ, mean 0.04, stdev 0.00502 (13.93 %)]
	BL~7414664695	73P	capa[sum 73459 mAh, mean 1006.29 stdev 328.65 (32.7 %)]	IR[parallel 0.04 mΩ, mean 70.51, stdev 30.46 mΩ (43.2 %)]
	BL~2307079377	73P	capa[sum 73448 mAh, mean 1006.14 stdev 329.30 (32.7 %)]	IR[parallel 0.03 mΩ, mean 68.74, stdev 32.13 mΩ (46.7 %)]
	BL~1387963122	73P	capa[sum 73451 mAh, mean 1006.18 stdev 316.29 (31.4 %)]	IR[parallel 0.04 mΩ, mean 71.03, stdev 32.55 mΩ (45.8 %)]
	BL~7395805627	73P	capa[sum 73452 mAh, mean 1006.19 stdev 317.38 (31.5 %)]	IR[parallel 0.04 mΩ, mean 73.30, stdev 37.41 mΩ (51.0 %)]
	BL~7164536353	73P	capa[sum 73453 mAh, mean 1006.21 stdev 317.75 (31.6 %)]	IR[parallel 0.03 mΩ, mean 68.34, stdev 30.60 mΩ (44.8 %)]
	BL~8461656097	73P	capa[sum 73454 mAh, mean 1006.22 stdev 314.70 (31.3 %)]	IR[parallel 0.04 mΩ, mean 69.78, stdev 30.27 mΩ (43.4 %)]
	BL~3260516172	73P	capa[sum 73459 mAh, mean 1006.29 stdev 312.30 (31.0 %)]	IR[parallel 0.03 mΩ, mean 71.01, stdev 35.23 mΩ (49.6 %)]
	BL~6183423061	73P	capa[sum 73461 mAh, mean 1006.32 stdev 316.62 (31.5 %)]	IR[parallel 0.04 mΩ, mean 71.85, stdev 34.39 mΩ (47.9 %)]
	BL~1511304167	73P	capa[sum 73455 mAh, mean 1006.23 stdev 310.60 (30.9 %)]	IR[parallel 0.03 mΩ, mean 68.10, stdev 28.62 mΩ (42.0 %)]
	BL~5415821206	73P	capa[sum 73449 mAh, mean 1006.15 stdev 319.40 (31.7 %)]	IR[parallel 0.04 mΩ, mean 68.90, stdev 32.29 mΩ (46.9 %)]
2021-10-07 21:46.43 [info     ] pack layout                    energy_capacity=2.64 kWh
➜  greatriver git:(master) ✗ 

========
perform 5 swaps instead of one

$ pack.py --match '.props.brand == "SAMSUNG" and .state.self_discharge.assessment == "PASS" and .props.tags.likely_fake == true and (.props.tags.corrosion == true | not) and (.props.tags.precharge_fail == true | not) and (.props.tags.excessive_heat == true | not)' -S 10 -a


STR~1931735687	capa[sum   735 Ah, mean 73.45, stdev 86.28306 mAh (0.12 %)]	IR[max 0.04 mΩ, mean 0.04, stdev 0.00392 (10.96 %)]
	BL~4340021099	73P	capa[sum 73533 mAh, mean 1007.30 stdev 323.80 (32.1 %)]	IR[parallel 0.04 mΩ, mean 69.04, stdev 31.17 mΩ (45.1 %)]
	BL~5052293186	73P	capa[sum 73345 mAh, mean 1004.73 stdev 320.70 (31.9 %)]	IR[parallel 0.03 mΩ, mean 69.47, stdev 30.58 mΩ (44.0 %)]
	BL~3960388940	73P	capa[sum 73448 mAh, mean 1006.14 stdev 329.03 (32.7 %)]	IR[parallel 0.04 mΩ, mean 73.45, stdev 35.79 mΩ (48.7 %)]
	BL~9142552195	73P	capa[sum 73309 mAh, mean 1004.23 stdev 323.31 (32.2 %)]	IR[parallel 0.04 mΩ, mean 72.92, stdev 37.72 mΩ (51.7 %)]
	BL~3450673188	73P	capa[sum 73537 mAh, mean 1007.36 stdev 300.96 (29.9 %)]	IR[parallel 0.03 mΩ, mean 71.40, stdev 33.20 mΩ (46.5 %)]
	BL~1886084653	73P	capa[sum 73549 mAh, mean 1007.52 stdev 318.12 (31.6 %)]	IR[parallel 0.03 mΩ, mean 68.32, stdev 28.80 mΩ (42.2 %)]
	BL~0814046953	73P	capa[sum 73421 mAh, mean 1005.77 stdev 312.98 (31.1 %)]	IR[parallel 0.04 mΩ, mean 72.88, stdev 35.32 mΩ (48.5 %)]
	BL~1936973233	73P	capa[sum 73406 mAh, mean 1005.56 stdev 295.19 (29.4 %)]	IR[parallel 0.04 mΩ, mean 69.46, stdev 30.23 mΩ (43.5 %)]
	BL~3503694321	73P	capa[sum 73546 mAh, mean 1007.48 stdev 298.74 (29.7 %)]	IR[parallel 0.03 mΩ, mean 66.00, stdev 27.94 mΩ (42.3 %)]
	BL~9258379711	73P	capa[sum 73447 mAh, mean 1006.12 stdev 356.21 (35.4 %)]	IR[parallel 0.03 mΩ, mean 68.62, stdev 32.33 mΩ (47.1 %)]
2021-10-07 23:10.31 [info     ] pack layout                    energy_capacity=2.64 kWh
2021-10-07 23:10.32 [info     ] progress                       iterations=2939
2021-10-07 23:10.32 [info     ] progress                       iterations=3000
2021-10-07 23:10.34 [info     ] progress                       iterations=3318
2021-10-07 23:10.36 [info     ] progress                       iterations=3635
2021-10-07 23:10.38 [info     ] progress                       iterations=3951
2021-10-07 23:10.38 [info     ] progress                       iterations=4000
2021-10-07 23:10.40 [info     ] progress                       iterations=4318
2021-10-07 23:10.41 [info     ] optimizer timeout
2021-10-07 23:10.41 [info     ] optimization finished
STR~3496492031	capa[sum   735 Ah, mean 73.45, stdev 78.66730 mAh (0.11 %)]	IR[max 0.04 mΩ, mean 0.04, stdev 0.00392 (10.96 %)]
	BL~0011495436	73P	capa[sum 73533 mAh, mean 1007.30 stdev 323.80 (32.1 %)]	IR[parallel 0.04 mΩ, mean 69.04, stdev 31.17 mΩ (45.1 %)]
	BL~6883673161	73P	capa[sum 73438 mAh, mean 1006.00 stdev 320.32 (31.8 %)]	IR[parallel 0.03 mΩ, mean 69.53, stdev 30.57 mΩ (44.0 %)]
	BL~5020202926	73P	capa[sum 73448 mAh, mean 1006.14 stdev 329.03 (32.7 %)]	IR[parallel 0.04 mΩ, mean 73.45, stdev 35.79 mΩ (48.7 %)]
	BL~5096815221	73P	capa[sum 73295 mAh, mean 1004.04 stdev 323.38 (32.2 %)]	IR[parallel 0.04 mΩ, mean 72.11, stdev 37.22 mΩ (51.6 %)]
	BL~2342363501	73P	capa[sum 73445 mAh, mean 1006.10 stdev 301.07 (29.9 %)]	IR[parallel 0.03 mΩ, mean 71.43, stdev 33.20 mΩ (46.5 %)]
	BL~0964152636	73P	capa[sum 73563 mAh, mean 1007.71 stdev 318.04 (31.6 %)]	IR[parallel 0.03 mΩ, mean 69.13, stdev 29.55 mΩ (42.8 %)]
	BL~3178921588	73P	capa[sum 73421 mAh, mean 1005.77 stdev 312.98 (31.1 %)]	IR[parallel 0.04 mΩ, mean 72.88, stdev 35.32 mΩ (48.5 %)]
	BL~3828574120	73P	capa[sum 73406 mAh, mean 1005.56 stdev 295.19 (29.4 %)]	IR[parallel 0.04 mΩ, mean 69.46, stdev 30.23 mΩ (43.5 %)]
	BL~5022163143	73P	capa[sum 73546 mAh, mean 1007.48 stdev 298.74 (29.7 %)]	IR[parallel 0.03 mΩ, mean 66.00, stdev 27.94 mΩ (42.3 %)]
	BL~1998989309	73P	capa[sum 73446 mAh, mean 1006.11 stdev 356.47 (35.4 %)]	IR[parallel 0.03 mΩ, mean 68.53, stdev 32.33 mΩ (47.2 %)]
2021-10-07 23:10.41 [info     ] pack layout                    energy_capacity=2.64 kWh
➜  greatriver git:(master) ✗ 

➜  ~ pack.py --match '.state.self_discharge.assessment == "PASS" and ((.props.brand == "SAMSUNG" and .props.tags.likely_fake == true) or .props.tags.noname == true) and (.props.tags.corrosion == true | not) and (.props.tags.precharge_fail == true | not) and (.props.tags.excessive_heat == true | not) and .state.internal_resistance.v < 110' -S 10 -a

STR~0783121006	capa[sum   920 Ah, mean 92.02, stdev 1590.49984 mAh (1.73 %)]	IR[max 0.79 mΩ, mean 0.77, stdev 0.01574 (2.05 %)]
	BL~4878908573	81P	capa[sum 91057 mAh, mean 1124.16 stdev 371.98 (33.1 %)]	IR[parallel 0.77 mΩ, mean 66.62, stdev 14.50 mΩ (21.8 %)]
	BL~1854442559	81P	capa[sum 92593 mAh, mean 1143.12 stdev 361.98 (31.7 %)]	IR[parallel 0.76 mΩ, mean 65.72, stdev 14.30 mΩ (21.8 %)]
	BL~3418197688	81P	capa[sum 91547 mAh, mean 1130.21 stdev 359.80 (31.8 %)]	IR[parallel 0.76 mΩ, mean 65.23, stdev 14.19 mΩ (21.8 %)]
	BL~7166902130	81P	capa[sum 90182 mAh, mean 1113.36 stdev 374.06 (33.6 %)]	IR[parallel 0.79 mΩ, mean 68.62, stdev 14.91 mΩ (21.7 %)]
	BL~9866488823	81P	capa[sum 94588 mAh, mean 1167.75 stdev 375.87 (32.2 %)]	IR[parallel 0.75 mΩ, mean 64.76, stdev 14.01 mΩ (21.6 %)]
	BL~4707750159	81P	capa[sum 93085 mAh, mean 1149.20 stdev 371.97 (32.4 %)]	IR[parallel 0.77 mΩ, mean 66.14, stdev 14.37 mΩ (21.7 %)]
	BL~2318557251	81P	capa[sum 90479 mAh, mean 1117.02 stdev 325.72 (29.2 %)]	IR[parallel 0.76 mΩ, mean 65.57, stdev 14.27 mΩ (21.8 %)]
	BL~6977988664	81P	capa[sum 94392 mAh, mean 1165.33 stdev 356.73 (30.6 %)]	IR[parallel 0.75 mΩ, mean 64.47, stdev 14.03 mΩ (21.8 %)]
	BL~9147059487	81P	capa[sum 90567 mAh, mean 1118.11 stdev 316.44 (28.3 %)]	IR[parallel 0.78 mΩ, mean 66.02, stdev 14.37 mΩ (21.8 %)]
	BL~0339350970	81P	capa[sum 91758 mAh, mean 1132.81 stdev 338.36 (29.9 %)]	IR[parallel 0.79 mΩ, mean 66.85, stdev 14.52 mΩ (21.7 %)]


➜  greatriver git:(master) ✗ pack.py --match '.state.self_discharge.assessment == "PASS" and .state.usable_capacity != null and .state.internal_resistance != null and (.props.tags.workflow_failure == true | not) and (.props.tags.precharge_fail == true | not) and (.props.tags.excessive_heat == true | not) and .path == "/STOCK/RACK~0768983590/" and ((.props.brand == "SAMSUNG" and .props.tags.likely_fake == true) or .props.tags.noname == true) and .state.internal_resistance.v < 110' -S 10 -P 80 -a

Initial layout:
2021-11-12 21:38.59 [info     ] string layout                  P=[80, 80, 80, 80, 80, 80, 80, 80, 80, 80] S=10 block_capacity_mean=102.14 Ah block_ir_mean=0.68 mΩ cells=800 energy_capacity=3.7 kWh interblock_capacity_stdev=0.48 % interblock_ir_stdev=3.07 % intrablock_ir_stdev_max=28.19 %

Final layout:
2021-11-12 21:58.57 [info     ] optimization finished
STR~2689936470	10S	capa[sum   988 Ah, mean 98.81, stdev 1413.16686 mAh (1.43 %)]	IR[max 0.73 mΩ, mean 0.70, stdev 0.01997 (2.87 %)]
	BL~2418779294	80P	capa[sum 96663 mAh, mean 1208.29 stdev 401.08 (33.2 %)]	IR[parallel 0.69 mΩ, mean 61.57, stdev 14.49 mΩ (23.5 %)]
	BL~5918828483	80P	capa[sum 97689 mAh, mean 1221.11 stdev 356.89 (29.2 %)]	IR[parallel 0.69 mΩ, mean 61.32, stdev 13.86 mΩ (22.6 %)]
	BL~9356836827	80P	capa[sum 100354 mAh, mean 1254.43 stdev 428.20 (34.1 %)]	IR[parallel 0.71 mΩ, mean 63.92, stdev 15.12 mΩ (23.7 %)]
	BL~0785313403	80P	capa[sum 98547 mAh, mean 1231.84 stdev 384.27 (31.2 %)]	IR[parallel 0.71 mΩ, mean 62.50, stdev 14.78 mΩ (23.7 %)]
	BL~4668536265	80P	capa[sum 99213 mAh, mean 1240.16 stdev 383.49 (30.9 %)]	IR[parallel 0.68 mΩ, mean 59.75, stdev 14.10 mΩ (23.6 %)]
	BL~9291384009	80P	capa[sum 97373 mAh, mean 1217.16 stdev 355.78 (29.2 %)]	IR[parallel 0.69 mΩ, mean 60.46, stdev 13.56 mΩ (22.4 %)]
	BL~9427614002	80P	capa[sum 100438 mAh, mean 1255.47 stdev 370.94 (29.5 %)]	IR[parallel 0.66 mΩ, mean 57.90, stdev 13.58 mΩ (23.4 %)]
	BL~7763384910	80P	capa[sum 99796 mAh, mean 1247.45 stdev 381.71 (30.6 %)]	IR[parallel 0.69 mΩ, mean 60.13, stdev 14.20 mΩ (23.6 %)]
	BL~8980484668	80P	capa[sum 100372 mAh, mean 1254.65 stdev 381.30 (30.4 %)]	IR[parallel 0.73 mΩ, mean 62.46, stdev 13.87 mΩ (22.2 %)]
	BL~9378155622	80P	capa[sum 97642 mAh, mean 1220.52 stdev 355.08 (29.1 %)]	IR[parallel 0.72 mΩ, mean 62.83, stdev 14.85 mΩ (23.6 %)]
2021-11-12 21:58.57 [info     ] string layout                  P=[80, 80, 80, 80, 80, 80, 80, 80, 80, 80] S=10 block_capacity_mean=98.81 Ah block_ir_mean=0.70 mΩ cells=800 energy_capacity=3.6 kWh interblock_capacity_stdev=1.43 % interblock_ir_stdev=2.87 % intrablock_ir_stdev_max=23.65 %

======================================

10S180P string

➜  ~ pack.py assemble --path /PREPROD/ --match '.state.self_discharge.assessment == "PASS" and .state.internal_resistance != null and .state.internal_resistance.v < 90' -a -S 10 -P 180
2024-05-14 11:18:27 [info     ] loading plugins                namespace=<module 'secondlife.plugins' from '/home/enki/repos/github.com/enkiusz/greatriver/lib/python/secondlife/plugins/__init__.py'>
2024-05-14 11:18:28 [info     ] searching for cells
2024-05-14 11:18:29 [info     ] cached all logs                count=4045
2024-05-14 11:18:29 [info     ] cached all extras              count=111
2024-05-14 11:18:30 [info     ] cached all container IDs       count=3912
2024-05-14 11:18:30 [warning  ] cannot determine bucket        id=JUNK
2024-05-14 11:18:30 [warning  ] cannot determine bucket        id=STOCK
2024-05-14 11:18:30 [warning  ] cannot determine bucket        id=PROD
2024-05-14 11:18:30 [warning  ] cannot determine bucket        id=9G4373J7+9R_Zyzna13
2024-05-14 11:18:30 [warning  ] cannot determine bucket        id=ACQUIRED
2024-05-14 11:18:30 [warning  ] cannot determine bucket        id=LOST
2024-05-14 11:18:30 [warning  ] cannot determine bucket        id=PREPROD
2024-05-14 11:18:30 [warning  ] cannot determine bucket        id=TESTBED
2024-05-14 11:18:30 [info     ] progress                       cells_found_total=1000
2024-05-14 11:18:31 [info     ] progress                       cells_found_total=2000
2024-05-14 11:18:32 [info     ] progress                       cells_found_total=3000
2024-05-14 11:18:32 [warning  ] cannot determine bucket        id=UNPACKED
2024-05-14 11:18:32 [info     ] progress                       cells_found_total=4000
2024-05-14 11:18:32 [info     ] cell pool                      count=2847
2024-05-14 11:18:32 [info     ] selecting cells                P=180 S=10 pool_size=2847
2024-05-14 11:18:35 [info     ] progress                       iterations=3
2024-05-14 11:18:38 [info     ] progress                       iterations=7
2024-05-14 11:18:39 [info     ] improved string found          iterations=9
2024-05-14 11:18:39 [info     ] string layout                  P=[180, 180, 180, 180, 180, 180, 180, 180, 180, 180] S=10 block_capacity_mean=343.59 Ah block_ir_mean=0.23 mΩ cells=1800 energy_capacity=12.4 kWh interblock_capacity_stdev=0.17 % interblock_ir_stdev=3.72 % intrablock_ir_stdev_max=37.89 %

final string configuration:

2024-05-14 11:32:31 [info     ] optimization finished
STR~0061623211  10S     capa[sum  3405 Ah, mean 340.48, stdev 3727.93705 mAh (1.09 %)]  IR[max 0.24 mΩ, mean 0.24, stdev 0.00493 (2.09 %)]
        BL~8832075584   180P    capa[sum 344045 mAh, mean 1911.36 stdev 378.60 (19.8 %)]        IR[parallel 0.23 mΩ, mean 48.90, stdev 17.23 mΩ (35.2 %)]
        BL~0488338132   180P    capa[sum 337309 mAh, mean 1873.94 stdev 409.95 (21.9 %)]        IR[parallel 0.24 mΩ, mean 50.54, stdev 17.94 mΩ (35.5 %)]
        BL~0527997270   180P    capa[sum 341735 mAh, mean 1898.53 stdev 378.14 (19.9 %)]        IR[parallel 0.24 mΩ, mean 49.89, stdev 17.68 mΩ (35.4 %)]
        BL~5508176447   180P    capa[sum 339844 mAh, mean 1888.02 stdev 431.32 (22.8 %)]        IR[parallel 0.24 mΩ, mean 50.52, stdev 17.92 mΩ (35.5 %)]
        BL~7498525845   180P    capa[sum 340867 mAh, mean 1893.71 stdev 398.38 (21.0 %)]        IR[parallel 0.24 mΩ, mean 50.57, stdev 17.95 mΩ (35.5 %)]
        BL~3490386883   180P    capa[sum 332450 mAh, mean 1846.95 stdev 408.84 (22.1 %)]        IR[parallel 0.23 mΩ, mean 50.67, stdev 17.87 mΩ (35.3 %)]
        BL~5947720009   180P    capa[sum 345244 mAh, mean 1918.02 stdev 376.91 (19.7 %)]        IR[parallel 0.24 mΩ, mean 51.10, stdev 17.22 mΩ (33.7 %)]
        BL~7836852014   180P    capa[sum 343088 mAh, mean 1906.04 stdev 369.61 (19.4 %)]        IR[parallel 0.23 mΩ, mean 48.03, stdev 17.03 mΩ (35.5 %)]
        BL~3341212477   180P    capa[sum 338400 mAh, mean 1880.00 stdev 399.69 (21.3 %)]        IR[parallel 0.24 mΩ, mean 50.07, stdev 17.56 mΩ (35.1 %)]
        BL~1915135987   180P    capa[sum 341852 mAh, mean 1899.18 stdev 371.33 (19.6 %)]        IR[parallel 0.23 mΩ, mean 48.82, stdev 17.08 mΩ (35.0 %)]
2024-05-14 11:32:31 [info     ] string layout                  P=[180, 180, 180, 180, 180, 180, 180, 180, 180, 180] S=10 block_capacity_mean=340.48 Ah block_ir_mean=0.24 mΩ cells=1800 energy_capacity=12.3 kWh interblock_capacity_stdev=1.09 % interblock_ir_stdev=2.09 % intrablock_ir_stdev_max=35.50 %
2024-05-14 11:32:31 [info     ] assembling string              path=/PREPROD/

Sorting sells:

greatriver/bin/sort.py \
--bucket-path 0 /PREPROD/STR~0061623211/BL~8832075584/ \
--bucket-path 1 /PREPROD/STR~0061623211/BL~0488338132/ \
--bucket-path 2 /PREPROD/STR~0061623211/BL~0527997270/ \
--bucket-path 3 /PREPROD/STR~0061623211/BL~5508176447/ \
--bucket-path 4 /PREPROD/STR~0061623211/BL~7498525845/ \
--bucket-path 5 /PREPROD/STR~0061623211/BL~3490386883/ \
--bucket-path 6 /PREPROD/STR~0061623211/BL~5947720009/ \
--bucket-path 7 /PREPROD/STR~0061623211/BL~7836852014/ \
--bucket-path 8 /PREPROD/STR~0061623211/BL~3341212477/ \
--bucket-path 9 /PREPROD/STR~0061623211/BL~1915135987/ -

Command used to replace missing cells:

pack.py replace --match '.path == "/STOCK/RACK~0768983590/" and .state.internal_resistance.v < 90 and .state.self_discharge.assessment == "PASS"' -


As there were many cells lost the decision has been made to reduce the size to 10S140P. Didnt bother to move the missing cells to /LOST/ as there were too many of them
(approx 400).


## List 

================================

Packing list for a string

First 10S80P string

➜  docs git:(master) ✗ info.py -a --match '.path | startswith("/PREPROD/STR~6404665298/")' -R infoset \
	--infoset-query '.path + .id' --infoset-query '.state.bucket' \
	--sort-query '.path + .state.bucket'
2023-03-12 18:20.47 [info     ] loading plugins                namespace=<module 'secondlife.plugins' from '/home/enki/repos/github.com/enkiusz/greatriver/lib/python/secondlife/plugins/__init__.py'>
2023-03-12 18:20.48 [info     ] searching for cells
2023-03-12 18:20.50 [info     ] cached all logs                count=3992
2023-03-12 18:20.53 [info     ] cached all extras              count=111
2023-03-12 18:20.54 [info     ] cached all container IDs       count=3859
2023-03-12 18:20.54 [info     ] progress                       cells_found_total=1
2023-03-12 18:20.55 [info     ] progress                       cells_found_total=1000
2023-03-12 18:20.55 [error    ] exception                      _exc_info=KeyError('ts')
2023-03-12 18:20.55 [error    ] exception                      _exc_info=KeyError('ts')
2023-03-12 18:20.55 [info     ] progress                       cells_found_total=2000
2023-03-12 18:20.56 [warning  ] cannot determine bucket        id=TESTBED
2023-03-12 18:20.56 [warning  ] cannot determine bucket        id=PREPROD
2023-03-12 18:20.56 [warning  ] cannot determine bucket        id=JUNK
2023-03-12 18:20.56 [warning  ] cannot determine bucket        id=STOCK
2023-03-12 18:20.56 [info     ] progress                       cells_found_total=3000
2023-03-12 18:20.57 [warning  ] cannot determine bucket        id=DEPACKED
|           .id |                                        .path + .id | .state.bucket |
| BL~0383457779 |              /PREPROD/STR~6404665298/BL~0383457779 |           03P |
| BL~0485767676 |              /PREPROD/STR~6404665298/BL~0485767676 |           04P |
| BL~1040067677 |              /PREPROD/STR~6404665298/BL~1040067677 |           10P |
| BL~2306594136 |              /PREPROD/STR~6404665298/BL~2306594136 |           23P |
| BL~2587102746 |              /PREPROD/STR~6404665298/BL~2587102746 |           25P |
| BL~3425691774 |              /PREPROD/STR~6404665298/BL~3425691774 |           34P |
| BL~5322205048 |              /PREPROD/STR~6404665298/BL~5322205048 |           53P |
| BL~6523649345 |              /PREPROD/STR~6404665298/BL~6523649345 |           65P |
| BL~9004878134 |              /PREPROD/STR~6404665298/BL~9004878134 |           90P |
| BL~9945209595 |              /PREPROD/STR~6404665298/BL~9945209595 |           99P |
|  C~0012168377 | /PREPROD/STR~6404665298/BL~0383457779/C~0012168377 |           00N |

UPS 4S24P

➜  docs git:(master) ✗ info.py -a --match '.props.formfactor == "18650" and (.path | startswith("/PREPROD/STR~7436719193/"))' -R infoset \
        --infoset-query '.path + .id' --infoset-query '.state.bucket' \
        --sort-query '.path + .state.bucket'
2023-03-14 15:42.20 [info     ] loading plugins                namespace=<module 'secondlife.plugins' from '/home/enki/repos/github.com/enkiusz/greatriver/lib/python/secondlife/plugins/__init__.py'>
2023-03-14 15:42.21 [info     ] searching for cells
2023-03-14 15:42.22 [info     ] cached all logs                count=3992
2023-03-14 15:42.25 [info     ] cached all extras              count=111
2023-03-14 15:42.25 [info     ] cached all container IDs       count=3859
2023-03-14 15:42.26 [info     ] progress                       cells_found_total=1
2023-03-14 15:42.26 [info     ] progress                       cells_found_total=1000
2023-03-14 15:42.26 [error    ] exception                      _exc_info=KeyError('ts')
2023-03-14 15:42.27 [error    ] exception                      _exc_info=KeyError('ts')
2023-03-14 15:42.27 [info     ] progress                       cells_found_total=2000
2023-03-14 15:42.27 [warning  ] cannot determine bucket        id=TESTBED
2023-03-14 15:42.27 [warning  ] cannot determine bucket        id=PREPROD
2023-03-14 15:42.27 [warning  ] cannot determine bucket        id=JUNK
2023-03-14 15:42.27 [warning  ] cannot determine bucket        id=STOCK
2023-03-14 15:42.28 [info     ] progress                       cells_found_total=3000
2023-03-14 15:42.28 [warning  ] cannot determine bucket        id=DEPACKED
|          .id |                                        .path + .id | .state.bucket |
| C~0968733553 | /PREPROD/STR~7436719193/BL~1022488536/C~0968733553 |           09P |
| C~1933991996 | /PREPROD/STR~7436719193/BL~1022488536/C~1933991996 |           19N |
| C~2057466134 | /PREPROD/STR~7436719193/BL~1022488536/C~2057466134 |           20N |
| C~2338068178 | /PREPROD/STR~7436719193/BL~1022488536/C~2338068178 |           23N |
[...]



============================

Count bucket totals (useful for tracking progress on the sorter)

➜  ~ info.py -a --match '.path | startswith("/PREPROD/STR~7436719193/")' -R groups --key-query '.state.bucket'
2023-03-14 13:23.21 [info     ] loading plugins                namespace=<module 'secondlife.plugins' from '/home/enki/repos/github.com/enkiusz/greatriver/lib/python/secondlife/plugins/__init__.py'>
2023-03-14 13:23.22 [info     ] searching for cells
2023-03-14 13:23.23 [info     ] cached all logs                count=3992
2023-03-14 13:23.26 [info     ] cached all extras              count=111
2023-03-14 13:23.26 [info     ] cached all container IDs       count=3859
2023-03-14 13:23.26 [info     ] progress                       cells_found_total=1
2023-03-14 13:23.27 [info     ] progress                       cells_found_total=1000
2023-03-14 13:23.27 [error    ] exception                      _exc_info=KeyError('ts')
2023-03-14 13:23.27 [error    ] exception                      _exc_info=KeyError('ts')
2023-03-14 13:23.28 [info     ] progress                       cells_found_total=2000
2023-03-14 13:23.28 [warning  ] cannot determine bucket        id=TESTBED
2023-03-14 13:23.28 [warning  ] cannot determine bucket        id=PREPROD
2023-03-14 13:23.28 [warning  ] cannot determine bucket        id=JUNK
2023-03-14 13:23.28 [warning  ] cannot determine bucket        id=STOCK
2023-03-14 13:23.28 [info     ] progress                       cells_found_total=3000
2023-03-14 13:23.29 [warning  ] cannot determine bucket        id=DEPACKED
| .state.bucket | Count |
|         "00N" |     1 |
|         "01N" |     2 |
|         "02N" |     1 |
|         "02P" |     2 |
|         "05P" |     2 |
|         "06N" |     2 |
|         "07N" |     1 |
|         "09N" |     1 |
|         "09P" |     1 |
|         "10P" |     1 |
|         "13N" |     1 |
|         "14P" |     1 |
|         "17N" |     1 |
|         "17P" |     1 |
|         "18N" |     1 |
|         "18P" |     1 |

===================================

Print labels

➜  ~ labels.py --copies 2 BL~1022488536 BL~3002812862 BL~4005524831 BL~8894048519

===================================

Sorting the cells into buckets (blocks)

python3 bin/sort.py \
--bucket-path 0 /PREPROD/STR~7436719193/BL~1022488536/ \
--bucket-path 3 /PREPROD/STR~7436719193/BL~3002812862/ \
--bucket-path 4 /PREPROD/STR~7436719193/BL~4005524831/ \
--bucket-path 9 /PREPROD/STR~7436719193/BL~8894048519/ \
--loglevel DEBUG -


# Typical workflows

Workflow overview:




                            JUNK ◄──┐
                             ▲      │               TESTBED
                             │      │                ▲    ▲
                             │      │                │    │
                             │      │                │    │
                             │      │                │    │
                             │ ┌────┼────────────────┘    │
                             │ │    │                     │
                             │ │    └──────────────────┐  │
                             │ │                       │  │
                             │ │                       │  │
 ACQUIRED   ────────────►   UNPACKED ───────────────► STOCK ──────────► PREPROD
    ▲                          ▲                                         │
    │                          │                                         │
    │                          │                                         │
    │                          │                                         │
    │                          │                                         │
    │                          │                                         │
    │                          │                                         ▼
    │                          │                                       PROD
    │                          │
Complete packs           Purchased unpacked
                         (batches)
PACK~nnnnn
                         BATCH~nnnnnnn

## Acquiring a new pack for disassembly (unpacking)

First generate a new identifier for the pack

➜  ~ labels.py -g 1 --prefix PACK --printer-pretend
deprecation warning: brother_ql.devicedependent is deprecated and will be removed in a future release
2023-08-05 15:36.13 [debug    ] config                         args=Namespace(g=1, copies=1, prefix='PACK', digits=10, printer_model='QL-500', printer_id=None, printer_backend='linux_kernel', printer_label='17x54', printer_pretend=True, identifiers=['-'])
2023-08-05 15:36.13 [info     ] saving bitmap                  file=labels_0.png
PACK~8762131947

Export the pack id into an environment variable to ease workflow:

➜  ~ export PACK_ID='PACK~8762131947'

Next, create the pack with any relevant properties that you can find on the pack itself:
- brand and model
- serial number
- datecode
- voltage
- capacity

➜  ~ log.py --autocreate --path /ACQUIRED -p serial '2JCGJ18IEB2582' -b Mi -m NE1003-H -p layout 10S3P -p voltage.nom 36 -p capacity.nom 7800 $PACK_ID

Photos can be also added for reference if needed.

Next, disassemble (unpack) the battery pack and throw away the corroded or otherwise unsuable cells. Log the number of junked cells as a property of the pack:

➜  ~ log.py -p junk_cells 1 $PACK_ID

Generate and print labels for all cells which are ok for further processing:

➜  ~ labels.py -g 30
deprecation warning: brother_ql.devicedependent is deprecated and will be removed in a future release
2023-08-05 17:37.54 [debug    ] config                         args=Namespace(g=30, copies=1, prefix='C', digits=10, printer_model='QL-500', printer_id=None, printer_backend='linux_kernel', printer_label='17x54', printer_pretend=False, identifiers=['-'])
2023-08-05 17:37.54 [info     ] autoselected printer           printer=file:///dev/usb/lp0
[...]
'printing completed' status not received.
'waiting to receive' status not received.
Printing potentially not successful?
C~0995766318
C~0596796888
[...]
➜  ~ 

Perform an initial check of the voltage and internal resistance of the cells and add them as child cells of your pack. Enter as much common data as possible for the cells
including formfactor and nominal capacity. The '%s' magic value can be used to input a different property value for each cell. This is useful for filling out serial
numbers.

➜  ~ log.py --autocreate -b EVE -m ICR18650/26V -c 2550 -p formfactor 18650 -p serial %s -M rc --path "/ACQUIRED/$PACK_ID/" -
➜  ~ log.py --autocreate -b EVE -m ICR18650/26V -c 2550 -p formfactor 18650 -p serial '%s' -M rc --path "/ACQUIRED/$PACK_ID/" -
2023-08-05 18:01.48 [info     ] loading plugins                namespace=<module 'secondlife.plugins' from '/home/enki/repos/github.com/enkiusz/greatriver/lib/python/secondlife/plugins/__init__.py'>
C~6492223235
2023-08-05 18:01.52 [info     ] fetching infoset               id=C~6492223235
2023-08-05 18:01.52 [info     ] fetching infoset               id=ACQUIRED
2023-08-05 18:01.52 [info     ] fetching infoset               id=PACK~8762131947
2023-08-05 18:01.52 [info     ] cell found                     id=C~6492223235
2023-08-05 18:01.52 [info     ] progress                       cells_found_total=1
[C~6492223235] .props.serial = 5HG421k379923
2023-08-05 18:01.56 [info     ] measurement start              codeword=rc id=C~6492223235
2023-08-05 18:01.56 [info     ] measurement results            results={'IR': {'range': 'AUTO', 'v': 19.0261, 'u': 'mOhm'}, 'OCV': {'range': 'AUTO', 'u': 'V', 'v': 1.1732}}
2023-08-05 18:01.56 [info     ] store measurement results      codeword=rc id=C~6492223235 results={'type': 'measurement', 'event': 'finished', 'ts': 1691251316.7318642, 'equipment': {'model': 'RC3563'}, 'results': {'IR': {'range': 'AUTO', 'v': 19.0261, 'u': 'mOhm'}, 'OCV': {'range': 'AUTO', 'u': 'V', 'v': 1.1732}}}
[...]
2023-08-05 18:10.32 [info     ] measurement start              codeword=rc id=C~5317527658
2023-08-05 18:10.32 [info     ] measurement results            results={'IR': {'range': 'AUTO', 'v': 20.1469, 'u': 'mOhm'}, 'OCV': {'range': 'AUTO', 'u': 'V', 'v': 1.1714}}
2023-08-05 18:10.32 [info     ] store measurement results      codeword=rc id=C~5317527658 results={'type': 'measurement', 'event': 'finished', 'ts': 1691251832.5796463, 'equipment': {'model': 'RC3563'}, 'results': {'IR': {'range': 'AUTO', 'v': 20.1469, 'u': 'mOhm'}, 'OCV': {'range': 'AUTO', 'u': 'V', 'v': 1.1714}}}
2023-08-05 18:10.39 [info     ] progress                       cells_found_total=29
➜  ~ 



