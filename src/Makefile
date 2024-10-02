

SWIG := swig

CXXFLAGS :=  -fPIC -std=c++11 -I. $(shell pkg-config --cflags speexdsp) $(shell python3-config --cflags)
LDFLAGS := -shared -L/usr/lib/x86_64-linux-gnu -lspeexdsp $(shell python3-config --ldflags)
CXX := g++

all: _speexdsp.so

speexdsp_wrap.cpp: speexdsp.i
	$(SWIG) -I. -c++ -python -o $@ $^

_speexdsp.so: speexdsp_wrap.o echo_canceller.o
	$(CXX) $(CXXFLAGS) speexdsp_wrap.o echo_canceller.o $(LDFLAGS) -o $@

clean:
	-rm -f speexdsp_wrap.cpp *.o _speexdsp.so speexdsp.py *.pyc
