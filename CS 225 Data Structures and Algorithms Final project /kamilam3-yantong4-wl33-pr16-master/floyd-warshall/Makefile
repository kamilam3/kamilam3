EXENAME = main
OBJS = main.o  floyd.o utility.o 

CXX = clang++
CXXFLAGS = -std=c++0x -c -g -O0 -Wall
LD = clang++
LDFLAGS = -std=c++0x

all: $(EXENAME)

$(EXENAME): $(OBJS)
	$(LD) $^ $(LDFLAGS) -o $@

main.o: main.cpp
	$(CXX) $< $(CXXFLAGS)


utility.o : utility.cpp utility.h
	$(CXX) $(CXXFLAGS) utility.cpp


floyd.o : floyd.cpp floyd.h  utility.h utility.cpp
	$(CXX) $(CXXFLAGS) floyd.cpp



clean:
	-rm -f *.o $(EXENAME)
