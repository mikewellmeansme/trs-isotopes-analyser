import random

month_names = ['September', 'October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August']
m_names = ['S', 'O', 'N', 'D', 'J', 'F', 'M', 'A', 'M ', 'J', 'J', 'A']

ind_titels = {
    '2H': '$δH$',
    '13C': '$δ^{13}C$',
    '18O': '$δ^{18}O$'
}

char_2_characteristic = {
    'Temp': 'Temperature',
    'Prec': 'Precipitation',
    'VPD': 'Vapor-Pressure Deficit',
    'RH': 'Relative Humidity',
    'SD': 'Sunshine Duration'
}

def random_hex_color():
    return '#'+''.join(random.sample('0123456789ABCDEF',6))

def combine_hex_colors(d):
    d_items = sorted(d.items())
    tot_weight = sum(d.values())
    red = int(sum([int(k[:2], 16)*v for k, v in d_items])/tot_weight)
    green = int(sum([int(k[2:4], 16)*v for k, v in d_items])/tot_weight)
    blue = int(sum([int(k[4:6], 16)*v for k, v in d_items])/tot_weight)
    zpad = lambda x: x if len(x)==2 else '0' + x

    res = zpad(hex(red)[2:]) + zpad(hex(green)[2:]) + zpad(hex(blue)[2:])
    return f'#{res}'
