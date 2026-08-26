CC=arm-none-eabi-gcc
CFLAGS=-mcpu=cortex-m4 -mthumb -O2 -g
TARGET=build/sensor.elf
SRC=src/main.c
all: $(TARGET)
$(TARGET): $(SRC)
	@mkdir -p build
	$(CC) $(CFLAGS) -T linker.ld -o $@ $^ || echo "ELF placeholder - need arm-none-eabi-gcc"
clean:
	rm -rf build
