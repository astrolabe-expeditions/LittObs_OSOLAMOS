CC=g++

CFLAGS=-O0 -g3 -march=native -mtune=native -std=c++14

LDFLAGS=

EXEC=main

SRC=./deps/flag_tones_to_symbol.cpp   \
    ./deps/update_flag_wake_up.cpp \
    main.cpp


OBJ= $(SRC:.cpp=.o)

all: $(EXEC)

main: $(OBJ)
	$(CC) $(CFLAGS) -o ./$@ $^ $(LDFLAGS)

%.o: %.cpp
	$(CC) $(CFLAGS) -o $@ -c $<

.PHONY: clean mrproper

clean:
	find ./bin -name main -exec rm {} \;
	find ./src -name *.o  -exec rm {} \;

mrproper: clean
	rm $(EXEC)
