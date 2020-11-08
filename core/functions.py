import discord

def eq_vel(luzes, percentage=False):
    '''
    Equação para obter a velocidade de farm do jogador,
    diminuindo consideravelmente o tempo de duração de
    cada farm.

    param boolean: percentage
        Se True: Retornar valor relativo em porcentagem % (Ex: 25.75%)
        Se True: Retornar valor absoluto (Ex: 0.2575)

    Equação atual: ((1.18523*(10**-7))*(luzes**3) + 0.0999)
    Equação teste: ((0.0000177976)*(luzes**2) + 0.0995551)
    Equação teste2: (((luzes**2)*0.00416) + 0.0833)
    '''
    if percentage:
        return round((((luzes**2)*0.00416) + 0.0833)*100, 2)
    else:
        return round((((luzes**2)*0.00416) + 0.0833), 4)