import time
import matplotlib.pyplot as plt
import numpy


def gaussian(x, delay, sigma):
    '''
    Функция, график которой будет отображаться процессе анимации
    '''
    return numpy.exp(-((x - delay) / sigma) ** 2)


if __name__ == '__main__':

    # !!! Включить интерактивный режим для анимации
    plt.ion()

    # У функции gaussian будет меняться параметр delay (задержка)
    while True:
        
        # !!! Очистить текущую фигуру
        plt.clf()

        # Отобразить график
        plt.plot(1, 1)

        # !!! Следующие два вызова требуются для обновления графика
        plt.draw()
        plt.gcf().canvas.flush_events()

        # Задержка перед следующим обновлением
        time.sleep(0.02)