#pragma once

#include "utility.h"

using namespace waikiki;
    
/**
* The Vertex class initializes the parameters that are parsed in the Graph class.
**/
class Vertex {
    public:
        // constructors
        Vertex();
        Vertex(int id, double lat, double lng);

        // airports
        void set_airportID(int id);
        int get_airportID();
        void set_longitude(double lng);
        double get_longitutde();
        void set_latitude(double lat);
        double get_latitude();

    private:
        // airports
        int airportID;
        double longitude;
        double latitude;
};
