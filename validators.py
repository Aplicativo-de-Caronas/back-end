import numpy as np
import erros


class Validator:
    def __init__(self):
        pass

    @staticmethod
    def cpf(cpf):
        numbers = np.array([int(x) for x in cpf[0:9]])
        multiplier = range(10, 1, -1)
        soma = sum(multiplier * numbers)
        if soma % 11 < 2:
            firstDigit = 0
        else:
            firstDigit = 11 - (soma % 11)
        numbers = np.append(numbers, firstDigit)
        multiplier = range(11, 1, -1)
        soma = sum(multiplier * numbers)
        if soma % 11 < 2:
            secondDigit = 0
        else:
            secondDigit = 11 - (soma % 11)
        numbers = np.append(numbers, secondDigit)
        newCpf = ''.join([str(f) for f in numbers])
        if cpf == newCpf:
            return True
        else:
            raise erros.InvalidCpf
