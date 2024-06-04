EXENAME = main
OBJS = main.o vertex.o graph.o utility.o traversal.o


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


graph.o : graph.cpp graph.h  utility.h utility.cpp
	$(CXX) $(CXXFLAGS) graph.cpp



clean:
	-rm -f *.o $(EXENAME)