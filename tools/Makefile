# kangaroo_pd -- plain-C++ distinguished-point kangaroo port
#
# Links the stock Kangaroo v2.2 SECPK1 primitives. No CUDA, no OpenCL; builds and
# runs on Termux/ARM.
#
# The library lives outside this repo by default; override with:
#   make KANGAROO_DIR=/path/to/Kangaroo
KANGAROO_DIR ?= $(HOME)/Kangaroo

CXX      ?= clang++
CXXFLAGS ?= -O2 -std=c++17 -Wall -I$(KANGAROO_DIR) -I$(KANGAROO_DIR)/SECPK1
LDLIBS   ?= -lpthread

SECPK1 = \
	$(KANGAROO_DIR)/SECPK1/SECP256K1.cpp \
	$(KANGAROO_DIR)/SECPK1/Int.cpp \
	$(KANGAROO_DIR)/SECPK1/IntMod.cpp \
	$(KANGAROO_DIR)/SECPK1/Point.cpp \
	$(KANGAROO_DIR)/SECPK1/Random.cpp \
	$(KANGAROO_DIR)/SECPK1/IntGroup.cpp \
	$(KANGAROO_DIR)/Timer.cpp

all: kangaroo_pd

kangaroo_pd: kangaroo_pd.cpp $(SECPK1)
	$(CXX) $(CXXFLAGS) -o $@ $< $(SECPK1) $(LDLIBS)

# Known-answer test. MUST pass before the binary is trusted for any search.
test: kangaroo_pd
	./kangaroo_pd -t

clean:
	rm -f kangaroo_pd

.PHONY: all test clean