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

