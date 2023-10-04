class Decoder:
    def __init__(self, 
                 n_symbols, 
                 pulse_wdith, 
                 pulse_interval, 
                 n_fft,
                 n_step,
                 shannon_frequency):
        self.global_timer = 0
        self.local_timer = 0
        self.count_symbol = 0
        self.n_symbols = n_symbols
        self.n_step = n_step
        self.max_global_timer = int((n_symbols + 1) * pulse_interval * shannon_frequency)
        self.max_local_timer = int(pulse_interval * shannon_frequency)
        self.max_temp = int(pulse_interval * shannon_frequency) - n_fft
     
    def step(self, symbol):
        flag_end = False
        message = []
        
        self.global_timer += self.n_step
        
        # if the temporisation has ended
        if self.global_timer >= self.max_temp:

            
            # if the iteration on a symbol is ending
            if self.local_timer >= self.max_local_timer:
                # equivalent to the majority of positive sign vs negative sign
                message.append(self.count_symbol > 0)
                self.count_symbol = 0
                self.local_timer = 0
            
            
            self.local_timer += self.n_step
            self.count_symbol += symbol
         
        if self.global_timer >= self.max_global_timer:
            flag_end = True
            
        return flag_end, message
        