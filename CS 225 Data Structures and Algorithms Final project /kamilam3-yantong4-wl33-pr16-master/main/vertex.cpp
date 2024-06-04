#include "vertex.h"

using namespace waikiki;

Vertex::Vertex() {
    // airports.dat
    airportID = NO_EDGE;
    longitude = 0.0;
    latitude = 0.0;
}

Vertex::Vertex(int id, double lat, double lng) {
    // airports
    airportID = id;
    latitude = lat;
    longitude = lng;
}

void Vertex::set_airportID(int id) {
    airportID = id;
}
int Vertex::get_airportID() {
    return airportID;
}

void Vertex::set_longitude(double lng) {
    longitude = lng;
}
double Vertex::get_longitutde() {
    return longitude;
}

void Vertex::set_latitude(double lat) {
    latitude = lat;
}
double Vertex::get_latitude() {
    return latitude;
}
