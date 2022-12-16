import random
from math import ceil
from zhutils.math import fexp

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


char_to_color = {
    'Temp': 'red',
    'Prec': 'blue',
    'VPD': 'green',
    'SD': 'orange',
    'RH': 'lightblue'
}


def random_hex_color():
    return '#'+''.join(random.sample('0123456789ABCDEF',6))


def combine_hex_colors(colors_to_weights):
    d_items = sorted(colors_to_weights.items())
    tot_weight = sum(colors_to_weights.values())
    red = int(sum([int(k[1:3], 16)*v for k, v in d_items])/tot_weight)
    green = int(sum([int(k[3:5], 16)*v for k, v in d_items])/tot_weight)
    blue = int(sum([int(k[5:7], 16)*v for k, v in d_items])/tot_weight)
    zpad = lambda x: x if len(x)==2 else '0' + x

    res = zpad(hex(red)[2:]) + zpad(hex(green)[2:]) + zpad(hex(blue)[2:])
    return f'#{res}'


def interpotate_between_colors(colors: list, points: int):
    points_for_color = ceil(points /  (len(colors)-1))
    result = []
    color_number = 0
    color_weight = 0
    for _ in range(points):
        color_weight += 1

        color_proportion = color_weight*(1.0/points_for_color)
        color = combine_hex_colors({
            colors[color_number]: 1.0 - color_proportion,
            colors[color_number+1]: color_proportion
        })
        result.append(color)
        if color_proportion >= 1:
            color_weight = 0
            color_number += 1 

    return result


def print_p_exponent(p: float) -> str:
    p_exp = fexp(p)
    return f'p<10^{{{p_exp+1}}}'


def print_p_classic(p: float) -> str:
    if p < 0.001:
        return 'p<0.001'
    elif p < 0.01:
        return 'p<0.01'
    elif p < 0.05:
        return 'p<0.05'
    else:
        return f'{p:.2f}'
