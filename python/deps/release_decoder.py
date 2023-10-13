""" Release decoder definition """


class ReleaseDecoder:
    """
        Release Decoder class
    """

    def __init__(self,
                 n_symbols,
                 pulse_interval,
                 n_fft,
                 n_step,
                 shannon_frequency):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the initial values of all variables and objects that are used in this class.


        :param self: Represent the instance of the class
        :param n_symbols: Determine the number of symbols in a frame
        :param pulse_interval: Set the maximum value of the local_timer variable
        :param n_fft: Determine the maximum value of local_timer
        :param n_step: Determine the number of samples per symbol
        :param shannon_frequency: Determine the number of samples per symbol
        :return: A class object

        """
        self.global_timer = 0
        self.local_timer = 0
        self.count_symbol = 0
        self.n_symbols = n_symbols
        self.n_step = n_step
        self.max_global_timer = int((n_symbols + 1) * pulse_interval * shannon_frequency)
        self.max_local_timer = int(pulse_interval * shannon_frequency)
        self.max_temp = int(pulse_interval * shannon_frequency) - n_fft

    def step(self, symbol):
        """
        The step function is the core of the algorithm. It takes in a symbol and returns two values:
            - flag_end: a boolean indicating whether or not to stop decoding
            - message: an array containing all messages decoded so far

        :param self: Represent the instance of the class
        :param symbol: Count the number of positive and negative symbols
        :return: A flag_end and a message

        """
        flag_end = False
        message = []

        self.global_timer += self.n_step

        # if the timer has ended
        if self.global_timer >= self.max_temp:

            # if the iteration on a symbol is ending
            if self.local_timer >= self.max_local_timer:
                # equivalent to the majority of positive sign vs negative sign
                if self.count_symbol != 0:
                    message.append(self.count_symbol > 0)
                self.count_symbol = 0
                self.local_timer = 0

            self.local_timer += self.n_step
            self.count_symbol += symbol

        if self.global_timer >= self.max_global_timer:
            flag_end = True

        return flag_end, message

    def reset(self):
        """
        The reset function is used to reset the global and local timers,
        as well as the count symbol.


        :param self: Represent the instance of the class
        :return: The global timer, local timer and the count symbol

        """
        self.global_timer = 0
        self.local_timer = 0
        self.count_symbol = 0
