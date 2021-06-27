#
# Current settings from the manual: https://www.kupifonar.kz/upload/manuals/liitokala/liito-kala-lii-500-en.pdf
#
# When  you  choose  the  charging  current (300mah,500mah),  the  system  recognizes  the  discharging current is the 250mah automatically.
# When you  choose  the  charging  current (700mah,1000mah),  the  system  recognize  the  discharging current is the 500mah automatically.
#

lii500_current_setups = {
    '300 mA':  dict(current_setting='300 mA',  charge_current='300 mA',  discharge_current='250 mA'),
    '500 mA':  dict(current_setting='500 mA',  charge_current='500 mA',  discharge_current='250 mA'),
    '700 mA':  dict(current_setting='700 mA',  charge_current='700 mA',  discharge_current='500 mA'),
    '1000 mA': dict(current_setting='1000 mA', charge_current='1000 mA', discharge_current='500 mA'),
}
